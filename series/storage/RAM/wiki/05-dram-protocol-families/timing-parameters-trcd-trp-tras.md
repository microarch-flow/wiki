# 关键 timing 参数：tRCD、tRP、tRAS、tCL 的物理来源

上级：[DRAM 协议层](./README.md)
相关：[ACT、RD、WR、PRE：DRAM 命令集为什么长这样](./commands-act-rd-wr-pre.md), [刷新：DRAM 的原罪和它的代价](../04-dram-foundations/refresh-the-fundamental-cost.md)

## 这页在回答什么问题

为什么 DRAM 协议里会有一大串看起来像“神秘常数”的 timing 参数，以及这些参数各自在等什么物理过程完成。更具体地说，tRCD、tRP、tRAS、tCL 不是随便规定的空档，而是 cell、位线、sense amp 和 I/O 路径必须拿到的时间预算。

## 命令时序对应的物理等待

第一次看 DRAM 规格书时，很多人会把 timing 参数当成一种不透明的背诵负担：`tRCD`、`tRP`、`tRAS`、`CL`、`tRFC`、`tWR`，好像只是标准委员会写出来的一串数字。这样记当然能在表层上区分不同颗粒，但你很难据此形成判断。真正有用的理解方式是反过来看：每一个 timing 参数，其实都在回答一个问题，”在前一个物理动作完成到足够安全之前，后一个动作最早什么时候可以开始”。就像烤箱食谱上写”预热 10 分钟再放入食物”——这不是厨师的强迫症，而是如果你不等烤箱热透就放进去，蛋糕会塌。DRAM 的 timing 参数就是这样一本”食谱”，每一条都在说”等这个物理过程稳定之后，你才能做下一步”。

上一页已经把 DRAM 命令集拆成了 `ACT -> RD/WR -> PRE` 这条显式路径。现在只需要再多问一步：为什么这些命令之间不能立刻无缝连着发？答案就是，底层阵列和 I/O 并不是理想瞬时资源。开行后，位线上的微弱差分需要时间被 sense amp 放大并稳定；读出结果从 row buffer 到 I/O 还要穿过列路径和外部接口；一行被使用过后，位线和 cell 侧也需要时间恢复到可再次切换的状态。timing 参数就是这些等待条件的协议化名字。

## 开行、列访问与首数据

先看 `tRCD`，也就是 row-to-column delay。它约束的是从 `ACT` 到器件内部执行 `RD` 或 `WR` 之间的最短时间。DDR4 配置 additive latency（AL）时，外部列命令可先发出并在器件内部等待 AL；不能把外部命令沿与内部执行沿混为一谈。物理上，这段时间对应的是：wordline 被拉高后，cell 与位线开始 charge sharing，sense amp 开始识别并放大微弱差分，直到该行的数据在 row buffer 一侧足够稳定，可以安全接受列访问。也就是说，`tRCD` 不是”控制器慢一点再发命令”的人工保守量，而是在等”这一整行真的已经被打开并可用了”。就像你从密集书库里推出一整面书架后，得等书架完全停稳、档位卡好，才能伸手去拿书——不等稳就拿，书架可能还在晃，你抓到的可能是错的那本。

再看 `CL`，也就是 CAS latency。以下 DDR4 简式以外部 RD 采样沿为起点，假设关闭 CA parity（`PL=0`）和 CS-to-CA latency：首数据的名义读延迟为 `RL = AL + CL` 个 CK 周期；在此模式下 `AL=0` 才有 `RL=CL`。对于 [Alliance Memory AS4C512M8D4A 数据手册](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_4Gb_DDR4_AS4C512M8D4A-75BCN_75BIN_Aug2022_Ver1.0.pdf)所列 CA parity 模式，表 29 注 3 给出 `RL=AL+CL+PL`、`WL=AL+CWL+PL`。其 Burst Read 示例关闭 CS-to-CA latency，设置 `AL=0, CL=11, PL=4`，因此外部 RD 到首数据为 15 CK。实际数据有效窗口还须检查 AC 时序。

CL 不是 row 打开时间，而是列路径和 I/O 启动相关的参数。不同命令的 guard 必须按所选器件和模式分别推导；不能机械地给所有命令间隔都加 PL。开启 CS-to-CA latency 时也要按手册定义对应采样沿与时序。

## 行保持与预充

`tRAS` 是同一 bank 的 `ACT -> PRE` 最小间隔。它约束该行自激活起至少保持打开多久；即使 ACT 后没有 RD 或 WR，也必须满足。开行后的感测和恢复是这一限制的物理背景，但 `tRAS` 不保证近期列操作已经完成。每条 RD 和 WR 还会分别给 PRE 施加其他下界；控制器必须取所有下界的最大值。

`tRP`，也就是 row precharge time，则约束从发出 `PRE` 到这个 bank 真正能再次接受下一次 `ACT` 之间必须等待多久。物理上它对应的是：当前 open row 被释放后，位线要重新回到预充平衡状态，sense amp 和相关阵列路径也要复位到下一次感测的初始条件。如果你在 `PRE` 后立刻对同一个 bank 发下一个 `ACT`，新一行会在旧状态还没真正清空时接入阵列，感测条件就会不正确。因此 `tRP` 本质上是在等 bank 从“刚用过一行”恢复成“可安全开新行”的中性状态。

把这几个最关键的参数串起来。以下示意的外部命令时间假设 `AL=0`、CA parity 关闭（`PL=0`）且 CS-to-CA latency 关闭：

```text
ACT ---- wait tRCD ---- RD ---- first data after RL=AL+CL -----
 |-------------------- row stays active --------------------|
                must satisfy at least tRAS
PRE ---- wait tRP ---- next ACT
```

这个图想表达的核心不是具体数值，而是等待窗口各自对应哪段过程：`tRCD` 在等“开行后能列访问”，`RL=AL+CL` 描述外部 RD 后首个数据的名义时刻，`tRAS` 在等“这一行活得足够久以完成恢复”，`tRP` 在等“关行后重新预充好可以换下一行”。

## 写恢复与参数适用条件

如果再看写路径，会发现很多参数的直觉也类似。写操作不仅需要列路径把数据送入 row buffer，还需要给 cell 留够时间完成写回和恢复，因此又会出现 `tWR` 这类 write recovery 相关约束；refresh 则会引入 `tRFC` 这类更长的不可服务窗口，因为那不是单个请求的路径，而是整个刷新操作在占用阵列资源。也就是说，DRAM 的 timing 表面上像一堆细碎符号，本质上都是在给不同物理阶段划边界。

这里必须强调一个常见误解：timing 参数并不是“同一颗 DRAM 的固定自然常数”，而是工艺、组织、代际和目标速率共同决定的安全窗口。你看到不同代 DDR 的参数变化，不应该只读成“新一代更快”或“数字更大更小”，而应该问：是阵列本体更快了，还是接口变快但内部等待预算并没同比缩小，还是某些约束因容量/密度增加反而变得更紧。后面你会看到，很多时候外部带宽提上去了，但某些绝对时间量级并没有按直觉等比例缩短，这正说明 DRAM 内部物理过程并不会因为 I/O 名义速率提高就自动同速提上去。

从系统视角看，理解 timing 参数最重要的价值，不是记住典型值，而是知道它们会怎样塑造访问成本结构。在同一 bank、相同接口和调度条件下，row hit 不需为本次访问再执行 PRE 和 ACT，通常减少该访问的命令路径成本。端到端延迟仍受排队、其他命令、数据总线和调度影响，不能保证每笔 row hit 都比每笔 row conflict 快。也就是说，timing 参数不是附属常量，而是 DRAM 访问非均匀性的定量边界。

所以，本页真正要建立的不是一份速查表，而是一种解释框架：每一个 timing 参数都应该能被翻译回某段物理等待。只要这层对应关系建立起来，后面看到 controller 调度、page policy 或不同 DRAM family 的时序差异时，你就能顺着“它在等哪段过程”往下判断，而不是停留在参数名本身。

## DDR4 同 bank 显式 PRE 的完整下界

下面是 DDR4、BL8、禁用写 CRC、正常时钟，且 CA parity 和 CS-to-CA latency 均关闭的例子（`PL=0`）。`tACT`、`tRD`、`tWR_command` 是命令采样时刻，单位为 CK 周期；`nRAS`、`nRTP`、`nWR` 是按目标器件规格得到的整数 CK 约束。该模式中 `WL = AL + CWL`；`BL` 是数据传输次数，DDR 在每个 CK 传两次，所以 BL8 占 4 CK。不存在某类命令时，忽略对应项。对同一打开行，自 ACT 以来的所有 RD 和 WR 都必须满足约束，不能只看 ACT 或只看最后一类命令。

将 BL8 表示在理想 DQS 半 CK 栅格上。设首个 transfer 的名义时刻为 `t0`，则第 `k` 次为 `t0+k/2`（`k=0..7`），末次为 `t0+3.5`，八个时隙的右开占用窗口为 `[t0, t0+4)`。右端点不是末次 transfer 的时刻。读操作在上述模式下有 `t0=tRD+RL`；`RL=AL+CL` 使用当前模式的生效值。若输入是基础 CL，须先按目标器件的模式换算，例如检查 [Read DBI 的影响](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_AS4C512M16D4B_AS4C1G8D4B_8Gb_DDR4_Datasheet_Rev1.0_Sep2024.pdf#page=203)。该栅格是模型约定，不给出实际 DQS/DQ 相位、数据有效窗口或 CPU load 的完成与退休时刻。

```text
PRE_earliest = max(tACT + nRAS,
                   max_over_RD(tRD + AL + nRTP),
                   max_over_WR(tWR_command + WL + BL/2 + nWR))
```

其物理原因是：ACT 后要给行感测和恢复时间；RD 后要给列路径规定的读后恢复时间；WR 命令后，写数据要先经过 `WL` 并完成 burst，再留出写恢复时间。DDR4 的 `tWR` 参考沿不是 WR 命令沿。规范通常还会给出 ns 最小值、最小周期数及模式设置；要遵循目标器件对这些值、取整和边沿的定义。

**手算例子，仅为假设**：在上述 `PL=0`、CS-to-CA latency 关闭的模式下，`AL=0`、`CWL=9`、`BL=8`、`nWR=12`，WR 命令在周期 0。`WL=9`；按上述名义栅格，写数据的首、末 transfer 和右开窗口终点分别为 9、12.5、13。写恢复的参考沿在 `0+9+8/2=13`，因此显式 PRE 不早于周期 `13+12=25`。如果 `tACT+nRAS=28`，则还要等到 28。其他命令总线、bank、刷新、数据总线和模式约束也须满足。改变 parity、CS-to-CA latency、burst 或 CRC 时须查目标器件；auto-precharge 的内部触发也不等于显式 PRE 命令。

参考：[Micron 8Gb DDR4 数据手册](https://www.micron-electronic.com/pdf-80/mt40a1g8sa-075-h.pdf)，2017 Rev. M，WRITE Operation 第 239 页 Figure 188；[大学托管版本](https://classes.engineering.wustl.edu/permanant/cse260m/images/0/0c/8Gb_DDR4_SDRAM.pdf)也可供查阅。该资料明确区分写命令、数据结束后的参考沿和写恢复时间。模型实现见 [MC 记分板](../06-memory-controller/mc-modeling-for-simulation.md)。

## 一句话理解

tRCD、tRP、tRAS、tCL 这些参数不是标准里凭空冒出来的等待常数，而是在给 DRAM 的开行、感测、恢复、列访问和预充这些物理过程划安全边界。

## 建模启示

在建模里，这些 timing 参数最少应该被实现成命令间的 guard，而不是只折成一个“读延迟常数”。如果只用一个统一 latency，模型可以大致估算平均响应，却无法表达 row hit/miss/conflict 差异，更无法表达 controller 为什么要重排命令。

一个最小可用的 timing 表可以写成：

```text
DramTiming {
  nRCD: cycles  # tRCD 的器件规则换算为 CK
  CL, AL: cycles
  ca_parity_enabled: bool
  parity_latency_PL: cycles
  cs_to_ca_latency_mode: enum
  tRAS: cycle
  tRP: cycle
  nRTP, nWR: cycles
  CWL: cycles
  BL: transfers
  tRFC: cycle
}
```

对应 guard 形式在 CA parity 关闭（`PL=0`）且 CS-to-CA latency 关闭时可以写成：

```text
guard external_RD_or_WR only if now + AL >= act_cycle + nRCD
# 此式只表达内部列操作的 tRCD 下界；仍须检查命令总线和其他规则
guard PRE legal only if now >= pre_ready[bank]  # 包括 ACT、RD、WR 的约束
guard next_ACT legal only if now >= pre_cycle + tRP
schedule first_read_data at rd_command_cycle + AL + CL  # PL=0；另检查 AC 窗口
```

如果只关心粗粒度性能，可以把这些 guard 折成三类代价：`row_hit_cost`、`row_miss_cost`、`row_conflict_cost`。但只要你要研究协议差异、controller 调度或 refresh 与普通请求的交互，最好显式保留 timing 表和命令级时间戳。因为很多“为什么这条请求不能现在发”的答案，根本不是队列里有没有空位，而是 timing guard 还没放行。
