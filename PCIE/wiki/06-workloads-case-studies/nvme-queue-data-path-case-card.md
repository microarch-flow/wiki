# NVMe 队列与数据路径案例卡

上级：[06 工作负载与案例](./README.md)

相关：[队列、Doorbell、Completion 与 MSI-X](../04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

为什么 NVMe 是理解“低开销提交队列 + 高并发 completion”最好的 PCIE 存储案例。

## 典型系统位置

- NVMe controller 作为 PCIe endpoint
- host software 维护 submission / completion queue
- 数据通过 DMA 在 host memory 和 device 之间流动

## 最关键的机制

- 多队列并发
- MMIO doorbell 提交
- DMA 读命令、写结果
- MSI-X 或轮询完成

## 为什么它值得学

因为它把以下几条线绑得很紧：

- software queue depth
- device 并发能力
- read / write 数据路径差异
- completion 处理成本

## 一句话理解

NVMe 展示了 PCIE 设备如何把 `队列化控制面` 和 `DMA 数据面` 组合成高 IOPS、高吞吐的存储路径。
