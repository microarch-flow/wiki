# AXI Waveform Debug 方法

上级：[05 性能与调试](./README.md)

相关：[AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md)、[AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)、[Timeout、Fault 与 Hang 定位框架](./timeout-fault-hang-debug-framework.md)

## 这页在回答什么问题

打开 AXI 波形就像面对一台**五个屏幕的安防监控**——如果你在五个画面之间来回扫，很快就会头晕眼花。正确的做法是：先确认你要查的是"有人进来没出去"（读路径）还是"有东西送进去没收到回执"（写路径），然后找到**第一个画面停止变化的时间点**，最后沿着依赖链上下游各看一跳。

这页给出一个可执行顺序：分读写、找握手、闭环 transaction、看 ID/outstanding、解释 response、把波形翻译成系统语言。就像交通事故调查：先分车道，再找第一辆停下来的车，然后看它前面和后面分别发生了什么。

## 第一步：先分读路径和写路径

AXI 读写通道解耦，读问题和写问题的闭环不同。

| 问题类型 | 重点通道 | 闭环条件 |
| --- | --- | --- |
| read | `AR` -> `R` | `ARVALID && ARREADY` 后，所有 `R` beat 返回并看到 `RLAST` |
| write | `AW` + `W` -> `B` | 地址和全部写数据被接收后，`BVALID && BREADY` 完成 |
| write data stall | `W` | `WVALID && !WREADY` 或 W beat 与 AW 配对异常 |
| write response missing | `AW/W/B` | AW/W 已闭合，但 B 不返回 |
| read response missing | `AR/R` | AR 已闭合，但 R 不返回 |

不要先看五条通道的所有细节。先确认当前故障是 read completion 失败、write completion 失败、还是某条 channel 的 handshake 未发生。

## 第二步：只相信握手

AXI 的黄金法则：**只有两只手同时伸出来的那一刻，东西才算交出去了**。`VALID` 是递东西的人举手（"我这边好了"），`READY` 是接东西的人举手（"我能接"）。只看到一边举手，不代表交接发生了。

| 波形现象 | 不能直接得出的结论 | 更准确的判断 |
| --- | --- | --- |
| `READY=1` 但 `VALID=0` | sink 没问题 | source 没发，可能被更前面的 slot/outstanding 限制 |
| `VALID=1` 但 `READY=0` | source 错误 | sink 或下游路径反压 |
| `VALID&&READY` 一次 | 完整事务完成 | 地址握手只是开始，response 才闭环 |
| `RVALID=1` 但 `RREADY=0` | slave 慢 | master/return path 接收侧在反压 |
| `BVALID=0` | 写没发生 | 需要先确认 AW 和全部 W beat 是否已被接收 |

第一轮波形标注建议只标 `*_fire = VALID && READY`，避免被持续高电平误导。

## 第三步：读路径检查

读路径从 AR handshake 开始，到最后一个 R beat 完成。

| 检查点 | 要看什么 | 结论 |
| --- | --- | --- |
| AR fire | `ARVALID && ARREADY` 是否发生 | 未发生则 request 未进入下游 |
| AR payload | `ARADDR/ARLEN/ARSIZE/ARBURST/ARID` | 地址、burst、ID 是否符合预期 |
| outstanding | AR fire 后对应 ID 是否占 slot | slot 满会阻止后续 AR |
| R first beat | `RVALID && RREADY` 是否出现 | 不出现则看 slave/controller/return path |
| R beats count | beat 数是否等于 `ARLEN+1` | 少 beat 是协议或桥接问题 |
| RLAST | 最后一 beat 是否带 `RLAST` | 无 RLAST 则 transaction 未闭环 |
| RRESP | 是否 OKAY/SLVERR/DECERR 等 | 错误要追 fault source |

若 `AR` 已 fire 但 `R` 不来，不要只盯 R channel。要向下游看 slave 是否收到 request、bridge 是否发出子事务、DDR/controller 是否返回数据、return FIFO 是否被反压。

## 第四步：写路径检查

写路径要同时看 AW、W 和 B。AXI 允许 AW 和 W 独立到达，不能假设地址先于数据或两者同周期。

| 检查点 | 要看什么 | 结论 |
| --- | --- | --- |
| AW fire | `AWVALID && AWREADY` 是否发生 | 写地址是否进入下游 |
| W fire | 每个 `WVALID && WREADY` beat 是否发生 | 写数据是否完整进入下游 |
| WLAST | 最后一 beat 是否带 `WLAST` | 无 WLAST 则写数据未闭环 |
| AW/W 配对 | 地址长度与 W beat 数是否匹配 | mismatch 会导致 bridge/slave 等待 |
| WSTRB | byte lane 是否符合访问 | partial write/MMIO side effect 风险 |
| B fire | `BVALID && BREADY` 是否发生 | 写事务完成 |
| BRESP | response 是否 OKAY 或错误 | 错误要追 slave/bridge/decoder |

若 `BVALID` 不来，先确认 AW 已 fire、所有 W beat 已 fire、WLAST 正确。若 AW/W 都已完成但 B 不来，再看 slave 是否生成 response、bridge 是否聚合子事务、return path 是否反压。

## 第五步：ID、Outstanding 与 Ordering

AXI 的难点不是单笔事务，而是多笔 outstanding 的匹配。

| 观察 | 解释 |
| --- | --- |
| 同 ID 多笔读返回顺序固定 | 受同 ID ordering 约束 |
| 不同 ID read data 交错 | 合法，但 master 必须按 RID 匹配 |
| outstanding 达上限后 AR/AW 停止 | source 可能没发，不是 sink 阻塞 |
| 某个 ID response 不回 | 该 ID slot 泄漏或下游事务未闭环 |
| bridge 改写 ID | 需要看内部 remap slot 和 response 匹配 |

调试时要维护一个小表：每次 AR/AW fire 记录 ID、地址、长度、时间；每次 RLAST/B fire 删除对应项。表里长期不消失的 entry，就是下一步追踪对象。

## 第六步：把波形翻译成系统语言

波形结论停留在”READY 低”就像事故报告写”车停了”——没有任何诊断价值。你需要翻译成**人话**：为什么停了、被什么卡住了、影响了谁。

| 波形结论 | 系统语言 |
| --- | --- |
| `ARVALID && !ARREADY` | read request 入口被反压，可能是 queue/slot/full |
| AR fire 后无 R | request 已进入下游，但 response path 或 slave 未闭环 |
| RVALID 有空洞 | DDR row conflict、turnaround、return arbiter 或 RREADY 反压 |
| AW/W fire 后无 B | write response 未生成或未返回 |
| WVALID 长期等 WREADY | write data path 或 width/bridge 下游拥塞 |
| RRESP/BRESP 错误 | fault/error path 已闭环，追错误源 |

这一步把 waveform debug 和系统 debug 连接起来。否则波形只能说明某个信号变化，不能解释为什么软件看到 timeout、fault 或 hang。

## 例子：Read Hang

| 阶段 | 波形观察 | 判断 |
| --- | --- | --- |
| T0 | `ARVALID && ARREADY`，记录 `ARID=3` | request 已接受 |
| T1 | 之后没有 `RID=3` 的 R beat | response missing |
| T2 | 下游 slave 侧也看到 request fire | interconnect 已转发 |
| T3 | slave 内部 busy，未产生 response | slave/controller 是 no-progress 点 |
| T4 | fabric timeout 后返回 `RRESP=SLVERR` | hang 被 timeout 包装成 fault/timeout |

若 T4 不发生，软件会看到 read hang；若 T4 发生，软件看到的是错误或异常。根因可能相同，观察入口不同。

## 例子：Write Response Missing

| 阶段 | 波形观察 | 判断 |
| --- | --- | --- |
| T0 | AW fire，`AWLEN=3` | 需要 4 个 W beat |
| T1 | 只看到 3 个 W fire，没有 WLAST | 写数据未完整到达 |
| T2 | BVALID 不出现 | slave 等待完整 write data |
| T3 | master WVALID 停止 | source 侧数据生成或内部状态机卡住 |

这个例子里问题不在 B channel。B 不返回是结果，真正 no-progress 点在 W data 生产。

## 常见误区

| 误区 | 更准确的判断 |
| --- | --- |
| READY 低就是接收方 bug | READY 低可能是合法 backpressure，要追下游原因 |
| READY 高就说明路径空闲 | source 可能因 outstanding、ordering 或上游状态没发 |
| 地址握手完成代表事务完成 | 读要等 RLAST，写要等 B response |
| R/B 没回来就只看返回通道 | 也要确认下游是否收到 request、是否生成 response |
| 不同 ID 返回乱序就是错误 | 不同 ID 允许交错，关键是 RID/BID 匹配和同 ID 约束 |

## 一句话理解

AXI 波形调试要按 `分读写 -> 标握手 -> 闭环 transaction -> 查 ID/outstanding -> 翻译成系统状态` 的顺序推进。

## 建模启示

AXI waveform debug 的模型核心是 transaction ledger。每次 `AR/AW/W/R/B` handshake 都要变成 ledger 事件：request 进入、data beat 进入、response 返回、slot 释放。性能模型要记录每笔 transaction 的 wait、service、response latency 和 outstanding age。功能模型要记录 ID 匹配、burst beat count、WLAST/RLAST、WSTRB、RRESP/BRESP 和错误映射。

事件模型建议显式表达 `ar_fire`、`aw_fire`、`w_fire`、`wlast_seen`、`r_fire`、`rlast_seen`、`b_fire`、`id_slot_allocate`、`id_slot_release`、`response_error_seen`、`forward_progress_lost`。这些事件能把波形从信号变化转成可复盘的 transaction 状态。
