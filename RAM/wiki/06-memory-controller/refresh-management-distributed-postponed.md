# Refresh 调度：分散刷新、推迟刷新、bank-level refresh

上级：[Memory Controller](./README.md)
相关：[刷新：DRAM 的原罪和它的代价](../04-dram-foundations/refresh-the-fundamental-cost.md), [写缓冲与 write drain：为什么读优先](./write-buffer-write-drain.md)

## 这页在回答什么问题

既然 refresh 无法取消，memory controller 还能在哪些地方争取调度灵活性。更具体地说，distributed refresh、postponed refresh、bank-level refresh 这些策略分别在交换什么，以及它们怎样影响吞吐、尾延迟和控制复杂度。

## 正文

上一章已经把 refresh 的物理本质讲清了：它不是业务访问，而是 DRAM 为了不让数据自然蒸发而持续缴纳的系统税。到了 controller 这一层，问题就变成了另一句更现实的话：既然这笔税一定要交，能不能挑个没那么痛的时候交，或者至少别每次都把整块阵列最关键的服务窗口一起锁死。refresh 管理的全部意义，都在这里。

最朴素的 refresh 实现方式，是把刷新严格按固定节拍触发，到点就发，发完再继续服务正常请求。这样的实现简单、易验证，也最接近“物理 deadline 到了就立即处理”的直觉。但它的问题也同样直接：它对请求流形状完全不敏感。无论当前 bank/rank 空不空、读请求急不急、是不是刚好处在热点窗口，refresh 都会硬插进来。对平均带宽也许还能接受，对 tail latency 和 QoS 则往往很不友好。

`Distributed refresh` 的思路，是把必须完成的刷新工作更均匀地摊开，而不是让更大块的刷新集中砸在少数时刻。你可以把它理解成把税款拆成更多小笔定期支付。这样做的收益是：单次 blocking 窗口更容易控制，请求流更不容易被某个超长刷新区间一次性打断；功耗峰值也更平滑。代价则是 controller 必须更持续地关心 refresh 节奏，系统更频繁地进入“虽然每次不长，但经常要让路”的状态。换句话说，distributed refresh 优化的是刷新干扰的波形形状，而不是刷新总成本本身。

`Postponed refresh`，也就是推迟刷新，背后的逻辑更像是“deadline 还没彻底到，先把眼前这一小段高价值请求流服务掉”。因为 DRAM 规范通常会给 refresh 一定的灵活窗口，而不是要求绝对每个固定时刻立刻执行，所以 controller 有机会在受限范围内往后拖几次 refresh，把一些 bursty 的 row-hit 请求、关键读请求或高优先级流量先送过去。这样做的好处很明显：controller 获得了一点对 workload 相位的感知能力，不再被 refresh 节拍完全牵着走。坏处也同样明显：你只是把 debt 往后挪，不是消灭它；如果后面一直繁忙，被推迟的 refresh 会积压成更集中的压力，甚至在更糟时刻一起回来。

可以用一个最简化的例子看 postponed refresh 为什么“看似聪明，但不能滥用”。假设 bank 当前连续收到一串命中同一 row 的关键读：

```text
Cycle 100: refresh due
Queue: R(row10), R(row10), R(row10), R(row10)
```

如果立即 refresh，可能会变成：

```text
REF -> R -> R -> R -> R
```

如果允许有限推迟，controller 可能做成：

```text
R -> R -> REF -> R -> R
```

这样局部吞吐和前两笔读的延迟都更好。但如果 controller 每次都只想再拖一下，而后面队列始终很满，那么到某一刻就不得不补交前面欠下的多笔 refresh，反而形成更大的 tail spike。也就是说，postponed refresh 的收益来自相位移动，风险也来自相位移动。

`Bank-level refresh` 则是在刷新作用范围上做文章。它的核心思想不是把 refresh 时间藏起来，而是尽量把它局部化。若刷新只锁住一个 bank，而不是整组更大的资源，那么其他 bank 至少还可以继续服务普通请求。这种策略非常契合我们在前面讲 bank 时建立的直觉：bank 是最小可调度并行单元，因此 refresh 若也能在 bank 粒度上局部化，就更容易把影响限制在局部，而不把整条通道一次性拖死。它的收益是并行性保留得更多，尤其在多 bank 活跃负载下更有价值；代价是实现和控制更复杂，controller 必须更细粒度跟踪哪些 bank 在 refresh、哪些仍可调度。

把这三种思路摆在一起，可以得到一个很实用的比较框架：

```text
Distributed refresh:
  优点：单次阻塞更平滑
  代价：更频繁打断普通服务

Postponed refresh:
  优点：能让 controller 先吃掉眼前高价值请求窗口
  代价：只是把压力后移，可能制造之后的集中惩罚

Bank-level refresh:
  优点：把 refresh 影响局部化，保住其他 bank 并行
  代价：控制复杂、状态更细、调度空间更大也更难用好
```

这三者并不是彼此排斥的。现实控制器往往会组合使用：在 bank 粒度上做局部刷新，同时允许有限推迟，并用分散策略控制刷新债务不要突然堆成一坨。也就是说，refresh 管理不是选一个名词，而是在“作用范围、相位安排、债务积压程度”这三个维度上共同调参数。

这里最重要的控制器视角，是把 refresh 看成一种 `deadline-constrained background task`，而不是一种硬编码中断。它和普通请求不同，因为它没有“业务价值”，却有硬 deadline；它和纯后台任务也不同，因为拖过 deadline 就是错误。于是 controller 的工作，不是问“要不要 refresh”，而是问“在 deadline 允许的自由度里，怎么让 refresh 和正常服务相撞得更少”。这也是为什么 refresh 管理天然会和写排空、page policy、QoS 一起形成耦合：你在某个时刻让 refresh 先走，就改变了后面总线、bank 和延迟分布。

refresh 管理对尾延迟尤其敏感。平均吞吐层面，很多策略看起来差异没那么夸张，因为总税额变化不大；但对单请求延迟分布来说，策略差异会非常明显。把 refresh 分散开，会让每次被挡住的时间短一些，但被挡住的概率更高；把 refresh 推后，会让大多数时刻更顺，却可能在后面某个时刻形成更重的堵塞。对追求 QoS 或实时性的平台，这意味着 refresh policy 不能只看平均带宽，还必须看它把阻塞“切成什么形状”。

这也是为什么 LPDDR、HBM 等路线会对 refresh 管理更敏感。LPDDR 更在意待机和背景功耗，因此自刷新、部分阵列保持和低功耗状态切换会更重要；HBM stack 的热条件和堆叠复杂性又会让 refresh 规划更加棘手。虽然这些具体家族机制各有不同，但 controller 层的根问题一样：如何让“不可取消的保命任务”尽量少打断真正想做的业务访问。

所以，本页真正要建立的不是一组 refresh 技术名词，而是这样一个判断：refresh 管理的本质，是 controller 在 deadline 不能破、总债务不能少的前提下，努力重塑这笔成本对请求流的撞击方式。不同策略改变的不是 refresh 是否存在，而是它如何分布、如何局部化、如何与高价值流量错峰。

## 一句话理解

Refresh 管理不是在决定“要不要刷”，而是在决定“这笔必须交的税怎样分期、怎样错峰、怎样局部化”，从而把它对吞吐和尾延迟的伤害重新塑形。

## 建模启示

在模型里，refresh policy 不应只是一个固定的 `tRFC penalty` 常数，而应至少显式保留三类策略自由度：`作用范围`、`可推迟预算`、`触发节奏`。否则模型只能给出平均扣税，却无法表达 distributed / postponed / bank-level 之间对 tail latency 和并行性的真实差异。

一个够用的策略状态草图可以写成：

```text
RefreshPolicyModel {
  scope: enum { RANK_LEVEL, BANK_LEVEL }
  distributed: bool
  max_postpone_count: int
  due_cycle[scope_id]: cycle
  postponed_count[scope_id]: int
}
```

对应事件流可以写成：

```text
event RefreshDue(scope_id)
event RefreshPostpone(scope_id)
event RefreshIssue(scope_id)
event RefreshComplete(scope_id)
```

一个最小调度判定可以是：

```text
if refresh_due and postpone_budget_remaining and critical_reads_present:
    postpone_refresh()
else:
    issue_refresh()
```

如果只关心平均吞吐，可以把 refresh 近似成每个作用域周期性损失固定服务窗口；但只要你要看 QoS、tail latency 或多 bank 并行利用率，就最好显式保留 `scope` 和 `postpone_budget`。因为 refresh policy 的价值，恰恰体现在“同样总税额，不同冲击形状”。
