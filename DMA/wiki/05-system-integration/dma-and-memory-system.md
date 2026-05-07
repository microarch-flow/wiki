# DMA 与 Local Memory / DDR / HBM

上级：[05 系统集成](./README.md)

相关：[AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)、[NOC：Memory-Centric NoC](../../NOC/wiki/04-ai-dataflow-system/memory-centric-noc.md)

## 这页在回答什么问题

为什么 DMA 的瓶颈经常不在 DMA 自己，而在它连接的 memory hierarchy。

## DMA 会同时受三类端点约束

- 源端发得出多少
- 互连运得动多少
- 目的端吃得下多少

任何一端失衡，DMA 就无法稳定满速。

## 在 Local Memory 上常见的问题

- SRAM bank conflict
- shared port arbitration
- refill 写入压住 compute 读取
- writeback 抢占有限 buffer

## 在 DDR / HBM 上常见的问题

- row/bank locality 差
- page/burst 边界拆分过多
- 多 DMA 流竞争同一 controller port
- 带宽看似够，但 latency 尾部被放大

## 一个工程上很好用的判断

如果 DMA 指标显示“发得出去但完成慢”，优先检查：

- memory controller port 利用率
- response latency
- destination ejection / bank 冲突

## 一句话理解

DMA 的真实上限不是自己定义的，而是由 `local memory + interconnect + external memory` 共同钳制出来的。
