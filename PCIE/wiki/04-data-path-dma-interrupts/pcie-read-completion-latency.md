# PCIe Read Completion 延迟为什么敏感

上级：[04 数据路径、DMA 与中断](./README.md)

相关：[设备 DMA 的读写路径](./device-dma-read-write-flow.md)、[带宽、延迟、Credit、MPS 与 MRRS](../05-performance-debug/bandwidth-latency-credit-mps-mrrs.md)

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

PCIe read 性能差，常常不是“带宽不够”，而是 `飞行中的请求数 x 单次 completion 往返延迟` 乘不起来。

## 一句话理解

read completion latency 是很多 PCIE 设备吞吐上不去的隐藏主线，因为它直接限制了 device 能把流水线撑多深。
