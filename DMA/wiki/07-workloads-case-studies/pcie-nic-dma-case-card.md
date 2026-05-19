# PCIe NIC DMA 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md)、[队列、Doorbell 与 Completion](../04-programming-model/queues-doorbells-completions.md)、[PCIE Wiki: NIC DMA 案例卡](../../../PCIE/wiki/06-workloads-case-studies/nic-dma-case-card.md)

## 这页在回答什么问题

网卡里的 DMA 为什么是理解 `device DMA + host memory + ring buffer` 最好的入门案例之一。

## 典型系统位置

- DMA engine 位于 NIC 设备侧
- 通过 PCIe 访问 host memory
- 与 RX/TX ring、descriptor、MSI-X 中断紧密配合

## 它通常在解决什么问题

- 把收包数据写入 host buffer
- 从 host buffer 取包发出
- 用 ring 和 completion 把高速包流与 CPU 解耦

## 核心机制

- RX/TX descriptor ring
- host memory DMA read/write
- completion / interrupt moderation
- IOMMU / 映射与隔离

## 最常见瓶颈

- 小包导致 descriptor 和 completion 压力过大
- 中断过多
- IOMMU / 映射管理开销
- cache locality 差

这里的延迟也最好拆开看：

- ring submit 到 DMA issue
- DMA 数据搬运本身
- completion 对 host 软件可见
- interrupt moderation / polling 带来的额外等待

## 最值得抄走的判断

NIC DMA 最值得学的不是“网卡会 DMA”，而是它如何用 `ring + batching + moderation` 维持高速 steady-state。

## 一句话理解

PCIe NIC DMA 展示了设备侧 DMA 如何与主机软件栈形成长期稳定的数据流契约。
