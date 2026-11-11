# PCIe 建模参数与公式速查

上级：[术语与检查清单](./README.md)

相关：[带宽、延迟、Credit、MPS 与 MRRS](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)、[PCIe Read Completion 延迟](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)、[SerDes：链路状态、失败与恢复](../../../SERDES/wiki/09-modeling/link-state-and-failure.md)

本页区分协议限制、实现参数和估算假设。建模时先定义方向、测量层次、链路模式、包长分布和时间单位；再用目标平台的配置和测量值校准。PCIe Base Specification 的相应版本是协议细节的最终依据。

## 链路速率和计数边界

下表为单向、每 lane 的上界，GB = 10⁹ B。Gen1–5 列已扣除编码开销，但没有扣 TLP、DLLP、replay 或空闲；链路宽度为 xN 时乘 N。

| Gen | 每 lane 速率 | 模式 | 上界 |
| --- | ---: | --- | ---: |
| 1 | 2.5 GT/s | 8b/10b | 0.250 GB/s |
| 2 | 5 GT/s | 8b/10b | 0.500 GB/s |
| 3 | 8 GT/s | 128b/130b | 0.985 GB/s |
| 4 | 16 GT/s | 128b/130b | 1.969 GB/s |
| 5 | 32 GT/s | 128b/130b | 3.938 GB/s |
| 6 | 64 GT/s | PAM4、Flit Mode | 原始 8.000 GB/s；TLP 区域最多 7.375 GB/s |

Gen5 x16 单向约 `3.938 × 16 = 63.0 GB/s`，在此之后才扣协议与工作负载开销。Gen6 不能沿用 128b/130b 模型，见下文。不要对任何已计入的开销再乘一次。

## Non-Flit Mode：按真实 TLP 大小估算

MPS 是有数据 TLP 的 payload 上限，并非每个包的实际 payload。某些请求无数据；地址、尾包、byte enable 和请求长度都会让有效数据小于上限。Header 可能是 3DW 或 4DW；可选字段、TLP 类型、framing、DLLP、链路模式和 replay 都影响实际占用。因此不存在适用于所有 TLP 和模式的固定 `24 B`。

仅作为可替换的一阶模型，假设使用 Non-Flit Mode、连续传输相同长度的有数据 TLP，每包实际传送的 payload `P` 全部是有效数据，且该模型计入的非 payload 占用 `O = 24 B`：

```text
payload 效率 = P / (P + O)
有效吞吐 = 已扣编码的链路带宽 × payload 效率
```

| 实际 payload P | 假设 O = 24 B 时的效率 |
| ---: | ---: |
| 128 B | 84.2% |
| 256 B | 91.4% |
| 512 B | 95.5% |

例如 MPS = 256 B 但每个包只有 64 B 实际有效数据，效率是 `64/(64+24) ≈ 72.7%`，不是 91.4%。此例不含额外 DLLP、重传、空闲或 byte enable 损失。`O` 只能作为已指定计数边界下的假设；若 O 已包含某项，就不能再在其他折扣里计算同一项。更准确的模型应根据每种包格式和链路模式统计实际字节，分别计算两个方向。

## Read 吞吐与 Tag

对稳定状态，使用平均在途 read 数 `N`、每请求平均有效数据 `S` 和平均往返完成时间 `RTT`：

```text
read 有效吞吐 ≤ min(响应方向有效带宽, N × S / RTT, 其他资源上限)
```

该近似需要对应同一负载和测量口径的平均值。`S` 受 MRRS、请求边界及实际访问限制，并不总等于 MRRS；RTT 包含排队和 completion 返回，可能随负载变化。要达到目标有效吞吐 `B`，至少需要 `ceil(B × RTT / S)` 个可同时在途的请求。

假设 Gen4 x8、目标为 `12.8 GB/s`、RTT `1 µs`、每请求 `512 B`，则需要 `ceil(12.8e9 × 1e-6 / 512) = 25` 个请求。Gen4 x8 的编码后上界约为 `15.75 GB/s`，目标还须低于扣除协议开销后的实际有效带宽；带宽时延积估算不保证实测达到 12.8 GB/s。

| Tag 条件 | 协议上界与实现约束 |
| --- | --- |
| 5-bit | 通常每 Function 最多 32 个待完成请求 |
| Extended Tag 已使能 | 可增加到 256；仍受实现和资源限制 |
| 10-bit Tag 已使能 | 针对单个支持该能力的 completer，可增加至最多 768；这是上限，不是所有设备的实际可用数 |

Requester 的能力和使能、目标 completer 的能力、Tag 分配、完成缓冲及 IP 具体槽数都要检查。10-bit 字段有 1024 种位模式，不代表针对单一 completer 有 1024 个可用并发槽，也不能把 768 当成所有目标或设备的总并发常数。混用不同能力的目标时还需遵守 Tag 唯一性和别名限制。例如 [AMD CPM5 文档](https://docs.amd.com/r/en-US/pg346-cpm-pcie/Tag-Management-for-Non-Posted-Transactions)说明其实现的表容量最多 768；这不是对其他 IP 的保证。

## Completion 的边界、大小与分包

MRRS 限制一个 Memory Read Request 的请求大小；MPS 限制带数据 TLP 的 payload 大小。RCB 是允许拆分的位置边界，不是 CplD 的最大长度，也不表示一定在每个 RCB 都拆包。首包起点及末包终点可以是原请求的起止地址；其余拆分位置必须满足适用 RCB 对齐规则。

例如请求地址与 `256 B` 对齐，长度 256 B，`MRRS ≥ 256 B`、`MPS = 256 B`、RCB 为 64 B，且其他条件许可：completer 可返回一个 256 B CplD，也可返回四个 64 B CplD。也可能有符合边界和 MPS 规则的其他组合。实际包数取决于 completer 策略、地址和可用数据，不能只用 `ceil(request_size / RCB)` 断言。

建模可把真实分包策略作为参数；若要预留接收缓冲，要考虑合法的最坏分包，而非只用最少包数。[AMD PG213 RCB 说明](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Read-Completion-Boundary)与 [Intel R-Tile 示例](https://www.intel.com/content/www/us/en/docs/programmable/683501/25-1/completion-buffer-size-72675.html)给出可选拆分和缓冲例子。

## Credit 与接收缓冲

传统 Non-Flit 流控按 Posted、Non-Posted、Completion 分类，区分 header 和 data credit；传统 data credit 以 16 B 为单位。实际值可为有限或协议规定的无限，不能假设每一种 credit 都会耗尽。[AMD PG213](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Managing-Receive-Buffer-Space-for-Inbound-Completions)说明 Endpoint 接收 completion 的特殊情况：其通告的 Completion credit 为无限时，requester 仍须为可能返回的 completion 预留实际缓冲。模型需分别表示协议 credit、物理缓冲和返回更新时刻；检查具体模式的规则。

## Gen6 Flit Mode

在 64 GT/s PAM4 下，每个 symbol 承载 2 bit，符号率为 32 GBd；64 GT/s 已是单向每 lane 的原始传输位速率表示；原始单向速率为 `64e9 / 8 = 8 GB/s`，不要因 PAM4 再乘 2。[PCI-SIG](https://pcisig.com/blog/evolution-pci-express-specification-its-sixth-generation-third-decade-and-still-going-strong)说明每个 256 B Flit 含 236 B TLP 区域、6 B DLP、8 B CRC、6 B FEC。因此连续填满时：

```text
8 × 236 / 256 = 7.375 GB/s/lane  （TLP 区域上限）
```

236 B 区域包括 TLP header 和数据，也可能有 NOP；7.375 GB/s 不是纯有效 payload 吞吐。一个 TLP 可以跨 Flit，一个 Flit 也可以容纳多个 TLP。还要扣除 TLP 头、填充、空闲和重传等实际占用。Flit Mode 不再为每个 TLP 重复计算旧模式的 framing 和独立 LCRC；不能把 Non-Flit 的 24 B 示例再套到这里。Flit Mode 也可在其他链路速率下使用，模型应以实际协商模式而非仅以代际选择。

## 校准与扫描

记录 Gen、lane、模式、各方向流量、实际 TLP 大小、MPS、MRRS、RCB、目标、Tag/缓冲槽数、credit、RTT 分布及 replay。用实际控制器配置、计数器与流量测试校准；分别扫描负载、延迟、分包和并发，避免把上界当成测得吞吐。
