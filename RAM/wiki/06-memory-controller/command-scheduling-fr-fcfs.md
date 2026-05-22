# 命令调度：FR-FCFS 及其变体

上级：[Memory Controller](./README.md)
相关：[为什么说 DRAM 的实际性能由 MC 决定](./why-mc-is-the-real-bottleneck.md), [Open、close、adaptive page policy 的权衡](./page-policy-open-close-adaptive.md)

## 这页在回答什么问题

为什么 FR-FCFS 会成为 DRAM 控制器里最经典、最常被引用的调度策略，以及它为什么一方面几乎天然有效，另一方面又几乎天然不公平。更重要的是，它到底在利用什么物理结构，又在哪些场景下会把某些请求饿得很惨。

## 正文

一旦你接受了上一页的判断：DRAM 的真实性能高度取决于 controller 如何在 row/bank/timing 约束下选择下一条命令，那么下一个自然问题就是“什么样的选择才算好”。FR-FCFS，也就是 `First-Ready, First-Come-First-Serve`，之所以经典，不是因为它名字漂亮，而是因为它正好抓住了 DRAM 最值钱的一点局部性：如果某个请求已经 ready，尤其是已经命中当前 open row，那么先服务它往往能立刻省掉 activate/precharge 这笔大成本。

先把名字拆开。`First-Ready` 的意思是，在当前时刻所有排队请求中，优先挑那些其下一步命令已经满足 timing guard、而且最容易立即发出的请求。对 DRAM 来说，这通常意味着 row-hit 请求天然占优，因为它们往往只差一个 RD/WR 就能继续，而 row-conflict 请求还得等 PRE、ACT 等一串前置动作。`FCFS` 的部分则是说，在同样 ready 的请求之间，再用先来先服务作为次级排序依据。换句话说，FR-FCFS 不是简单的到达顺序队列，而是“先看谁最能立刻利用当前 bank/open-row 状态，再在这些候选里看谁来得早”。

这个策略为什么有效，其实几乎是 DRAM 物理结构直接推出来的。row hit 的边际成本远低于 row miss / row conflict，因此只要你优先服务 row hit，请求平均成本就会下降，总线空洞也更少，bank 利用率通常更高。FR-FCFS 不是在玩复杂启发式，而是在非常直接地说：既然某些请求已经踩在当前 open row 上，那就别急着切走，先把便宜的活干完。对于大量存在行局部性的 workload，这种选择几乎一定能提高吞吐。

一个简单例子最能说明它为什么“天然有效”。假设同一 bank 当前 open row 是 `R10`，队列里有三笔请求：

```text
Req A: bank0, row10, col1   arrival=10
Req B: bank0, row22, col8   arrival=8
Req C: bank0, row10, col9   arrival=12
```

若完全按到达顺序，controller 可能会想先做 `Req B`，但这意味着：

```text
PRE(row10) -> ACT(row22) -> RD(B)
```

之后如果还要回到 `Req A/C`，又得再切回 row10，代价更高。FR-FCFS 则会优先看 ready 的 row-hit：

```text
RD(A) -> RD(C) -> PRE(row10) -> ACT(row22) -> RD(B)
```

这条顺序显然更便宜，因为同一 row 的开行成本被摊薄了。这就是 FR-FCFS 长期有效的根因：它把 DRAM 的“状态相关便宜机会”尽量吃干净。

但这个策略也几乎注定会伤害公平性。因为只要请求流里源源不断出现新的 row-hit，请求队列中那些命不中当前 open row 的访问就会不断被推后。你可以把它理解成：FR-FCFS 天生喜欢“顺手、便宜、现在就能做”的请求，而不喜欢那些需要先清场再开新局的请求。从系统吞吐角度，这非常合理；从个体请求视角，这可能非常残酷。常见误解是觉得 FR-FCFS 只是“稍微偏向 row-hit”；实际上，在高压负载下，它完全可能形成明显的 starvation 倾向。

再看一个更尖锐的例子。假设 bank1 当前 open row 是 `R5`，某个流 `S` 连续不断地访问 row5 的不同列；同时另一个流 `T` 偶尔访问 bank1 的 row9。队列可能持续呈现：

```text
S1: bank1 row5
T1: bank1 row9
S2: bank1 row5
S3: bank1 row5
S4: bank1 row5
...
```

在 FR-FCFS 下，只要 row5 hit 还在不断补进来，`T1` 就会反复被压后，因为一旦为了它切到 row9，当前 row5 的便宜窗口就被放弃了。于是：

```text
RD(S1) -> RD(S2) -> RD(S3) -> RD(S4) -> ...
```

而 `T1` 可能长期等不到 `PRE(row5) -> ACT(row9)` 这一步真正发生。也就是说，FR-FCFS 的吞吐提升，来自把“昂贵切换”尽量推迟；但被推迟的请求恰恰会形成尾延迟长尾。

这就是为什么 FR-FCFS 虽然经典，却很少会在真实系统里原封不动裸跑。很多控制器会在它外面叠加各种“变体保护”：老化机制、服务计数、最大连续 row-hit 数限制、read/write 分级队列、per-thread/per-master fairness cap，或者直接在 QoS 场景里为高优先级流保底。所有这些变体的核心目标都一样：保住 FR-FCFS 对 row locality 的利用，但别让它把某些请求永远饿在门外。

这里还需要把 FR-FCFS 和 page policy 的关系说清。FR-FCFS 喜欢 row-hit，本质上是在利用“当前 open row 仍值得留着”这个前提；而这个前提是否成立，又取决于 controller 的 page policy。如果你走 close-page，很多请求根本没机会形成连续 hit，FR-FCFS 的优势就会被削弱；如果你走 open-page，它的局部性收益更大，但公平性和冲突问题也更明显。也就是说，FR-FCFS 不是独立策略，而是天然和“你愿意让 open row 活多久”绑在一起。

它还和地址映射高度耦合。若地址映射把相关请求分散到不同 bank，FR-FCFS 也许更容易在多 bank 间交织，既吃 row-hit 又保并行；若映射让某些流集中撞到同一 bank，则 FR-FCFS 会更像“偏爱某一小撮幸运行”的策略。因此，看到 FR-FCFS 表现好或差，不应只评价调度本身，还要问：请求流是怎么被映射成 row/bank 结构的。

从建模角度再压缩一下，FR-FCFS 的本质可以理解成一个很直接的目标函数：`maximize immediate readiness and row reuse`。这让它成为极其强的吞吐优化器，但也自然让它对个体公平性缺乏内在关心。只要系统目标更偏吞吐，它几乎总会是强基线；只要系统开始看重 QoS、实时性或多租户隔离，它就必须被修剪、约束或与更高层策略结合。

所以，本页真正要建立的不是“FR-FCFS 是经典算法”这句标签，而是更具体的判断：它之所以经典，是因为 DRAM 的物理结构直接奖励 row-hit 与 ready-first；它之所以危险，也是因为同一物理结构会让不命中当前 open row 的请求天然处于被牺牲的位置。理解这一点，后面 page policy、QoS 和建模决策就都有了出发点。

## 一句话理解

FR-FCFS 天然有效，是因为它优先兑现当前 DRAM 状态里最便宜的 row-hit 机会；它天然不公平，也是因为同样的策略会持续推迟那些需要切行才能服务的请求。

## 建模启示

在建模里，FR-FCFS 不需要被写成很复杂的算法，但必须至少保留两个排序维度：`是否 ready` 和 `是否 row-hit`。如果直接按到达顺序出队，就会严重低估 controller 对吞吐的优化能力；如果只按 row-hit 排序，又会高估它对公平性的忽视程度。一个最小实现通常是三层优先级：ready row-hit > ready non-row-hit > not-ready。

一个简化的调度伪码可以写成：

```text
candidates = requests whose next_cmd is timing-legal
rank by:
  1. row_hit first
  2. earlier arrival first
pick top candidate
```

如果要把 starvation 风险也带进模型，可以加一个简单 aging 项：

```text
priority = row_hit_bonus + ready_bonus + age_weight * waiting_cycles
```

一个够用的数据结构草图可以是：

```text
SchedReq {
  arrival_cycle: cycle
  bank_id: int
  target_row: row_id
  row_hit: bool
  ready: bool
  waiting_cycles: cycle
  source_master: MasterId
}
```

如果只关心平均吞吐，纯 FR-FCFS 可能已经够用；但只要你要评估 tail latency、QoS 或多 master 场景，就最好显式加入 aging/fairness 机制。因为 FR-FCFS 的问题不在于它“不聪明”，而在于它太忠实地在优化 DRAM 物理结构最喜欢的那一类请求。
