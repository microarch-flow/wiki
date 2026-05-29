# SoC 外设与 I/O DMA

上级：[05 系统集成](./README.md)

相关：[软件栈与编程模型](../04-programming-model/software-stack.md)、[DMA IP 与厂商图谱](../08-industry-ip/vendor-landscape.md)、[AXI / PCIe 视角下的 DMA](./axi-pcie-view.md)

## 这页在回答什么问题

如何把 AI / HPC 视角下的 DMA，与 MCU/SoC 里更常见的外设 DMA 联系起来理解；以及为什么它们复杂度差很多，但本质问题是同一个。

## 外设 DMA 的第一性问题是把持续数据流从 CPU 控制路径里剥离出来

camera、audio、UART、SPI、Ethernet MAC、storage controller 这类外设都有一个共性：数据不是偶尔来一笔，而是以帧、包、采样流或连续字节流的形式持续出现。若 CPU 每次都参与搬运，不但软件负担大，而且很难满足实时性或能效要求。

所以外设 DMA 的核心动机和高性能 DMA 一样，都是把持续数据流从 CPU 控制路径中剥离出去。不同的是，外设 DMA 常常更强调：

- 实时性和稳定节拍
- 低复杂度、低功耗
- 明确的外设握手语义

而不是追求极致的 descriptor 灵活性或超深 outstanding。

## 它和高性能 DMA 的共性是什么

即使最简单的外设 DMA，也仍然绕不开三件事：

- 某种任务描述入口：寄存器、简单 descriptor 或循环模式
- 某种完成或状态通知：half-transfer、transfer-done、status bit、interrupt
- 某种 backpressure 关系：外设 FIFO、memory port 或 consumer 路径谁在等谁

所以不要把“MCU DMA”和“服务器 DMA”看成完全不同的知识体系。它们的复杂度不同，但都在回答同一个本质问题：如何把数据流稳定地从一端送到另一端，而不让 CPU 逐次介入。

## 它和高性能 DMA 的差异到底在哪

差异首先在任务形状。外设 DMA 的数据单位常是采样流、包或帧片段，强调的是节拍连续和丢包/欠采样不能发生；AI local DMA 或 PCIe DMA 更常处理大块 buffer、multi-queue 和复杂 completion 契约。

差异也在软件接口。很多外设 DMA 更常见的是寄存器编程、circular mode、half-transfer / full-transfer 中断、硬件握手信号，而不是完整 ring/queue。因为它们面对的是更固定的场景，不值得为通用性付出更重的软件和硬件复杂度。

## 外设 DMA 为什么仍然值得放进这套 wiki 主线

因为它提供了最干净的 DMA 核心结构：持续数据流、低 CPU 介入、明确的完成边界、有限资源上的节拍稳定。很多高性能 DMA 的复杂度，其实都是在这条基本主线上逐层叠加出来的。你可以把外设 DMA 看成“DMA 的最小系统版本”，而 NIC/NVMe/GPU/AI DMA 则是这条主线在更高复杂度系统里的扩展。

## 常见误解

常见误解：`外设 DMA 太简单，不值得和高性能 DMA 放在一起看`。实际上很多核心概念，比如 ownership、completion、backpressure，在外设 DMA 里同样成立，只是形态更简单。

常见误解：`外设 DMA 主要看带宽`。实际上很多时候真正关键的是实时性、抖动和握手节拍是否稳定。

常见误解：`没有 queue/ring 就不算现代 DMA`。实际上很多固定功能外设根本不需要完整 queue 模型，寄存器和循环缓冲已经足够合理。

## 一句话理解

外设 DMA 和高性能 DMA 在复杂度上不同，但它们都在解决同一个本质问题：把持续数据流从 CPU 控制路径中剥离出来，并稳定地送到下游。

## 建模启示

这页的关键是别把外设 DMA 简化成纯 memcpy。至少要显式保留 `fifo_level`、`service_period`、`transfer_irq` 和 `memory_ready` 这类节拍状态。

一个够用的结构是：

```text
PeripheralDMAPath {
  producer_rate
  fifo_depth
  dma_service_quanta
  consumer_visibility
}
```

如果只关心平均吞吐，可以把路径折叠成稳定生产者/消费者模型；如果关心 underrun、overrun 或 half-transfer 中断节拍，就必须显式建模 FIFO 和周期事件。
