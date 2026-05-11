# 地址映射与层级结构

上级：[04 系统架构视角](./README.md)

相关：[DRAM 单元、Bank 与 Row Buffer](../02-memory-cells-arrays/dram-cell-bank-row-buffer.md)、[控制器、并行度与页策略](./controller-parallelism-page-policy.md)

## 为什么物理地址不会直接变成“一个 DRAM 坐标”

从 CPU / GPU 视角看，软件通常先看到虚拟地址；经过地址翻译后，控制器真正处理的是系统物理地址中的若干 bit。对 DRAM 控制器来说，还必须把这些 bit 继续拆解成多个层次：

- channel
- rank
- bank group / bank
- row
- column
- cache-line / byte offset

这一步就是地址映射。

上面这组字段是 `简化抽象`，真实产品里还可能出现 subchannel、pseudo-channel 等更细分层次。

## 每一层分别在干什么

### Channel

独立内存通道，是带宽扩展最直接的手段之一。

更多 channel 往往意味着：

- 更高峰值带宽
- 更高引脚和主板复杂度
- 更高控制器和封装代价

### Rank

更准确地说，rank 是一组共享同一条 channel 数据总线、按片选协同工作的 DRAM devices。

它有助于：

- 扩展容量
- 在部分时序阶段提供一定重叠空间

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
