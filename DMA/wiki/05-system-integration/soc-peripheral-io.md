# SoC 外设与 I/O DMA

上级：[05 系统集成](./README.md)

相关：[软件栈与编程模型](../04-programming-model/software-stack.md)、[DMA IP 与厂商图谱](../08-industry-ip/vendor-landscape.md)

## 这页在回答什么问题

如何把 AI / HPC 视角下的 DMA，与 MCU/SoC 里更常见的外设 DMA 联系起来理解。

## 常见外设 DMA 场景

- camera / ISP
- audio
- UART / SPI / I2C
- Ethernet / storage controller

这些场景都强调“持续流动的数据”和“低 CPU 介入”。

## 与高性能 DMA 的共性

- 都需要 descriptor 或 ring
- 都需要 completion / interrupt
- 都有 backpressure 与目的端消费问题

## 与高性能 DMA 的差异

- 通常更强调实时性和稳定性
- 数据单位常是帧、包、采样流，不一定是大块 tensor
- 硬件更倾向低复杂度、低功耗和确定性

## 一句话理解

外设 DMA 和高性能 DMA 在复杂度上不同，但它们都在解决同一个本质问题：把持续数据流从 CPU 控制路径中剥离出来。
