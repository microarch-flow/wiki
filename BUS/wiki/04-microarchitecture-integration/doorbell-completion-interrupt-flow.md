# Doorbell、Completion 与 Interrupt Flow

上级：[04 微架构与系统集成](./README.md)

相关：[DMA Wiki 首页](../../../DMA/wiki/README.md)、[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[PCIE Wiki: 队列、Doorbell、Completion 与 MSI-X](../../../PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

为什么很多 SoC 软件路径里总会反复出现 doorbell、completion 和 interrupt，它们在 BUS 上到底是怎样串起来的。

这里先统一三个词：

- `completion record / completion queue entry`：写在内存里的完成记录
- `status bit / status register`：设备内部或 MMIO 可见的完成状态
- `interrupt`：把“该看完成状态了”的通知推给 CPU

## 一条典型提交路径

常见流程是：

1. 软件在内存中准备 descriptor 或 queue entry
2. 软件通过 MMIO 写 doorbell 寄存器
3. device 或 DMA 通过 BUS 读到新任务
4. 数据路径开始运行

这里 doorbell 本质上是一笔控制面 bus write。

## 一条典型完成路径

常见流程是：

1. device 更新 completion record 或 status memory
2. device 更新状态寄存器或内部完成位
3. device 触发 interrupt，或软件轮询看到完成

这说明“任务完成”常常不是单一事件，而是：

- memory update
- status visible
- interrupt delivery

三者协同成立。

## 为什么这里容易出 bug

因为它横跨了：

- cacheable memory
- MMIO register
- interrupt controller
- DMA / device local state

如果顺序或可见性处理不对，就会出现：

- doorbell 写了但设备还没看到 descriptor
- completion 已写回但 CPU 看不到
- interrupt 先到了，但状态还没稳定

## 一句话理解

doorbell、completion 和 interrupt 共同构成了 SoC 里最典型的一条“控制提交到完成通知”的 bus-level 协同链路。
