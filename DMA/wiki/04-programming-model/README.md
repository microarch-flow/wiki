# 04 软件栈与编程模型

这一部分回答的是“软件到底如何和 DMA 形成契约”。前面几章讲的是 DMA 要做什么、硬件里怎么做；这一章讲的是软件如何把任务描述给 DMA、如何判断什么时候真的完成、以及为什么很多看起来像硬件故障的问题，本质上是软件时序和可见性契约没对齐。

## 推荐阅读顺序

1. [软件栈与编程模型](./software-stack.md)
2. [同步、一致性与常见错误](./synchronization-errors.md)
3. [Tiling、Double Buffer 与 Overlap](./tiling-double-buffering.md)
4. [队列、Doorbell 与 Completion](./queues-doorbells-completions.md)

## 本章输出物

- 一条统一软件主线：任务如何被描述、提交、同步和消费
- 一组最容易出错的时序边界：descriptor 可见性、doorbell 顺序、completion 语义、buffer ownership
- 一个关键判断：DMA 的软件价值不只是“会异步”，而是“能把搬运和消费组织成稳定流水”
