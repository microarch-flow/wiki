# 地址映射与层级结构

上级：[04 系统架构视角](./README.md)

相关：[DRAM 单元、Bank 与 Row Buffer](../02-memory-cells-arrays/dram-cell-bank-row-buffer.md)、[控制器、并行度与页策略](./controller-parallelism-page-policy.md)

## 为什么物理地址不会直接变成“一个 DRAM 坐标”

从 CPU / GPU 视角看，软件给的是线性地址；但对 DRAM 控制器来说，必须把地址拆解成多个层次：

- channel
- rank
- bank
- row
- column

这一步就是地址映射。

## 每一层分别在干什么

### Channel

独立内存通道，是带宽扩展最直接的手段之一。

更多 channel 往往意味着：

- 更高峰值带宽
- 更高引脚和主板复杂度
- 更高控制器和封装代价

### Rank

可以理解为共享一部分通道资源的物理子模块组织方式。

它有助于：

- 扩展容量
- 提供一定切换级并行

但不等于“免费提升带宽”。

### Bank

bank 是 DRAM 内部最关键的并行资源之一。

多个 bank 并行，有助于：

- 隐藏单 bank 行切换代价
- 提高总吞吐
- 让控制器有更多调度空间

### Row / Column

row 决定一次 activate 打开的行；column 决定从该行中取哪个位置。

这正是 row hit / miss 的来源。

## 地址映射为什么重要

相同峰值带宽的 DRAM 系统，地址映射策略不同，实际效果可能差很多。

映射策略通常在平衡：

- 连续访问是否分散到多个 bank
- 行局部性是否被保留
- 多线程访问是否互相冲突

所以地址映射不是简单的编码问题，而是系统吞吐和尾延迟优化问题。

## 从架构角度该怎么看

当你评估一个内存系统时，可以先问：

- 连续 cache line 被映射到哪里
- 访问是否容易打散到不同 bank / channel
- workload 更依赖 row locality，还是 bank-level parallelism

很多“纸面带宽够高却跑不满”的问题，根源都在这里。

## 一句话理解

地址映射把软件看到的线性地址，变成了硬件可调度的 `channel/rank/bank/row/column` 资源分配问题。
