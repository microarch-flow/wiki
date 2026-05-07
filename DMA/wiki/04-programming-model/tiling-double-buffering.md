# Tiling、Double Buffer 与 Overlap

上级：[04 软件栈与编程模型](./README.md)

相关：[AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)

## 这页在回答什么问题

为什么在 AI 和高性能系统里，DMA 最重要的价值经常不是单次搬运速度，而是支撑稳定 overlap。

## 三个关键动作

- 预取下一块数据
- 当前块参与计算
- 把上一块结果写回

只要这三件事能并行，系统吞吐通常就会明显提升。

## Double Buffer 的本质

它不是“多放一块 buffer”这么简单，而是把：

- 生产
- 消费
- 回收

三种时序拆开，减少相互等待。

## Tiling 为什么总和 DMA 绑在一起

tile 大小会直接决定：

- DMA 任务粒度
- burst 形状
- local SRAM 占用
- overlap 难度

所以 tile 设计和 DMA 调度本来就是一体的。

## 一句话理解

当系统追求高吞吐时，DMA 的核心能力就不再是“搬”，而是“让搬运和计算能稳定重叠起来”。
