# NIC DMA 案例卡

上级：[06 工作负载与案例](./README.md)

相关：[DMA Wiki: PCIe NIC DMA 案例卡](../../../DMA/wiki/07-workloads-case-studies/pcie-nic-dma-case-card.md)

## 这页在回答什么问题

为什么网卡是理解 PCIE 数据路径最好的起点之一。

## 典型系统位置

- NIC 作为 endpoint 挂在 PCIE 上
- host memory 中有 RX/TX ring 和 data buffer
- 中断通常通过 MSI-X 回到 CPU

## 最关键的三条主线

- descriptor / ring 如何喂给设备
- DMA write 如何把包写进主机内存
- completion 和 interrupt moderation 如何平衡吞吐与 CPU 开销

## 最常见瓶颈

- 小包导致 doorbell、descriptor、completion 压力过大
- 中断太频繁
- IOMMU / mapping 开销不可忽视
- NUMA 和 host memory locality 差

## 最值得抄走的判断

NIC 让你最容易看清：高性能设备真正依赖的不是“链路很快”，而是 `ring + batching + moderation + DMA` 的稳态协同。

## 一句话理解

NIC DMA 是学习 PCIE host-device 稳态数据流最具代表性的系统案例。
