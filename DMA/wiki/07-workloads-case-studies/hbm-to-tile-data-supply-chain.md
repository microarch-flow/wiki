# HBM 到 Tile 的数据供给链

上级：[07 工作负载与案例](./README.md)

相关：[AI 加速器里的 DMA](./ai-accelerator-dma.md)、[NOC：KV Cache / Decode Memory Path 深化](../../NOC/wiki/04-ai-dataflow-system/kv-cache-decode-memory-path.md)

## 这页在回答什么问题

如果把 AI 芯片里一次典型的数据供给过程完整展开，DMA 到底处在什么位置，为什么它常常成为真正的执行骨架。

## 一条典型路径

- runtime/mapper 决定下一批 tile
- DMA 从 HBM 拉取 tensor block
- NoC 把数据送到 cluster SRAM
- local DMA 或 load 单元再把数据送到 tile buffer
- compute 消费
- 结果经 writeback 路径回流

## 这条链里最容易出问题的地方

- HBM latency 被低估
- DMA outstanding 不足导致供数断流
- NoC response 与 bulk transfer 混跑
- cluster SRAM 写入和 tile 读取打架
- writeback 抢占 refill

## 为什么这页重要

很多人会把问题割裂成：

- HBM 问题
- NoC 问题
- SRAM 问题
- compute mapping 问题

但在真实系统里，DMA 是把这些问题串起来的那根主线。

## 一个系统判断框架

先问：

1. 数据在哪一级等
2. 谁在等谁
3. DMA 是否在正确时间发出了足够但不过量的流量

## 一句话理解

在 AI 芯片里，HBM 到 tile 的供给链能否稳定运行，往往不取决于单点峰值，而取决于 DMA 是否把整条链路节奏组织对了。
