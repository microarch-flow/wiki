# Memory Controller

上级：[`RAM/wiki/`](../01-memory-hierarchy/)
相关：[DRAM 协议层](../03-dram/protocols/README.md), [系统视角](../01-memory-hierarchy/system-architecture/README.md)

## 这页在回答什么问题

这一章讨论：相同 DRAM 器件在不同请求流和系统中，为什么可能表现出不同的有效带宽、平均延迟和尾延迟。器件时序、上游供给、地址映射和 controller 策略都可能影响结果，需要按实际观测定位。

## 命令合法性与调度策略

DRAM 不是一个固定延迟的黑盒，而是带显式命令、timing guard、open-row 状态、refresh deadline 和 bank 并行结构的系统。当同一资源有多个合法且代价不同的候选，或请求发生争用时，命令次序和地址映射可能影响结果。若只有一条无排队依赖链，或者 DQ 已饱和，更换调度策略可能不改变观测；应分别检查器件时间、队列与总线利用率。

Memory controller 连接请求接口和 DRAM 协议。对上，它接收来自 CPU、DMA、GPU、NPU 等 master 的地址和操作；对下，它检查 bank 的打开行、命令合法性、refresh 时限和读写切换约束，再选择可发命令。多个候选竞争时，选择顺序可能改变各请求的等待与资源利用；没有竞争时，其他路径可能主导结果。

这一章按 controller 的决策展开。`why-mc-is-the-real-bottleneck.md` 说明 controller 如何与器件、请求流及上游共同影响实际性能。`command-scheduling-fr-fcfs.md` 说明：有多个合法候选时，row-hit 优先可能减少切行；持续竞争时，它也可能增加其他请求的等待。是否影响吞吐和公平性取决于候选、到达和资源约束。`page-policy-open-close-adaptive.md` 继续讨论何时保留或提前关闭一行。

后面的 `refresh-management-distributed-postponed.md`、`write-buffer-write-drain.md`、`address-mapping-channel-rank-bank-row-col.md` 和 `qos-multi-master-arbitration.md`，则分别对应 controller 另外几类长期绕不过去的问题。refresh 不是背景噪声，而是要被调度的 deadline 事件；写请求不能无限和读请求一视同仁，因为总线方向切换有真实代价；地址映射不是位切分细节，而是 row locality 和 bank hotspot 的根源；多 master 仲裁更不是公平性口号，而是在吞吐、实时性和隔离性之间做硬选择。最后的 `mc-modeling-for-simulation.md` 会把这整章收束到建模视角，明确哪些状态与事件在 cycle-level 仿真里必须保留。

这章还有一个阅读边界需要先讲清。它讨论的是“如何在既定 DRAM family 与协议约束下调度和组织请求”，而不是重新定义 DRAM 协议本身。也就是说，这里默认 `ACT/RD/WR/PRE`、timing 参数、bank 结构等都已经存在；controller 的工作，是在这些既定规则下尽量把 workload 翻译成更少冲突、更高 row-hit-rate、更平滑的总线利用和更可控的尾延迟。因此，controller 的聪明之处，不在打破底层规则，而在借着这些规则露出来的缝隙做优化。

例如同一器件上的访问流，在一种映射和调度下可能大量命中 open row；另一种安排可能增加 row conflict、方向切换或 refresh 干扰。其吞吐和尾延迟是否因此改变，仍取决于到达时序、上游供给及共享资源。应通过候选、排队和 DQ 利用率观测判断，不能只由策略名称推出结果。

对 AI 芯片和架构探索来说，这个章节尤其重要。因为很多系统在讨论“内存带宽够不够”时，只看到了 channel 数和 MT/s，却没看见 controller 本身是否允许关键 master 拿到稳定服务、是否把地址打散到了正确粒度、是否把 refresh 和 write drain 管理得足够聪明。只要这些问题答得不好，外存就很容易在系统模型里被高估。后面进入 `07-system-architecture/` 和 `09-ai-chip-memory-architecture/` 时，这一章提供的，正是“外存不是纯资源量，而是调度资源”的核心视角。

## 阅读顺序

建议按下面顺序阅读本目录：

1. [控制器与 DRAM 性能](./why-mc-is-the-real-bottleneck.md)
2. [命令调度与 FR-FCFS](./command-scheduling-fr-fcfs.md)
3. [开页与关页策略](./page-policy-open-close-adaptive.md)
4. [刷新调度](./refresh-management-distributed-postponed.md)
5. [写缓冲与写排空](./write-buffer-write-drain.md)
6. [地址映射](./address-mapping-channel-rank-bank-row-col.md)
7. [QoS 与公平性](./qos-multi-master-arbitration.md)
8. [控制器仿真建模](./mc-modeling-for-simulation.md)

如果你这次主要想补“为什么同一套 DRAM 颗粒会跑出完全不同的系统行为”，优先看 1 -> 7。若你的目的已经是做仿真或架构探索，再接着看 8。

## 一句话理解

Memory controller 按协议把请求转换并调度为命令序列。存在可选择的合法候选或资源争用时，策略可能改变可兑现性能和等待分布；器件、上游供给和工作负载也共同决定结果。

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
