# DRAM timing 参数速查

上级：[参考资料](./README.md)
相关：[关键 timing 参数：tRCD、tRP、tRAS、tCL 的物理来源](../05-dram-protocol-families/timing-parameters-trcd-trp-tras.md), [ACT、RD、WR、PRE：DRAM 命令集为什么长这样](../05-dram-protocol-families/commands-act-rd-wr-pre.md)

## 这页在回答什么问题

如果只想快速回忆主要 timing 参数分别约束哪段行为、影响哪类冲突，这页应该提供怎样的紧凑对照。

## 正文

这一页不重复解释所有物理细节，而是把最常见的 DRAM timing 参数压成一个能快速拿来用的对照表。读法很简单：先看“它在约束哪两个动作之间”，再看“它本质上在等什么物理过程完成”，最后看“如果它变大或撞上了，会把哪类访问变贵”。

## 核心参数

`tRCD`

- 全称：`Row to Column Delay`
- 约束：`ACT -> RD/WR`
- 在等什么：开行后整行感测和 row buffer 稳定到可列访问
- 主要影响：row miss 的首个列访问成本

`tCL`

- 全称：`CAS Latency`
- 约束：`RD -> first data out`
- 在等什么：列路径、内部预取、I/O 启动把首拍数据推出去
- 主要影响：读请求从列命令到外部可见数据的返回时间

`tRAS`

- 全称：`Row Active Time`
- 约束：`ACT -> PRE` 的最短保持时间
- 在等什么：感测、恢复以及该行必须活够的最短窗口
- 主要影响：一行最早多久才能安全关闭

`tRP`

- 全称：`Row Precharge Time`
- 约束：`PRE -> next ACT`
- 在等什么：关行后位线和相关状态恢复到下一次开行前的初始条件
- 主要影响：row conflict 后切换到下一行的成本

`tWR`

- 全称：`Write Recovery Time`
- 约束：`WR -> PRE`
- 在等什么：写入后数据真正写回 cell 并稳定
- 主要影响：写后不能立刻关行，写密集场景会受影响

`tRFC`

- 全称：`Refresh Cycle Time`
- 约束：refresh 占用窗口
- 在等什么：一次 refresh 操作完整占用并释放相关阵列资源
- 主要影响：refresh 对正常请求的阻塞长度

`tCCD`

- 全称：`Column to Column Delay`
- 约束：相邻列命令之间的最小间隔
- 在等什么：列访问管线和数据总线节奏
- 主要影响：连续 burst 的列吞吐节拍

`tBURST`

- 含义：一次 burst 在数据总线上持续占用的时间
- 约束：一条读写命令在总线侧实际持续多长
- 在等什么：不是等待，而是 burst 本身的传输长度
- 主要影响：总线占用与列命令节拍配合

`tRRD`

- 全称：`Row to Row Delay`
- 约束：相邻 `ACT` 之间的最小间隔
- 在等什么：开行相关的瞬时资源和电流冲击限制
- 主要影响：多 bank 并行开行速度

`tFAW`

- 全称：`Four Activate Window`
- 约束：一个时间窗口内允许的 `ACT` 数量上限
- 在等什么：功耗/电流峰值约束，而不是单条命令逻辑依赖
- 主要影响：密集多 bank 开行时的并行度

## 先记哪几条最重要

如果你只想先抓主干，优先记下面这组：

- `tRCD`：开行后多久能列访问
- `tCL`：读命令后多久看到第一拍数据
- `tRAS`：一行至少要开多久
- `tRP`：关行后多久能开下一行
- `tRFC`：一次 refresh 会挡多久

只靠这五条，你已经能解释很多最基本的现象：

- 为什么 row hit 比 row miss 便宜
- 为什么 row conflict 更贵
- 为什么 refresh 会制造尾延迟
- 为什么 DRAM 不是固定延迟数组

## 把它们串成脑内时序

最常见的一条读路径可以先记成：

```text
ACT --tRCD--> RD --tCL--> first data
ACT ---------tRAS--------> PRE --tRP--> next ACT
```

写路径只要再多补一条：

```text
WR --tWR--> PRE
```

refresh 则可以脑内记成：

```text
REF --tRFC--> normal requests can fully resume
```

## 它们分别更影响谁

如果你的请求主要是：

- `row miss`：更敏感 `tRCD + tCL`
- `row conflict`：更敏感 `tRP + tRCD + tCL`
- `write-heavy`：更敏感 `tWR`
- `many-bank parallel ACT`：更敏感 `tRRD / tFAW`
- `refresh-sensitive workload`：更敏感 `tRFC`

也就是说，不同参数并不是平均影响所有场景，而是在不同访问形状下放大不同代价。

## 不该怎么记

最容易犯的错有三个：

- 把所有 timing 参数都记成“神秘常数”
- 把 `MT/s` 的提升误当成所有 timing 绝对时间都同步大幅变短
- 把 DRAM 访问时间压成一个固定 latency，忽略 row hit/miss/conflict 分层

如果只避免这三种错，很多 controller 和系统行为就已经容易解释得多。

## 一句话理解

DRAM timing 参数不是一堆要死记的符号，而是在给“开行、列访问、恢复、关行、刷新”这些动作之间的物理等待窗口起名字。

## 建模启示

做模型时，这页最直接的用途不是提供“精确数字”，而是提醒你最少要保留哪些命令间约束。一个很粗但够用的层次可以是：

```text
row_hit_cost
row_miss_cost
row_conflict_cost
refresh_block_cost
```

如果要再细一点，就至少把下面这些 guard 保留下来：

```text
ACT -> RD/WR guarded by tRCD
RD -> data visible guarded by tCL
ACT -> PRE guarded by tRAS
PRE -> next ACT guarded by tRP
WR -> PRE guarded by tWR
REF blocks service for tRFC
```

只要这些约束还在，模型就还能表达 DRAM 访问成本为什么是分层的；一旦全被折成一个统一 latency，很多后续结论都会失真。
