# 为什么说 DRAM 的实际性能由 MC 决定

上级：[Memory Controller](./README.md)
相关：[命令调度：FR-FCFS 及其变体](./command-scheduling-fr-fcfs.md), [峰值带宽 vs 有效带宽：损失发生在哪里](../07-system-architecture/effective-bandwidth-vs-peak.md)

## 这页在回答什么问题

为什么同一套 DRAM 颗粒，在不同系统里会表现出完全不同的平均延迟、有效带宽和尾延迟。更关键的是，为什么 DRAM 规格书给你的大多只是理论上限，而 memory controller 才决定这些上限究竟能兑现多少、又是以什么方式失真。

## 正文

只要系统开始真正跑 workload，DRAM 性能就很少由“颗粒本身有多快”直接决定。颗粒规格当然重要，它定义了 bank 数、burst、timing guard、峰值 MT/s、可支持的通道组织等上限；但真正把请求一个个送进 DRAM 状态机、决定什么时候开行、什么时候保行、什么时候写排空、什么时候插 refresh、哪个 master 先服务的，是 memory controller。也就是说，颗粒给的是 `capability envelope`，controller 决定的是 `realized behavior`。这就像一支交响乐团——乐器（颗粒）的音域和音色是固定的，但演出效果取决于指挥（controller）如何安排每个声部何时进入、何时休止、何时强调。同一批乐器在好指挥手里可以奏出流畅的交响曲，在差指挥手里可能乱成一锅粥。

这个判断之所以成立，不是因为 controller “很聪明”，而是因为 DRAM 自身从根上就不是一个简单可组合资源。你面对的不是一排独立、固定延迟的存储单元，而是一套带 row buffer、bank 状态、总线共享、方向切换和 refresh deadline 的耦合系统。只要底层资源是耦合的，请求到达顺序、地址分布、命令重排和优先级策略就必然会改变结果。换句话说，MC 不是在给一个已经确定的性能做微调，而是在为一组本来就高度上下文相关的物理约束决定“最终表现长什么样”。

最直观的例子，是同一串地址流在不同 controller 策略下可能呈现完全不同的 row-hit-rate。若 controller 能识别和保留当前有价值的 open row，并把请求重排到更有利的 bank 顺序上，大量访问会落成 row hit，activate/precharge 成本被摊薄，延迟和带宽都更好。若 controller 过早关行、映射让热点集中在少数 bank、或者调度无法利用现有局部性，那么同样的颗粒会不断在 `PRE -> ACT -> RD/WR` 路径上来回跳，实际吞吐大幅下滑。常见误解是把 row locality 看成 workload 的天然属性；更准确地说，controller 至少参与决定了这份局部性能不能被兑现出来。

第二个例子是总线时间片的利用率。DRAM 的数据总线不是只要有请求就总能满负荷送数。读写方向切换有代价，不同 bank 虽然可部分并行，但最终还要争共享数据通道；refresh 还会周期性插入不可服务窗口。好的 controller 会尽量把可服务命令交织得更顺，把读请求优先级、写回时机和 refresh 窗口安排到相对合理的位置，让总线空洞尽量少。差的 controller 可能让总线频繁出现“bank 虽有工作可做，但当前可发命令不合适”或“数据总线必须等方向翻转/刷新结束”的空档。于是，峰值带宽并不是 DRAM 自动送给你的，而是 controller 要想办法把这些空洞压缩掉。

第三个例子是尾延迟。对很多系统来说，最致命的并不是平均延迟稍高，而是偶发请求为什么会慢得离谱。MC 正是尾延迟形状的直接塑形者。它如果长期偏向 row-hit 请求，吞吐可能很好，但某些 unlucky 请求会因为一直命不中、一直被插队而排得很久；如果它再叠加 refresh 撞窗、写排空或者多 master 抢占，尾部请求的等待会进一步拉长。换句话说，MC 决定的不只是”均值高低”，还决定延迟分布是更集中还是更长尾。就像一个餐厅经理——他可以让大多数客人 20 分钟吃上饭、少数人等 2 小时（偏吞吐），也可以让所有人都在 30 分钟内吃上（偏公平）。两种选择的”平均等待”也许差不多，但客户体验完全不同。

第四个例子是多 master 场景。CPU、GPU、DMA、NPU 或其他外设并不是各自拥有独立主存，它们通常都在共享同一个 controller 及其下游资源。如果 controller 不显式管理优先级、隔离性和服务窗口，那么高吞吐流量很容易把低带宽但高敏感请求压住。例如，一个大批量 DMA burst 也许能很好填满总线，却可能让 CPU 的关键控制访问或 NPU 的同步点等待异常久。此时再说“DRAM 带宽明明够高”没有意义，因为瓶颈不是理论带宽，而是 controller 怎样分配它。

再往深一点看，地址映射本身也说明 MC 不是可替换的薄壳。物理地址怎么拆成 channel/rank/bank/row/col，不是颗粒自动决定的，而是 controller 或其外围系统要参与定义的策略。不同映射会改变相邻地址究竟落到同一 row、不同 bank 还是不同 channel，这会直接改变 row-hit-rate 和并行性分布。也就是说，MC 不仅在“收到请求后怎么调度”这一步发挥作用，甚至在“地址先被理解成什么结构”这一步就已经决定了后续命运。

这也是为什么很多系统会出现一种表面矛盾：明明升级了更高代 DDR，跑某些 workload 却没见成比例收益。原因往往不是新颗粒没价值，而是 controller 并没有把新一代额外带来的 bank 并行、burst 组织、时序空间或低功耗状态好好利用起来。更高 MT/s 提供的是更大的外部潜力池，但如果调度仍然低效、映射仍然制造热点、refresh 与写排空依然常常撞在关键窗口上，那么系统看到的只是“理论上更大，实际上还在漏水的桶”。

把这一点再压缩一下，可以得到一个很实用的认识：对 DRAM 系统来说，瓶颈从来不是单点资源不够，而是 controller 是否能把多个部分可并行、部分必须串行、部分周期性被打断的资源组织成一条顺畅服务链。它既要利用 row locality，又不能只为 row hit 服务；既要提升总线利用率，又不能把尾延迟拖烂；既要按时 refresh，又不能让 refresh 把关键窗口全吃掉。这些矛盾的协调者就是 MC，所以说它是“真实瓶颈”并不是夸张，而是描述它在系统中的真实角色。

从架构探索角度看，这个结论尤其重要。因为如果你把外存只建模成一个 `latency + bandwidth` 资源，就会天然忽略 controller 的策略空间，也就看不到很多系统级 trade-off。很多 NPU/SoC 外存设计之所以后期出问题，不是因为一开始算错了峰值带宽，而是因为没有把 controller 行为建进模型，导致地址映射、QoS、写排空和 refresh 干扰在真实系统里一起反扑。

所以，本页真正要建立的结论是：DRAM 器件参数提供的是可能性边界，memory controller 决定的是现实中这些边界被兑现成什么样的延迟分布、带宽效率和服务隔离。只要 DRAM 还是 row/bank/refresh/timing 这套状态机，MC 就必然是实际性能的第一解释层。

## 一句话理解

DRAM 颗粒决定的是峰值能力上限，memory controller 决定的是这些上限在真实请求流中能兑现多少，以及它们会以高吞吐、低延迟还是高尾延迟的哪种形态表现出来。

## 建模启示

在模型里，外存不能只被建成一个纯资源池，至少要显式存在 `controller policy layer`。即使你不模拟完整 DRAM 命令，也应该保留某种“同样请求流在不同策略下会得到不同 row-hit-rate、总线利用率和尾延迟”的机制，否则模型会系统性高估理论带宽的可实现性。

一个最小可用的抽象可以是：

```text
McEffectModel {
  address_mapping_policy: enum
  scheduling_policy: enum
  page_policy: enum
  refresh_policy: enum
  write_drain_policy: enum
}
```

然后让这些策略影响三个关键观测量：

```text
ObservedMetrics {
  row_hit_rate: float
  bus_utilization: float
  tail_latency_p99: cycle
}
```

如果只关心粗粒度吞吐，可能只需要把策略影响折成经验参数；但只要你要比较不同 SoC、不同 workload 或不同 memory route，最好显式让 `address_mapping_policy` 和 `scheduling_policy` 进入模型。因为同一颗 DRAM 在系统里“表现像什么”，往往首先由这两者决定，而不是由峰值 MT/s 决定。
