# DMA 引擎的组成

上级：[03 DMA 引擎微架构](./README.md)

相关：[地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)、[调度、Outstanding 与回包组织](./scheduling-outstanding.md)、[DMA 与 NoC](../05-system-integration/dma-and-noc.md)

## 这页在回答什么问题

一个 DMA engine 到底由哪些功能块组成，以及哪些块只是“能搬就够”，哪些块决定它能否在复杂系统里高效、稳定、可调试地搬。

## DMA 不是一条直线数据通路

最容易低估 DMA 的方式，是把它想成“左边读，右边写”的数据搬运管道。这个想法只抓住了数据通路，却遗漏了真正决定系统行为的控制通路和状态通路。现实里的 DMA engine 更像三套结构叠在一起：

- 命令路径：从 descriptor 或 queue entry 生成内部任务
- 数据路径：发 read、收 data、发 write、处理边界
- 完成路径：记录状态、回收资源、通知软件或下游

只要系统允许多事务并发、乱序返回、fault 报告或多通道共享，这三条路径就不可能再被压扁成一个简单状态机。

## 一个最小可用 DMA engine 至少有什么

即使是最小的 memory-to-memory DMA，也通常需要这些块：

- descriptor fetch 或 command receive
- descriptor parser / command decoder
- address generation
- read request issue
- data buffer 或 response receive
- write request issue
- completion tracking

如果系统更复杂，还会继续长出 `outstanding table`、`burst splitter`、`reorder buffer`、`fault recorder`、`interrupt/completion writeback` 这些结构。它们不是锦上添花，而是对系统约束的直接回应。例如只要 read response 可能乱序回来，就必须有某种映射结构把 response 对回原任务；只要 completion 可能晚于 data write 对软件可见，就必须把完成路径建成独立状态。

## 为什么简单 DMA 和高性能 DMA 差这么多

差异并不在“会不会搬”，而在“要不要为复杂系统语义显式留状态”。简单 DMA 往往假设：

- 任务量不大
- outstanding 很小
- 返回路径基本顺序
- channel 少或没有共享隔离需求

高性能 DMA 则通常必须显式面对相反条件：descriptor 流源源不断，memory latency 需要被隐藏，返回乱序是常态，多队列和多 context 共享一套硬件资源。于是 DMA 不得不演化出更像处理器后端的内部结构，只不过它执行的是“数据移动指令”而不是通用算术指令。

## 先看哪四个块最有判断力

当你第一次读一个 DMA IP 文档时，不要平均用力。优先问四件事：

1. 命令从哪里来，是寄存器、descriptor 还是 queue。
2. 地址如何生成与翻译，是线性、stride 还是更高维。
3. 请求如何发出去，outstanding 和 burst 是如何组织的。
4. 完成如何定义，completion、error 和 resource release 怎么闭环。

这四个问题几乎能直接决定你后面该把注意力放在 AXI 通道、NoC 注入、IOMMU、local buffer 还是 software-visible completion 上。

## 常见误解

常见误解：`DMA engine 就是 read path + write path`。实际上 descriptor 路径、completion 路径和 fault 路径同样是主线。

常见误解：`只要数据路径够宽，DMA 就会快`。实际上没有足够的任务受理、outstanding 跟踪和返回组织，再宽的数据路径也打不满。

常见误解：`completion 是软件层附加物`。实际上 completion tracking 是硬件资源回收和 forward progress 的组成部分。

## 一句话理解

DMA engine 本质上是“命令解释器 + 数据事务调度器 + 完成与资源回收器”，而不是一条简单搬运通路。

## 建模启示

这一页适合定义 DMA engine 的骨架状态机。event-driven 仿真里，建议显式分成 `cmd_frontend`、`data_mover`、`completion_backend` 三段，而不是用一个总状态表示“busy”。

一个最小结构草图是：

```text
DMAEngineState {
  fetch_q
  issue_q
  inflight_table
  resp_buffer
  completion_q
}
```

如果只关心峰值吞吐，可以把 `resp_buffer` 和 `completion_q` 折叠成平均服务时间；如果关心 tail latency、hang 或错误恢复，它们必须保留，因为很多问题正出在数据已经回来但 completion 还没闭环这一段。
