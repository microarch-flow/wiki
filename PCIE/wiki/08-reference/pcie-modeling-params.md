# PCIe 建模参数与公式速查

上级：[08 术语与检查清单](./README.md)

相关：[带宽、延迟、Credit、MPS 与 MRRS](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)、[PCIe Read Completion 延迟为什么敏感](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)

## 这页在回答什么问题

如果你要给架构探索工具建 PCIe 模型，需要哪些**可量化的参数、公式和默认值**，以及应该扫描哪些维度。

这页和本 wiki 其余页面定位不同：其余页面建立**判断力**，这页提供**可以直接写进代码的数字**。所有数值用于建模量级估算，精确到位的取值请以 PCIe Base Spec 对应版本为准。

## 1. 链路名义带宽

单向、每 lane 的有效字节带宽（已扣编码开销，未扣 TLP/DLLP 开销）：

| Gen | GT/s | 编码方式 | 编码效率 | 每 lane 有效带宽 |
| --- | --- | --- | --- | --- |
| 1 | 2.5 | 8b/10b | 80% | 250 MB/s |
| 2 | 5.0 | 8b/10b | 80% | 500 MB/s |
| 3 | 8.0 | 128b/130b | ~98.5% | ~985 MB/s |
| 4 | 16 | 128b/130b | ~98.5% | ~1.97 GB/s |
| 5 | 32 | 128b/130b | ~98.5% | ~3.94 GB/s |
| 6 | 64 | PAM4 + FLIT + FEC | 见第 6 节 | ~7.56 GB/s |

链路名义带宽 = `每 lane 带宽 × lane 数`，lane 数取 x1 / x2 / x4 / x8 / x16。

例：Gen5 x16 单向 ≈ `3.94 × 16 ≈ 63 GB/s`。

> 建模注意：这一列已经把物理层编码开销算进去了，**不要再乘一次 80% 或 98.5%**。TLP/DLLP 开销是在这之上的第二层折扣，见第 2 节。

## 2. TLP 开销与有效吞吐

每个 TLP 在链路上的固定开销（Gen3+ 128b/130b 框架，量级值）：

| 部分 | 字节 | 来源层 |
| --- | --- | --- |
| STP framing token | 4 | Physical |
| Sequence Number | 2 | Data Link |
| TLP Header (3DW / 4DW) | 12 / 16 | Transaction |
| ECRC（可选） | 0 或 4 | Transaction |
| LCRC | 4 | Data Link |
| 合计 | **约 22–26** | |

有效吞吐公式：

```
payload_efficiency = MPS / (MPS + overhead_per_TLP)
有效吞吐 = 链路名义带宽 × payload_efficiency
```

按 overhead ≈ 24 字节估算：

| MPS（字节） | payload_efficiency |
| --- | --- |
| 128 | ~84% |
| 256 | ~91% |
| 512 | ~95% |
| 1024 | ~98% |

这就是「MPS 影响包头开销占比」的量化含义：**MPS 越大，每包摊薄的固定开销越小**。但 MPS 受限于路径上所有设备的最小公共值（枚举时协商），常见实际值是 128 或 256。

> 还有一层带宽被 DLLP（ACK/NAK、FC update）和 replay 占用，约百分之几量级；做一阶模型可先并入一个固定 overhead 因子，做二阶模型再单独建。

## 3. read 吞吐：Little's Law 模型

read 是 non-posted，必须等 completion 返回，所以 read 吞吐由**并发深度 × 往返**决定，而不是链路带宽：

```
read 吞吐 ≈ (outstanding_requests × bytes_per_request) / RTT
```

只要这个值小于链路有效带宽，read 就「链路没满但吞吐上不去」。要灌满链路需要：

```
所需 outstanding ≥ 链路有效带宽 × RTT / bytes_per_request   （带宽时延积）
```

约束这三个量的参数：

- **outstanding_requests** —— 受 Tag 空间限制，见第 4 节。
- **bytes_per_request** —— 受 MRRS 钳制（单个 read request 最多请求 MRRS 字节）。
- **RTT** —— device 发起 → RC/switch → host memory → completion 返回 device 的往返，见第 5 节。

## 4. Tag 空间（并发上限）

| 模式 | 可用 Tag 数 |
| --- | --- |
| 默认（5-bit） | 32 |
| Extended Tag（8-bit） | 256 |
| 10-bit Tag | 768 / 1024 |

Tag 数是 read 并发深度的硬上限。建模时作为一个可配置参数，并和第 3 节联动：Tag 不够时，无论 MRRS 多大都灌不满高 Gen 宽链路。

## 5. 延迟参数（量级，需按平台标定）

| 路径段 | 典型量级 | 说明 |
| --- | --- | --- |
| Root Complex 到 host memory 往返 | 数百 ns | 命中时 |
| 每经过一级 switch | +百 ns 量级 | store-and-forward 比 cut-through 高 |
| IOMMU 翻译命中（IOTLB hit） | 可忽略 ~ 几十 ns | |
| IOMMU 翻译 miss（需 page walk） | 数百 ns ~ µs | 放大 read 延迟的主要来源 |
| host memory 拥塞 | 可变 | 与 RAM 子系统模型耦合 |

> 这些是量级占位值，**强烈建议在目标平台上用实测标定**后再写死进模型。链接 [RAM Wiki](../../../RAM/wiki/README.md) 做内存侧延迟建模。

## 6. Completion 拆分（RCB 与 MRRS）

一个 read request 返回的数据可能被拆成多个 completion TLP：

- **MRRS**（Max Read Request Size）：单个 read request 最多请求多少字节，合法值 128 / 256 / 512 / 1024 / 2048 / 4096。
- **RCB**（Read Completion Boundary）：completion 在 64 或 128 字节边界上拆分。

每个 completion 各带一份 header 开销，所以拆分数量直接影响 read 路径的有效效率：

```
completions_per_read ≈ ceil(request_size / completion_payload)
```

建模时把 RCB 和 completer 的实际返回粒度作为参数：拆得越碎，header 开销占比越高，completion 路径越容易成为瓶颈。

## 7. Credit / 流控模型

flow control 用 credit 做背压。建模背压时需要三类独立信用池：

| 类型 | Header credit | Data credit |
| --- | --- | --- |
| Posted（P） | PH | PD |
| Non-Posted（NP） | NPH | NPD |
| Completion（CPL） | CPLH | CPLD |

单位：

- 1 个 **header credit** = 1 个 TLP 头。
- 1 个 **data credit** = 16 字节（4 DW）。

背压条件：当某一类的 header 或 data credit 耗尽，该类 TLP 即停发，与链路是否空闲无关。这是「下游缓冲反向约束吞吐」的可计算形式 —— 模型里给每个池一个深度参数，发包扣减、收到 FC update 时归还。

## 8. Gen6 FLIT / FEC（面向未来的模型分支）

Gen6 起改用 PAM4 + **FLIT（固定长度 flit）+ 前向纠错 FEC**，开销模型与 Gen1–5 的「逐 TLP 框架」不同：

- 带宽折扣来自固定的 FLIT 头 + FEC + CRC 开销，而不是每 TLP 的可变 framing。
- 编码不再是 128b/130b，PAM4 每个 symbol 携带 2 bit。

如果工具要覆盖 Gen6，建议把开销模型做成可切换的两种：`per-TLP framing`（Gen1–5）与 `FLIT+FEC`（Gen6+）。

## 9. 建议扫描的维度

做架构探索时，下列参数最值得做敏感性扫描：

- Gen × lane 宽度（名义带宽）
- MPS / MRRS / RCB（开销与拆分）
- Tag 数（并发上限）
- RTT（路径深度、switch 级数、IOMMU 命中率）
- read/write 比例（决定瓶颈是带宽还是往返）
- credit 池深度（背压点）

## 一句话理解

PCIe 性能模型 = `名义带宽（Gen×lane）` × `TLP 开销折扣（MPS/RCB）`，再用 `Little's Law（Tag × bytes / RTT）` 给 read 路径封顶，最后用 `credit 池` 决定背压发生在哪里。
