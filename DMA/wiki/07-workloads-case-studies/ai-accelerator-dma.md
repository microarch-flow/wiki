# AI 加速器里的 DMA

上级：[07 工作负载与案例](./README.md)

相关：[Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)、[NOC：DMA Engine / Request-Response Scheduling](../../NOC/wiki/04-ai-dataflow-system/dma-engine-request-response-scheduling.md)

## 这页在回答什么问题

为什么在 AI accelerator 里，DMA 常常比传统 SoC 里的 DMA 更核心、更复杂，也更值得单独研究。

## AI 系统里的 DMA 典型路径

- HBM -> cluster SRAM
- SRAM -> tile local buffer
- result -> writeback buffer -> HBM

DMA 负责把这些路径拼成可持续供给 compute 的节奏。

## 为什么它更难

- 数据量大
- 并发 stream 多
- refill / compute / writeback 强耦合
- NoC 与 local memory 都可能成为瓶颈

## 最重要的能力

- 高并发 outstanding
- 多 stream 调度
- 强 overlap
- 对 local memory 布局友好

## 一句话理解

AI 加速器里的 DMA 已经不是“辅助搬运器”，而是连接 HBM、NoC、SRAM 和 compute pipeline 的执行骨架。
