# Memory Controller

上级：[`RAM/wiki/`](../)
相关：[DRAM 协议层](../05-dram-protocol-families/README.md), [系统视角](../07-system-architecture/README.md)

## 这页在回答什么问题

如果前两章已经把 DRAM 的物理约束和协议约束讲清，那么这一章要回答的就是：为什么同一套 DRAM 颗粒，在不同系统里会表现出完全不同的有效带宽、平均延迟和尾延迟。答案通常不在颗粒宣传参数本身，而在 memory controller 如何把那些底层债务翻译成调度、映射、仲裁和状态管理策略。

## 正文

很多人把 DRAM 看成“外面一排内存芯片，里面性能已经基本写死”，于是系统能做的似乎只剩下换更高代颗粒或多加几个 channel。这个看法最大的问题，是低估了 memory controller 在整套 DRAM 系统中的地位。到这里你已经知道，DRAM 不是一个近似固定延迟的黑盒，而是一个带显式命令、timing guard、open-row 状态、refresh deadline 和 bank 并行结构的状态机阵列。既然底层对象是状态机，系统真正的性能表现就不可能只由器件标称值决定，而一定高度依赖“谁在什么时刻发什么命令、让哪些请求先过、把哪些地址分到哪些 bank”。

换句话说，memory controller 是协议世界和系统世界之间的翻译层。就像一个机场的航班调度中心——飞机（DRAM 颗粒）的起降能力是固定的，跑道规则（协议 timing）也不能改，但航班调度（controller 策略）直接决定了每天能实际起降多少架次、哪些航班准点、哪些被延误。对上，它面对的是来自 CPU、DMA、GPU、NPU 或其他 master 的读写请求流；这些请求只知道自己要访问某个物理地址、希望尽快完成，并不会自带 row locality、bank 均衡或 refresh 友好性。对下，controller 面对的是一套并不宽容的 DRAM 状态机：某个 bank 当前是否 open，下一条命令是否合法，什么时候必须 refresh，读写切换会不会打断总线，哪些请求可以交错、哪些必须等待。这一上一下之间的张力，正是 controller 存在的全部意义。

这一章的结构会沿着 controller 真正要做的几类决策展开。`why-mc-is-the-real-bottleneck.md` 先把总判断立住：理论峰值只是上限，实际性能首先取决于 controller 如何利用 row locality、bank parallelism 和总线时间片。`command-scheduling-fr-fcfs.md` 进入最经典的调度核心，说明为什么 row-hit 优先策略能提高吞吐，又为什么它会天然伤害公平性。`page-policy-open-close-adaptive.md` 继续追问：一行打开后应不应该继续留着，controller 到底是在押注未来局部性还是在提前为下一次切换清场。

后面的 `refresh-management-distributed-postponed.md`、`write-buffer-write-drain.md`、`address-mapping-channel-rank-bank-row-col.md` 和 `qos-multi-master-arbitration.md`，则分别对应 controller 另外几类长期绕不过去的问题。refresh 不是背景噪声，而是要被调度的 deadline 事件；写请求不能无限和读请求一视同仁，因为总线方向切换有真实代价；地址映射不是位切分细节，而是 row locality 和 bank hotspot 的根源；多 master 仲裁更不是公平性口号，而是在吞吐、实时性和隔离性之间做硬选择。最后的 `mc-modeling-for-simulation.md` 会把这整章收束到建模视角，明确哪些状态与事件在 cycle-level 仿真里必须保留。

这章还有一个阅读边界需要先讲清。它讨论的是“如何在既定 DRAM family 与协议约束下调度和组织请求”，而不是重新定义 DRAM 协议本身。也就是说，这里默认 `ACT/RD/WR/PRE`、timing 参数、bank 结构等都已经存在；controller 的工作，是在这些既定规则下尽量把 workload 翻译成更少冲突、更高 row-hit-rate、更平滑的总线利用和更可控的尾延迟。因此，controller 的聪明之处，不在打破底层规则，而在借着这些规则露出来的缝隙做优化。

从系统性能角度看，controller 之所以关键，还因为它经常是“同一颗 DRAM 为什么有时很快、有时很慢”的直接分界点。一个访问流如果被映射得好、调度得顺、refresh 插得巧，可能大量命中 open row，实际带宽接近峰值；同样的颗粒，在另一种映射或调度下，可能 constantly 触发 row conflict、读写反复翻转、refresh 碰上关键窗口，结果有效带宽和 tail latency 完全是另一张脸。也就是说，controller 决定的不只是平均数值，而是 workload 能不能和 DRAM 的物理结构对齐。

对 AI 芯片和架构探索来说，这个章节尤其重要。因为很多系统在讨论“内存带宽够不够”时，只看到了 channel 数和 MT/s，却没看见 controller 本身是否允许关键 master 拿到稳定服务、是否把地址打散到了正确粒度、是否把 refresh 和 write drain 管理得足够聪明。只要这些问题答得不好，外存就很容易在系统模型里被高估。后面进入 `07-system-architecture/` 和 `09-ai-chip-memory-architecture/` 时，这一章提供的，正是“外存不是纯资源量，而是调度资源”的核心视角。

## 阅读顺序

建议按下面顺序阅读本目录：

1. [为什么说 DRAM 的实际性能由 MC 决定](./why-mc-is-the-real-bottleneck.md)
2. [命令调度：FR-FCFS 及其变体](./command-scheduling-fr-fcfs.md)
3. [Open/close/adaptive page policy 的权衡](./page-policy-open-close-adaptive.md)
4. [Refresh 调度：分散刷新、推迟刷新、bank-level refresh](./refresh-management-distributed-postponed.md)
5. [写缓冲与 write drain：为什么读优先](./write-buffer-write-drain.md)
6. [地址映射：物理地址到 channel/rank/bank/row/col 的拆分艺术](./address-mapping-channel-rank-bank-row-col.md)
7. [多 master 场景下的 QoS 与公平性](./qos-multi-master-arbitration.md)
8. [MC 在 cycle-level 仿真里的建模方法](./mc-modeling-for-simulation.md)

如果你这次主要想补“为什么同一套 DRAM 颗粒会跑出完全不同的系统行为”，优先看 1 -> 7。若你的目的已经是做仿真或架构探索，再接着看 8。

## 一句话理解

Memory controller 的本质，是把 workload 的地址流和时序需求翻译成一串在 DRAM 状态机上尽可能高效、尽可能可控的命令序列，因此它决定的不是理论峰值，而是实际可兑现性能。

## 建模启示

这一章对应的核心建模转变，是从“协议层命令合法性”进入“策略层命令选择”。也就是说，模型里不再只是判断某条命令能不能发，还要决定在多个合法候选之间先发哪条、延后哪条、牺牲谁的局部性、保护谁的时延。

一个适合作为本章各页公共底座的抽象草图可以是：

```text
MemoryControllerModel {
  req_queues: list<queue<MemReq>>
  cmd_queue: queue<DramCmd>
  bank_state: array<DramBankModel>
  timing: DramTiming
  scheduler_policy: object
  page_policy: object
  refresh_policy: object
  qos_policy: object
}
```

最小的策略循环可以写成：

```text
collect_arrivals()
update_bank_and_refresh_state()
pick_schedulable_requests()
choose_next_command(policy)
issue_or_wait()
```

如果只关心非常粗粒度的外存延迟，可以把这一整层折成经验式 latency model；但只要你要分析地址映射、row-hit-rate、QoS 或 AI workload 的外存可预测性，这一层显式 controller model 就不应再省略。因为从这里开始，性能差异已经不只是协议差异，而是策略差异。
