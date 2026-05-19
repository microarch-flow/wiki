# PCIE 高频问题

上级：[08 术语与检查清单](./README.md)

## 为什么 write 常比 read 更容易跑满

因为 read 依赖 completion 返回路径，容易被往返延迟和 outstanding 深度限制。

## BAR 和 DMA 地址有什么区别

BAR 是主机访问设备资源的窗口；DMA 地址是设备访问主机内存时使用的地址视角。

## 为什么设备明明支持 DMA，却还要看 IOMMU

因为“能访问”不等于“应该被允许任意访问”，还要考虑翻译、隔离和虚拟化。

## 为什么 MSI-X 常和 queue 一起讨论

因为高性能设备通常用 queue 承载任务，用 MSI-X 通知主机推进完成处理。

## 为什么看起来是 PCIE 问题，最后却落到 host memory

因为 host-device 路径的尾部常常连着 IOMMU、DDR、NUMA 和 CPU 软件栈，链路不是唯一瓶颈。
