# DRAM 时序参数速查

<span id="dram-timing-参数速查"></span>

上级：[参考资料与工具](./README.md)
相关：[时序参数的物理来源与完整推导](../../03-dram/protocols/commands-act-rd-wr-pre.md#命令时序对应的物理等待) · [DRAM 命令](../../03-dram/protocols/commands-act-rd-wr-pre.md)

## 这页在回答什么问题

原“DRAM timing 参数速查”用于查找命令约束的参考动作和作用范围。此页不提供通用参数值：先确定器件、协议代际、速率、温度、模式和单位，再查该器件手册。不同模式可能修改参考沿或引入额外限制。

## 按参考动作查找时序约束

下表中的外部命令简式以 DDR4 的 CA parity 关闭（PL=0）、CS-to-CA latency 关闭为前提。AL 表示 additive latency。CK 表示时钟周期，不能与传输次数或纳秒混用。

## 核心参数

| 参数 | 主要约束与参考动作 | 适用范围或注意事项 |
| --- | --- | --- |
| tRCD | ACT 到内部 RD/WR 的最小间隔 | 外部列命令可提前 AL；还须满足其他规则。 |
| CL / RL | 读命令到首数据的名义周期数 | 本页模式 RL = AL + CL；AC 数据有效窗口另按手册检查。 |
| tRAS | ACT 到同 bank 显式 PRE 的最小间隔 | 即使没有列命令，也须满足。 |
| tRP | PRE 到同 bank 下一次 ACT 的最小间隔 | 行切换还须考虑 tRC 等限制。 |
| tRC | 同 bank 两次 ACT 的最小间隔 | 与 PRE、tRAS、tRP 等约束一起检查。 |
| tRTP | 读后到 PRE 的约束 | 本页模式为每条外部 RD + AL + nRTP；并非首数据返回时刻。 |
| tWR | 写数据后的恢复时间 | 起点是器件规定的数据参考沿，不是 WR 命令沿。 |
| tCCD_L / tCCD_S | 同 rank 连续同向列命令最小间隔 | DDR4 同 bank group 与跨组分别检查；读写反向还受转换约束。 |
| tRRD_L / tRRD_S | 同 rank 不同 bank 的相邻 ACT 间隔 | 同组与跨组分别检查；同 bank 另查 tRC。 |
| tFAW | 同 rank 滚动窗口内最多四次 ACT | 第五次不早于最早一次 ACT + tFAW，并同时满足 tRRD。 |
| tBURST | burst 的数据传输持续时间 | DDR4 BL8 占 4 CK；不同协议及模式以手册为准。 |
| tRFC | 指定刷新命令后的恢复间隔 | 刷新范围及恢复时间依命令、模式和器件而变。 |
| tREFI | 对应刷新模式的平均刷新间隔 | 延后或提前有协议和器件规定的限制；温度和刷新模式可能改变要求。 |
| tWTR | 写到读的转换限制 | 同时核对数据参考沿、bank group、rank 和其他总线约束。 |

## 先记哪几条最重要

先分清 ACT→列访问、ACT→PRE、PRE→下一次 ACT、读或写→PRE、刷新→恢复。每一段都有自己的起点和作用域。特别是写恢复从数据参考沿计算，不能直接把 nWR 加到 WR 命令时刻。

## 把它们串成脑内时序

在 AL=0、PL=0、CS-to-CA latency 关闭的 DDR4 模式下，ACT 后至少等待 tRCD 才能发出受该约束的列命令；显式 PRE 还受 ACT、各次读写以及其他规则共同约束。下式只展示 BL8、无写 CRC 模式下的主要同 bank 下界；缺失的 RD 或 WR 项省略，多次命令逐条取最大值。

<div class="ram-calculation" markdown>
**PRE 不早于** max（ACT 时刻 + nRAS，所有 RD 时刻 + AL + nRTP，所有 WR 时刻 + WL + BL / 2 + nWR）

**WL** = AL + CWL
</div>

所有时间戳、AL、CWL、nRAS、nRTP 和 nWR 使用 CK；BL 是传输次数。例如 AL=0、CWL=9、nWR=12，WR 在周期 0，则 WL=9，写恢复参考沿为周期 13，写约束要求 PRE 不早于周期 25。若 ACT+nRAS 或其他限制更晚，应取更晚时刻。这个例子不是器件的通用时序值。详细条件和数据手册见[完整推导](../../03-dram/protocols/commands-act-rd-wr-pre.md#ddr4-同-bank-显式-pre-的完整下界)。

[Alliance Memory DDR4 手册](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_4Gb_DDR4_AS4C512M8D4A-75BCN_75BIN_Aug2022_Ver1.0.pdf)同时给出 CA parity 模式下包含 PL 的 RL/WL；不能将本页 PL=0 简式直接用于其他模式。

## 它们分别更影响谁

行未打开时，tRCD 影响首个列访问；行冲突还涉及 PRE 与下一次 ACT。密集跨 bank 激活要检查 tRRD 和 tFAW。刷新对哪些请求造成阻塞，取决于命令覆盖范围、状态和流量。

## 不该怎么记

不要把器件数据率当作内部阵列时钟，也不要把 row hit、closed-row miss 和 row conflict 的实际延迟简化成彼此固定的数字。排队、命令时序及总线竞争都可能改变结果。刷新也不总是整个器件同时不可用；例如 AMD 的控制器区分 [LPDDR5/5X all-bank 和 per-bank 刷新](https://docs.amd.com/r/en-US/pg456-integrated-mc/LPDDR5/5X-Refresh-Options)，具体支持范围以实现为准。

## 一句话理解

时序参数规定动作之间的限制；正确使用必须同时确定参考沿、单位、作用域与模式。

## 建模启示

需要比较命令调度时，记录各 bank 状态、每条相关命令的时刻、刷新覆盖范围及共享命令和数据通路的预留。所有适用的 guard 同时成立才可发命令；简化平均延迟模型不能独立证明命令轨迹合法。
