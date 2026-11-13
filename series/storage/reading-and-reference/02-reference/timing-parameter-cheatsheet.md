# DRAM timing 参数速查

上级：[参考资料](./README.md)
相关：[关键 timing 参数：tRCD、tRP、tRAS、tCL 的物理来源](../../03-dram/protocols/timing-parameters-trcd-trp-tras.md), [ACT、RD、WR、PRE：DRAM 命令集为什么长这样](../../03-dram/protocols/commands-act-rd-wr-pre.md)

## 这页在回答什么问题

如果只想快速回忆主要 timing 参数分别约束哪段行为、影响哪类冲突，这页应该提供怎样的紧凑对照。

## 按参考动作查找时序约束

这一页不重复解释所有物理细节，而是把最常见的 DRAM timing 参数压成一个对照表。除特别说明，以下 DDR4 外部命令简式假设 CA parity 关闭（PL=0）且 CS-to-CA latency 关闭。开启其他模式须按器件手册定义采样沿和 guard，不能机械给每个命令间隔加 PL。

## 核心参数

`tRCD`

- 全称：`Row to Column Delay`
- 约束：DDR4 的 `ACT -> 内部 RD/WR`；外部列命令可提前 AL，仍需满足其他命令规则
- 在等什么：开行后整行感测和 row buffer 稳定到可列访问
- 主要影响：row miss 的首个列访问成本

`tCL`

- 全称：`CAS Latency`
- 约束：在上述 PL=0 模式下，外部 `RD -> first data out` 的名义延迟是 `RL = AL + CL`，且 AL=0 时等于 CL。Alliance Memory AS4C512M8D4A 的 CA parity 模式为 `RL=AL+CL+PL`，`WL=AL+CWL+PL`；AL=0、CL=11、PL=4 的读例为 15 CK。见[原厂手册表 29 注 3 与 Burst Read 示例](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_4Gb_DDR4_AS4C512M8D4A-75BCN_75BIN_Aug2022_Ver1.0.pdf)。
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
- 约束：写数据 burst 结束后的指定参考沿到 PRE；并非 `WR` 命令沿直接加 `tWR`
- 在等什么：写入后数据真正写回 cell 并稳定
- 主要影响：写后不能立刻关行，写密集场景会受影响

`tRFC`

- 全称：`Refresh Cycle Time`
- 约束：refresh 占用窗口
- 在等什么：一次 refresh 操作完整占用并释放相关阵列资源
- 主要影响：refresh 对正常请求的阻塞长度

`tRTP`

- 全称：`Read to Precharge`
- 约束：DDR4 显式 PRE 对同 bank 外部 RD 的下界含 `RD + AL + nRTP`；还要同时满足 `ACT + nRAS` 等约束。参考沿及可用值以器件模式为准。
- 主要影响：读后最早关行时刻，不是首数据返回时刻。

`tCCD`

- 全称：`Column to Column Delay`
- 约束：所选 DDR4 模式下同 rank 的连续同向 RD→RD 或 WR→WR 列命令间隔；同 bank group 的 tCCD_L 与跨组 tCCD_S 分开。读写反向切换另检查方向、rank 和 DQ 时序
- 在等什么：列访问管线和数据总线节奏
- 主要影响：连续 burst 的列吞吐节拍

`tBURST`

- 含义：一次 burst 在数据总线上持续占用的时间
- 约束：一条读写命令在总线侧实际持续多长
- 在等什么：不是等待，而是 burst 本身的传输长度
- 主要影响：总线占用与列命令节拍配合

`tRRD`

- 全称：`Row to Row Delay`
- 约束：DDR4 同 rank 不同 bank 的相邻 `ACT` 最小间隔；同 bank group 用 tRRD_L，跨组用 tRRD_S。相同 bank 的再次 ACT 另受 tRC/PRE 等约束
- 在等什么：开行相关的瞬时资源和电流冲击限制
- 主要影响：多 bank 并行开行速度

`tFAW`

- 全称：`Four Activate Window`
- 约束：同 rank 的滚动 tFAW 时间窗内至多四次 ACT；第五次 ACT 的时刻不早于前四次中最早 ACT + tFAW，且仍须满足 tRRD 等其他约束
- 在等什么：功耗/电流峰值约束，而不是单条命令逻辑依赖
- 主要影响：密集多 bank 开行时的并行度

## 先记哪几条最重要

如果你只想先抓主干，优先记下面这组：

- `tRCD`：开行后多久能列访问
- `RL=AL+CL`：外部读命令后首数据的名义时刻（CK 周期）
- `tRAS`：一行至少要开多久
- `tRP`：关行后多久能开下一行
- `tRTP / tWR`：读后和写数据后何时能关行；参考沿不同
- `tRFC`：一次 refresh 会挡多久

只靠这五条，你已经能解释很多最基本的现象：

- 为什么 row hit 比 row miss 便宜
- 为什么 row conflict 更贵
- 为什么 refresh 会制造尾延迟
- 为什么 DRAM 不是固定延迟数组

## 把它们串成脑内时序

你可以把整个过程想象成去银行保险柜取东西：先让工作人员打开保险柜（ACT，等 tRCD），然后找到你的格子取出物品（RD，等 RL=AL+CL），取完后工作人员要锁好保险柜（PRE，等 tRP），你才能请求打开另一个保险柜。如果你要取的东西在同一个已打开的保险柜里，就省掉了开锁和关锁的时间——这就是 row hit 快的原因。

下面的命令示意假设 `AL=0`、PL=0 且 CS-to-CA latency 关闭：

```text
ACT --tRCD--> RD --RL=AL+CL--> first data
ACT ---------tRAS--------> PRE --tRP--> next ACT
```

DDR4 BL8、禁用写 CRC、PL=0 且 CS-to-CA latency 关闭的显式 PRE 必须同时满足。时间戳、AL、CWL、nRAS/nRTP/nWR 均以 CK 周期计；BL 是传输次数，BL8 占 4 CK：

```text
PRE >= max(tACT+nRAS, tRD+AL+nRTP, tWR_command+WL+BL/2+nWR)
WL = AL + CWL
```

若 `AL=0, CWL=9, nWR=12, WR@0`，写恢复参考沿为 `13`，PRE 不早于 `25`；仍须满足 `tACT+nRAS` 及其他约束。没有 RD 或 WR 时忽略对应项；同一打开行有多次命令时取各命令约束的最大值。模式、burst 长度、CRC 和参考沿由目标规格决定。详见 [完整推导](../../03-dram/protocols/timing-parameters-trcd-trp-tras.md#ddr4-同-bank-显式-pre-的完整下界)。

refresh 则可以脑内记成：

```text
REF --tRFC--> normal requests can fully resume
```

## 它们分别更影响谁

如果你的请求主要是：

- `row miss`：AL=0 时更敏感 `tRCD + RL`
- `row conflict`：AL=0 时更敏感 `tRP + tRCD + RL`
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

如果要再细一点，在本页所述 PL=0 且 CS-to-CA latency 关闭的模式下，至少把下面这些 guard 保留下来：

```text
external RD/WR + AL >= ACT + nRCD  # 同时检查其他命令规则
RD -> nominal first data after RL=AL+CL; check AC timing window
ACT -> PRE guarded by tRAS
PRE -> next ACT guarded by tRP
PRE guarded by max(ACT+nRAS, each RD+AL+nRTP, each WR+WL+BL/2+nWR)
REF blocks service for tRFC
```

只要这些约束还在，模型就还能表达 DRAM 访问成本为什么是分层的；一旦全被折成一个统一 latency，很多后续结论都会失真。
