# DMA 引擎的组成

上级：[03 DMA 引擎微架构](./README.md)

相关：[地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)、[DMA 与 NoC](../05-system-integration/dma-and-noc.md)

## 这页在回答什么问题

一个 DMA engine 到底由哪些功能块组成，以及哪些能力决定它只是“能用”，哪些能力决定它“好用且高性能”。

## 一条最小数据路径

一个最小 DMA engine 通常包含：

- descriptor fetch / command queue
- address generation
- read request issue
- read response / data buffer
- write request / write data path
- completion tracking

对通用 memory-to-memory DMA 来说，上面这些子路径通常都需要。  
只有更简单的单向 peripheral DMA，才可能裁掉其中一部分子路径或把它们做得很薄。

## 常见的关键子模块

- descriptor parser
- outstanding table
- reorder / completion buffer
- burst splitter / coalescer
- error handling
- interrupt / doorbell logic

## 为什么简单 DMA 和高性能 DMA 差异巨大

决定差异的往往不是“会不会搬”，而是：

- 能不能同时追踪很多未完成事务
- 能不能处理乱序返回
- 能不能在复杂边界上自动拆分
- 能不能做多 stream、公平性和优先级控制

## 一个实用拆解方法

看 DMA engine 时，优先问四件事：

1. 命令从哪里来
2. 地址如何生成和翻译
3. 请求如何发、回包如何收
4. 完成如何定义和通知

## 一句话理解

DMA engine 本质上是“命令解释器 + 传输调度器 + 完成跟踪器”，不是一条简单搬运通路。
