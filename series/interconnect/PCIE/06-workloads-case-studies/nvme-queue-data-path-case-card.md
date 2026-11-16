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
- 控制器 DMA read 主机 SQE 取命令；数据方向由命令决定
- 控制器向 CQ 写 CQE，主机通过 MSI-X 或轮询处理

例如 NVMe **Read** 从存储介质取数据，控制器通常以 PCIe DMA write 将数据写到主机缓冲；NVMe **Write** 则通常以 DMA read 从主机取数据，再写入存储介质。两种命令都可在执行后写 CQE，并按配置发中断或由软件轮询。

这里的 NVMe Read/Write 是存储命令；设备 DMA read 收到的 PCIe Completion 是事务返回；CQE 是命令完成状态。三个对象不能互相代替。

## 为什么它值得学

因为它把以下几条线绑得很紧：

- software queue depth
- device 并发能力
- read / write 数据路径差异
- completion 处理成本

## 一句话理解

NVMe 展示了 PCIE 设备如何把 `队列化控制面` 和 `DMA 数据面` 组合成高 IOPS、高吞吐的存储路径。
