# DRAM 时序：从命令采样到读写恢复

上级：<span id="关键-timing-参数trcdtrptrastcl-的物理来源"></span>[DRAM 命令与接口](./README.md)

相关：[ACT、RD、WR、PRE](./commands-act-rd-wr-pre.md) · [刷新](../foundations/refresh-the-fundamental-cost.md) · [控制器模型](../../04-dram-controller/mc-modeling-for-simulation.md)

## 这页在回答什么问题

`tRCD`、`tRP`、`tRAS`、`CL` 等约束分别限制哪些事件？如何在明确器件模式的前提下计算命令的最早时间？

## 关键 timing 参数：tRCD、tRP、tRAS、tCL 的物理来源 {#命令时序对应的物理等待}

阵列感测、恢复和预充需要时间，列路径及 I/O 也有各自延迟。参数是接口规定的边界，不是可以任意组合的固定访问延迟。每一项都要核对起点、终点、单位、适用命令和模式。

## 开行、列访问与首数据

`tRCD` 约束 ACT 到内部列操作的最短间隔。DDR4 配置 additive latency（AL）时，外部 RD/WR 先被采样，内部列操作再延后 AL；关闭 CA parity 与 CS-to-CA latency 时，其 `tRCD` 条件为 `tRD + AL ≥ tACT + nRCD`，仍须检查其他规则。

同一简化模式下，以外部 RD 采样沿为起点，名义读延迟 `RL = AL + CL`。只有 `AL = 0` 时 `RL = CL`。[Alliance AS4C512M8D4A 数据手册](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_4Gb_DDR4_AS4C512M8D4A-75BCN_75BIN_Aug2022_Ver1.0.pdf)的特定 CA parity 模式还定义 `RL = AL + CL + PL` 和 `WL = AL + CWL + PL`。例如关闭 CS-to-CA latency，取 `AL = 0、CL = 11、PL = 4`，名义 RL 为 15 CK。实际 DQ 有效窗口仍须检查 AC 时序，不能把 PL 机械加到所有命令规则。

## 行保持与预充

`tRAS` 限制同一 bank 的 ACT 到 PRE 最短间隔，即使其间没有列命令也适用；它本身不保证最近一次读写已恢复。`tRP` 限制 PRE 到该 bank 下次 ACT 的间隔。还要单独检查 `tRC` 等其他约束。不同等待可能重叠，因此不能一律相加。

## 写恢复与参数适用条件

写恢复从器件规定的数据参考沿计算，不是从 WR 命令沿直接计算。规格可能同时给出 ns 与最小周期数：按相应模式和手册规则，常见换算形式为 `n = max(n_min, ceil(t_min / tCK))`。检查有效 CL、CWL、AL、burst、CRC 和其他模式；例如 [Alliance 数据手册](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_AS4C512M16D4B_AS4C1G8D4B_8Gb_DDR4_Datasheet_Rev1.0_Sep2024.pdf#page=203)描述了读 DBI 的影响。

## DDR4 显式 PRE 的三类下界 {#ddr4-同-bank-显式-pre-的完整下界}

以下只计算所列三类约束的共同下界，不能替代完整协议检查。假设 DDR4、BL8、写 CRC 关闭、正常时钟，CA parity 和 CS-to-CA latency 均关闭。命令时刻和 `nRAS、nRTP、nWR` 均以 CK 计；`WL = AL + CWL`。对该打开行自 ACT 以来的全部读写，取：

<div class="ram-calculation" markdown>
**PRE 最早时刻** = max（`tACT + nRAS`，各 `tRD + AL + nRTP`，各 `tWR_command + WL + BL/2 + nWR`）
</div>

不存在某类列命令时忽略对应项。这里 `BL/2` 是 DDR 数据传输占用的 CK 数。假设 `AL = 0、CWL = 9、BL = 8、nWR = 12`，WR 在周期 0：名义首 transfer 在 9，末 transfer 在 12.5，右开数据窗口为 `[9, 13)`；写恢复参考沿为 13，所以该约束要求 PRE 不早于 25。若 ACT 的 `tACT + nRAS = 28`，还要等到 28。末次 transfer 与窗口右端不是同一时刻。

这个半 CK 栅格只是时序计算约定，不给出实际 DQ/DQS 有效窗口。[Micron 8Gb DDR4 数据手册](https://www.micron-electronic.com/pdf-80/mt40a1g8sa-075-h.pdf)的 WRITE Operation、Figure 188 区分了写命令、数据和恢复参考沿；另有[大学托管版本](https://classes.engineering.wustl.edu/permanant/cse260m/images/0/0c/8Gb_DDR4_SDRAM.pdf)。还必须检查总线、刷新、其他 bank 及所选模式；auto-precharge 的内部触发不同于显式 PRE。

## 一句话理解

时序参数约束特定事件之间的距离；计算一条命令时，要同时满足所有适用下界。

## 建模启示

保存命令采样时间、内部执行偏移、读写数据窗口以及每 bank 的最早可用时间。分别校验共享总线和跨 bank 约束，避免把行命中成本当作所有请求的端到端延迟。
