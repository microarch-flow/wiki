# NIC DMA 案例卡

上级：[06 工作负载与案例](./README.md)

相关：[DMA Wiki: PCIe NIC DMA 案例卡](../../../../microarchitecture/DMA/wiki/07-workloads-case-studies/pcie-nic-dma-case-card.md)

## 这页在回答什么问题

为什么网卡是理解 PCIE 数据路径最好的起点之一。

## 典型系统位置

- NIC 作为 endpoint 挂在 PCIE 上
- host memory 中有 RX/TX ring 和 data buffer
- 中断通常通过 MSI-X 回到 CPU

## 最关键的三条主线

- **RX**：主机在 RX ring 发布空缓冲描述符；NIC 收包后以 DMA write 把载荷写入主机，再发布完成状态。若可用描述符耗尽，设备可能丢包或暂停，具体计数与策略由 NIC 定义。
- **TX**：主机发布待发送缓冲描述符；NIC 以 DMA read 取主机载荷，再向网络发送并发布完成状态。设备 DMA read 的 PCIe Completion 与软件完成记录不同。
- **通知**：小包使每包 descriptor 和 CQE 处理占比增大。中断合并可在累计门限或定时后通知，减少每秒中断数，但首个完成可能等待更久；轮询也能消费已发布的完成。

## 最常见瓶颈

- 小包导致 doorbell、descriptor、completion 压力过大
- 中断太频繁
- IOMMU / mapping 开销不可忽视
- NUMA 和 host memory locality 差

## 最值得抄走的判断

NIC 让你最容易看清：高性能设备真正依赖的不是“链路很快”，而是 `ring + batching + moderation + DMA` 的稳态协同。

## 一句话理解

NIC DMA 是学习 PCIE host-device 稳态数据流最具代表性的系统案例。
