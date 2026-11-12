# 第三轮：有限资源的接纳与事件时间

建议先独立完成[原始题面](./cases.md)，再看本页的结果和推导。题面有 9 个确定用例：SRAM 的 S1–S3、DRAM 的 D1–D4、NoC 的 N1–N2；还有 3 个信息不足的小问 SU、DU、NU。

独立读者在第二轮基线 `84e459a` 阅读正文并冻结答案。九个确定用例的所有记录与两份独立参考结果逐字段一致。三个欠定小问均给出缺失条件和可区分的实现。这是修订正文前的盲测结果；本轮后续补充了 NoC credit 和 DRAM 理想数据时间边界的说明。

## 怎么复现

从仓库根目录运行，仅使用 Python 标准库。`--check` 和 `-O` 下的比较已在 Python 3.9.6、3.12.14 验证：

```sh
python3 docs/reviews/round-3/model.py --check
python3 docs/reviews/round-3/model.py --case N1
python3 docs/reviews/round-3/model.py --case N2
python3 docs/reviews/round-3/model.py --waits
python3 docs/reviews/round-3/model.py --expand-dram D4
```

默认不带参数也执行 `--check`。它把状态推进模型的输出与[独立参考数据](./expected.json)逐字段比较；不写入文件。差异会报告用例、拍号及字段。`--case` 可查看单个用例的完整结果，N1、N2 包含每拍快照。`--waits` 给出 SRAM 的等待原因。`--expand-dram` 包含 t=0 起至目标读窗口右开终点之前的每个整数 CK，`cmd: null` 表示当拍没有目标命令，`data_transfer_half` 是该 CK 内目标读的半 CK 传输沿；历史写数据不在展开输出中。

### 题设与正文各提供什么

- **题设**固定了请求、地址、端口数、II、读延迟、DDR4 的模式和 timing、NoC 容量及事件相位，还规定资源合格时立即发送或接纳。它保证 DRAM 其他命令、DQ、刷新与调度约束已满足。这些数值是教学配置。
- **正文**提供机制：SRAM 的 bank 与物理端口、II 与读延迟的区别；DRAM 行状态与 PRE/ACT/RD 的时序下界；NoC 的 slot credit、在途状态和按快照推进的规则。见 [SRAM 端口](../../../series/storage/RAM/wiki/02-sram-foundations/single-port-dual-port-multi-port.md)、[DRAM timing](../../../series/storage/RAM/wiki/05-dram-protocol-families/timing-parameters-trcd-trp-tras.md)、[NoC credit](../../../series/interconnect/NOC/wiki/02-router-microarchitecture/credit-based-flow-control.md)及[逐拍伪代码](../../../series/interconnect/NOC/wiki/08-simulator-construction/router-pipeline-pseudocode.md)。
- **题面记号的解释**：此处 `CL=14` 表示当前模式实际生效的 CAS 延迟，因 `AL=PL=0`，有效读延迟为 14 CK。若把 14 当成启用 Read DBI 前的基础值，还要给出模式及相应修正。题面没有声明器件料号、频率或 speed bin。[AMD PG201 的 CAS Latency 选项](https://docs.amd.com/r/3.4-English/pg201-zynq-ultrascale-plus-processing-system/DDR-Memory-Options)举例说明控制器如何处理 DBI 修正。

## 结果和触发条件

### SRAM

`bank = floor(byte_address / 4) mod 2`。A 和原始 B 在 bank 1，C 在 bank 0；S2 的 B 改到 bank 0。接纳后同一 bank 最早在 `accept + II` 再接纳，结果在 `accept + 3` 就绪。

| 用例 | A、B、C 接纳拍 | A、B、C 就绪拍 | 原因 |
|---|---|---|---|
| S1 | 0、1、1 | 3、4、4 | t=0，A 和 B 争用 bank 1，A 先接纳。t=1，B 和 C 使用不同 bank。 |
| S2 | 0、0、1 | 3、3、4 | A、B 在不同 bank；bank 0 的 II=1，C 在 t=1 可接纳。 |
| S3 | 0、2、1 | 3、5、4 | B 先输给 A；bank 1 的 II=2 又使 B 在 t=1 继续等待。 |

### DRAM

命令时刻用 CK。数据首沿、末沿和窗口右开终点也用 CK；机器数据将它们乘以 2，因而可以用整数表达半 CK。历史命令不计入目标命令列表。

| 用例 | 目标命令 | 首沿 / 末沿 / 右开终点 | 触发条件 |
|---|---|---|---|
| D1 | RD@0 | 14 / 17.5 / 18 | 目标行已打开，满足列命令下界。 |
| D2 | ACT@0，RD@14 | 28 / 31.5 / 32 | bank 已关闭且预充完成，先 ACT，再等 nRCD。 |
| D3 | PRE@0，ACT@14，RD@28 | 42 / 45.5 / 46 | 另一行已开，且 t=0 时已满足关闭行的下界。 |
| D4 | PRE@18，ACT@32，RD@46 | 60 / 63.5 / 64 | 历史 WR 的数据与写恢复仍然有效，延迟了 PRE。 |

D4 中，RAS 给出 `-40 + 35 = -5`；写恢复给出 `-8 + WL(10) + BL/2(4) + nWR(12) = 18`。因此 `PRE = max(0, -5, 18) = 18`。随后等 14 CK 发 ACT，再等 14 CK 发 RD。每个读数据窗口有八个理想传输沿，相邻半 CK；末沿与右开终点相差半 CK。[Alliance Memory DDR4 数据手册：读数据时隙](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_AS4C512M16D4B_AS4C1G8D4B_8Gb_DDR4_Datasheet_Rev1.0_Sep2024.pdf#page=200)、[写恢复与显式 PRE](https://www.alliancememory.com/wp-content/uploads/AllianceMemory_AS4C512M16D4B_AS4C1G8D4B_8Gb_DDR4_Datasheet_Rev1.0_Sep2024.pdf#page=223)

### NoC

四个状态量都在拍初 `S(t)` 观察。先依 `S(t)` 决定发送和移除，再在拍末提交到期的正向和反向事件。第 t 拍末返回的 credit，最早在下一拍拍初参与发送判定。

| 用例 | F0–F3 发送拍 | F0–F3 移除拍 | 首个全部信用归还的静止快照 |
|---|---|---|---|
| N1，Lr=1 | 0、1、7、8 | 5、6、10、11 | S(13) |
| N2，Lr=3 | 0、1、9、10 | 5、6、12、13 | S(17) |

例如 N2 的 S(7) 为 `credit=0, forward=0, fifo=0, reverse=2`。下游 FIFO 虽有两个物理空槽，两个返还信用还在途中，源端不能发送。该单跳单 VC 模型满足 `B = credit + forward + fifo + reverse`。slot credit 表示逐跳槽位授权；它既不是端到端完成确认，也不等于新包的 VC 分配许可。[Concer 等，NoC buffer 流控](https://sld.cs.columbia.edu/pubs/concer_codesIsss08.pdf#page=3)

### 三个条件不足的小问

- **SU：**仅有 1R1W 端口类型，不能确定同沿同址读写是否都被接纳，也不能确定读值。例子：将共时钟双口 UltraRAM 的 A、B 分别固定为读口和写口，并允许两笔并发；宏在同周期内先执行 A，读到旧值 `0x11`。交换接线，A 写、B 读，则读到新值 `0x22`。这是该宏的规定，不是所有 1R1W 宏的通则。[AMD UG573，UltraRAM 端口操作](https://docs.amd.com/r/en-US/ug573-ultrascale-memory-resources/Dual-Port-SRAM-Array-Operations?contentId=75bb_vGII_~YqW0kPU2_bg) 另可构造同址写优先的接口，只接纳写请求。具体宏的跨口碰撞也可能不保证读值；例如 [AMD Block RAM 的碰撞表](https://docs.amd.com/r/en-US/ug573-ultrascale-memory-resources/Address-Collision?contentId=UQiiGZenETxer_8VR_ofYg)中，共时钟时写口为 WRITE_FIRST 的跨口读结果为 X。
- **DU：**外部数据传输时间不能唯一确定 CPU 指令退休。可构造两种同样在 D1 的 t=18 收齐数据的按序退休状态：load 在队头则 t=19 退休；若更老指令占用唯一退休端口到 t=25，则 load 可在 t=26 退休。时钟关系、返回路径、完成条件和 ROB 状态等都须另给。这里 19 和 26 是反例，不是题设结果。[BOOM，Commit Stage](https://docs.boom-core.org/en/latest/sections/reorder-buffer.html#the-commit-stage)
- **NU：**`credit=0` 和 FIFO 有空槽不足以确定下一发送拍。N1 和 N2 在 S(6) 的四项状态均为 `(0, 0, 1, 1)`，源端都等待 F2；N1 的 F2 在 t=7 发送，N2 在 t=9 发送。至少还要知道返还事件何时到达及何时可用于发送判定。

## 另三题的独立复读

第二位新读者只阅读正文，独立手算以下改变输入的三题；结果与事先另行写定的预期一致。这三题不属于脚本的九项对照，也不是硬件验证。表中未改变的相关调度和事件相位采用前述题设。

| 题 | 改变的输入 | 独立计算的检查值 |
|---|---|---|
| SRAM | 两个 1RW bank，4 B 交织，II=2，读延迟 1；A@0x14 在 t=0 到，B@0x1c、C@0x18 在 t=1 到。 | A/B/C 的接纳拍为 0/2/1，就绪拍为 1/3/2。 |
| DRAM | t=0 收到 X 的读请求；历史为 ACT(Y)@-30、RD(Y)@-3；nRAS/nRTP/nRP/nRCD 为 24/6/11/10，生效 CL=12，AL=PL=0。 | PRE@3、ACT@14、RD@24；首沿 36、末沿 39.5、右开终点 40 CK。 |
| NoC | 深度 1，正向延迟 1、返还延迟 2；两个同包 flit 已就绪，下游只要可以出队就移除。 | 发送拍 0/5，移除拍 2/7；全部信用在 S(10) 可用。 |

## 独立参考如何得到

`expected.json` 仅合并两份先于比较冻结的参考结果：一份涵盖 S1–S3 和 N1–N2，另一份涵盖 D1–D4。它没有从读者模型的输出生成。以下方法可以重新推导这些数据。

SRAM 参考按地址映射将请求分到各 bank，按到达时间与 ID 仲裁，并跟踪每个 bank 的下一可接纳拍；将每次接纳拍加 3 得到就绪拍。将两类事件分别填入从 t=0 到最后一个就绪拍的列表。

NoC 参考先计算每个 flit 的发送、可见、移除和信用重新可用时间，再按事件计数展开。令 `s[i]` 是发送拍，`e[i]` 是 FIFO 首次在拍初可见的拍，`p[i]` 是移除拍，`r[i]` 是对应 credit 首次在拍初可用的拍。题设的两枚初始信用、顺序移除、固定 Lr 和连续拍返还管线使下列递推成立：

```text
s[0] = 0; s[1] = 1
s[i] = max(s[i-1] + 1, r[i-2])       i = 2, 3
e[i] = s[i] + 3
p[0] = max(5, e[0])
p[i] = max(5, e[i], p[i-1] + 1)      i = 1, 2, 3
r[i] = p[i] + Lr + 1
```

每个 t 从 0 枚举到 `r[3]`。令 `U`、`V`、`W`、`Z` 分别是满足 `s[i]<t`、`e[i]≤t`、`p[i]<t`、`r[i]≤t` 的 flit 数量，则拍初四项依次是 `2-U+Z`、`U-V`、`V-W`、`W-Z`。当 `s[i]=t` 记发送 Fi；当 `p[i]=t` 记移除 Fi。独立事件队列还对这些展开值做了复核。

DRAM 参考逐例比较 row 状态和各 timing 下界，再逐 CK 选择首个合法命令。D4 的写恢复计算如上；`RD=r` 时八次传输为 `r+14+j/2`，`j=0…7`，右开终点为 `r+18`。逐字段比较同时覆盖命令及数据时刻。

## 模型边界

脚本保留请求队列、bank 可用时刻、DRAM timing 记分板、NoC 正反向事件队列和 FIFO 的状态推进。它检查题内容量、顺序和时间不变量；比较使用显式条件，即使以 `python3 -O` 运行也不会跳过。结果只证明本题参数和边界下的模型与独立参考一致。

题设没有提供 SRAM 宏的实际碰撞契约，也没有完整 DDR4 器件配置、PHY 模拟采样、CPU 退休、NoC 其他流量或 VC 分配。这里没有验证实物、RTL、完整协议约束或性能。DRAM 的首沿、末沿和右开终点是理想外部接口事件，不是 CPU 退休时刻。
