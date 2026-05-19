# 设备 DMA 的读写路径

上级：[04 数据路径、DMA 与中断](./README.md)

相关：[DMA Wiki: AXI / PCIe 视角下的 DMA](../../../DMA/wiki/05-system-integration/axi-pcie-view.md)、[队列、Doorbell、Completion 与 MSI-X](./queues-doorbells-completions-msix.md)

## 这页在回答什么问题

设备侧 DMA 在 PCIE 系统里到底是怎样读写主机内存的，以及为什么 read 和 write 体验差别很大。

## 一条常见提交路径

1. host 软件在主机内存准备 descriptor / buffer
2. host 通过 MMIO 写 doorbell
3. device 通过 DMA read 取 descriptor
4. device 根据任务执行 DMA read 或 DMA write
5. device 写 completion record，并可触发 MSI-X

## DMA write 常见特点

- 数据从 device 推向 host memory
- 常见于收包、写结果、写 completion record
- 容易形成高吞吐流

## DMA read 常见特点

- device 从 host memory 拉数据
- 常见于 descriptor fetch、发包、读输入数据
- 更依赖 completion 返回路径和 outstanding 深度

## 为什么两者不能混看

因为 PCIe read 往往更容易受限于：

- completion latency
- outstanding tag 数量
- credit 和返回路径拥塞

而 write 更常受限于：

- host memory 接收路径
- write combining / batching
- device 发包组织能力

## 一句话理解

PCIE DMA 不是单一动作，而是一条由 `MMIO 提交 + DMA 访问 + completion / interrupt 通知` 组成的完整 host-device 数据路径。
