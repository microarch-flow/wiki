# PCIe Read Completion 延迟为什么敏感

上级：[04 数据路径、DMA 与中断](./README.md)

相关：[设备 DMA 的读写路径](./device-dma-read-write-flow.md)、[带宽、延迟、Credit、MPS 与 MRRS](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)、[PCIe 建模参数与公式速查](../08-reference/pcie-modeling-params.md)

## 这页在回答什么问题

为什么很多 PCIE 设备在读主机内存时更容易掉速，read completion latency 到底卡在哪里。

## 一个最短链条

1. device 发起 memory read request
2. 请求穿过 Root Complex / switch / host memory 路径
3. host 侧准备返回数据
4. completion TLP 沿返回路径回到 device

只要其中任一段变慢，device 就会等。

## 为什么它比 write 更敏感

- read 必须等返回
- device 可并发挂起的请求数有限
- completion 返回分片和调度可能带来额外延迟
- host 侧缓存、IOMMU、内存拥塞都会放大等待

## 最常见的四类瓶颈

- outstanding 深度不够
- MRRS / MPS 配置不合适
- switch / root complex 返回路径拥塞
- host memory 或 IOMMU 延迟偏大

## 最值得记住的判断

PCIe read 性能差，常常不是“带宽不够”，而是 `在途请求数 × 每请求有效数据 / 平均往返时间` 达不到所需吞吐。

## 量化小节（Little's Law）

上面那句判断写成公式就是：

```
read 吞吐 ≈ (平均在途请求数 × 每请求平均有效字节) / 平均 RTT
```

要灌满链路所需的并发深度（带宽时延积）：

```
所需 outstanding ≥ 链路有效带宽 × RTT / bytes_per_request
```

这里使用同一稳态采样窗口：平均在途数是随时间平均的实际请求数，而不是直接把硬件槽容量当作实际值；RTT 从请求发出算到该请求全部所需数据成功返回、请求槽可回收。首个 CplD 到达时间可能更早。请求分片且末片延迟变大时，槽会被占用更久。若用硬槽上限 N 估算，则 `N × S / RTT` 只是并发窗口上界；结果还受请求供给、Completion 返回带宽、缓冲和其他资源限制。

三个量分别被这些参数钳制：

- **outstanding_requests** —— 取决于 Tag 模式、目标能力和实际槽数：5-bit 通常最多 32，Extended 已启用最多 256；10-bit 已启用且目标支持时，单个 completer 最多 768。
- **每请求平均有效字节** —— MRRS 只限制单 read 的最大请求长度；实际长度还受地址边界、剩余数据和请求生成器影响，不能直接当成 MRRS。
- **平均 RTT** —— 包含 RC、switch、内存及 IOMMU 路径；数百 ns 或 µs 量级只能作为未校准的示例假设，各段实际值应通过目标平台的计数器或测量确定。

举例：Gen4 x8 的编码后上界约 15.75 GB/s；假设目标有效吞吐 12.8 GB/s、RTT=1 µs、单请求 512 B，则需要 `ceil(12.8e9 × 1e-6 / 512) = 25` 个并发请求以覆盖该目标的带宽时延积。目标还须低于扣除协议开销后的实际有效带宽；若只有 32 个可用槽，RTT 进一步上升或其他资源不足仍可能导致掉速。完整参数表见 [PCIe 建模参数与公式速查](../08-reference/pcie-modeling-params.md)。

## 一句话理解

read completion latency 是很多 PCIE 设备吞吐上不去的隐藏主线，因为它直接限制了 device 能把流水线撑多深。
