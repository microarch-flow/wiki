# 多 master 场景下的 QoS 与公平性

上级：[Memory Controller](./README.md)
相关：[命令调度：FR-FCFS 及其变体](./command-scheduling-fr-fcfs.md), [NPU 的 on-chip 带宽预算从哪来、到哪去](../09-ai-chip-memory-architecture/on-chip-bandwidth-budget.md)

## 这页在回答什么问题

当 CPU、DMA、GPU、NPU 或其他外设的多个 master 同时访问 DRAM 时，controller 如何在总吞吐、公平性、实时性和隔离性之间取舍。更关键的是，为什么 QoS 不是“再加一层优先级”这么简单，而是直接决定谁可以把自己的延迟和带宽风险转嫁给别人。

## 正文

单一请求流下的 DRAM 调度已经很复杂，但真正让 controller 从“性能优化器”变成“系统治理者”的，是多 master 场景。只要多个 master 共用同一套 channel、bank、总线和 refresh 预算，控制器面对的就不再只是“如何提高平均 row-hit-rate”，而是“谁先过、谁让路、谁可以稳定拿到服务、谁必须接受波动”。这时候，吞吐、公平、实时性和隔离性不可能同时最优，QoS 的本质就是决定优先保哪几个。这就像一家医院的急诊分诊——你不能让所有病人按挂号顺序排队，因为心脏骤停的患者等不起。但你也不能让急诊永远插队，否则普通发烧的病人可能等到天亮都看不上。分诊护士做的，就是 QoS。

先看为什么单纯追求总吞吐会出问题。FR-FCFS 之类的策略天然偏爱 row-hit、多事务连续、易于填满总线的流量。如果一个 GPU 或 DMA 大流量请求流刚好有很好的 row locality，它会非常容易在调度中占优势；与此同时，CPU 的低带宽控制访问、NPU 的同步控制流或某些中断相关访问，虽然总流量很小，却可能因为经常不命中当前 row、不能形成长 burst，而被不断排在后面。从平均总线利用率看，这也许是“高效”的；从系统功能看，可能意味着关键控制路径抖动巨大。

这说明了 QoS 的第一层核心：`带宽贡献不等于服务优先级`。一个 master 产生的流量越大，并不代表它越应该总是先被服务。恰恰相反，很多对系统成败更关键的请求，往往带宽占比小、但对延迟特别敏感。比如 CPU 读一个锁变量、NPU 等一个下一阶段描述符、DMA 等待一个 doorbell 更新，这些事务单看吞吐毫不起眼，却可能决定整条系统流水是否停住。常见误解是把 QoS 理解成”公平分带宽”；更准确的说法是，它在决定”哪些低量但高敏感请求不能被高吞吐流量淹没”。就像消防通道不是为了”公平分配路面”，而是为了保证消防车在任何时候都能过——哪怕它一天只开一趟，这条通道也必须随时畅通。

第二层核心是 `公平` 并不等于 `隔离`。假设 controller 给每个 master 轮流平均分机会，这在字面上很公平，但并不一定能给出真实隔离。因为不同请求的成本不同：一个命中当前 row 的 burst 和一个需要 `PRE -> ACT -> RD` 的请求，占用的 bank 时间和总线时间完全不同；一个读请求与一个会触发写排空窗口的写流，影响也完全不同。于是“每人一个请求槽”不等于“每人承受相近干扰”。真正的隔离通常需要更细的度量，例如带宽配额、最大等待窗口、优先级保底、甚至 bank/channel 空间隔离。

第三层核心是 `实时性` 与 `吞吐` 经常天然冲突。对实时 master 来说，最重要的是最坏情况不能过长，因此 controller 可能要在某些时刻强行插队，让高优先级请求即使破坏当前 row locality，也要先过。这样做显然会损伤整体吞吐，因为你可能为了赶一个单小请求，放弃了一串本可连续命中的 row-hit。但对实时系统来说，这笔代价是值得的，因为它买来的是 deadline 可控。换句话说，QoS 不是给“性能更好”的请求加分，而是在必要时允许系统主动牺牲吞吐，换取确定性。

可以用一个最小例子看冲突为什么会变成治理问题。假设：

```text
Master A: GPU stream, high volume, row-friendly
Master B: CPU control reads, low volume, latency-sensitive
Master C: DMA writes, bursty
```

若 controller 只追求吞吐，可能长期形成：

```text
Serve A row-hit burst -> continue A -> drain C writes opportunistically -> B waits
```

从 bus utilization 看很漂亮，但 B 的单次等待可能非常难看。若 controller 为 B 设定高优先级保底，则行为可能变成：

```text
Serve A row-hit burst -> preempt for B critical read -> resume A/C
```

这时总吞吐略降，但 CPU 控制流稳定多了。QoS 就是在决定这类牺牲值不值得。

第四层核心是 `仲裁粒度`。QoS 不是只能在请求队列头上做。它可以发生在多个层面：请求进入 controller 前的 source tagging；请求在队列中的分组或配额；bank 选择时的高优先级抢占；write drain 是否允许被关键读打断；refresh 是否可以为某类 deadline-sensitive 流让出一点相位窗口。也就是说，QoS 不是独立算法，而是一组跨调度器、写缓冲、refresh 和地址映射的联动约束。

这也解释了为什么很多真实控制器会采用多层策略，而不是单一优先级队列。常见做法包括：

- 为延迟敏感流设更高 base priority
- 给吞吐型流保带宽但限制连续占用时长
- 用 aging 防止低优先级请求永久饿死
- 对关键 master 设最大等待门限
- 在 channel/bank 层做部分物理隔离

这些做法看起来各不相同，但底层目标一致：别让“擅长利用 DRAM 物理结构”的流量，把“对系统功能更关键”的流量彻底踩没。

从 NPU/SoC 视角看，QoS 的问题通常比 PC 更尖。因为加速器系统里 master 类型差异很大：有的流是大块连续张量搬运，有的是控制核的小随机访问，有的是 DMA completion，有的是同步栅栏或 descriptor 读取。它们的流量形状和敏感指标完全不同。如果 controller 只看总吞吐，很容易让高带宽张量流把关键控制流淹掉，结果表面上总线利用率很高，系统端到端吞吐却因为等待小控制请求而崩掉。后面到 `on-chip-bandwidth-budget.md` 和 AI 章节时，这种现象会以更具体的形式出现。

这里必须强调一个常见误解：QoS 不是“给高优先级流一切都最优”。如果你把优先级设计得过硬，某个 master 可能拿到了漂亮的最坏延迟，但其余所有流都被严重伤害，整体系统吞吐和能效下降得厉害。真正成熟的 QoS 更像一组边界条件：某些流不能超过某个最大延迟、某些流必须保住最低带宽、某些流可以被让路但不能永久饥饿。也就是说，QoS 的目标通常不是绝对最优，而是受约束的可接受。

因此，多 master DRAM controller 的仲裁问题，本质上是在做社会分配，而不是单纯做数学最优。你在决定哪类请求的等待更“值钱”，哪类请求的牺牲更“可接受”，以及哪些物理优化机会值得为了谁放弃。只要系统里同时存在吞吐型流和实时/控制型流，这个问题就无法回避。

## 一句话理解

多 master 下的 QoS，本质上是在决定谁可以把自己的 DRAM 冲突和排队成本转嫁给别人；它不是简单追求公平或吞吐，而是在吞吐、实时性和隔离之间做有意识的不对称分配。

## 建模启示

在模型里，QoS 不能只通过“每个 master 一个权重”草草表示。最少应同时保留三类约束：`base priority / bandwidth share / max latency protection`。因为同样的权重公平，并不能保证同样的实际影响公平。

一个够用的策略草图可以写成：

```text
MasterQosPolicy {
  base_priority: int
  min_bandwidth_share: float
  max_wait_cycles: cycle
  latency_sensitive: bool
}
```

然后让 controller 在调度时同时考虑：

```text
score(req) =
  row_hit_bonus
  + ready_bonus
  + qos_priority(req.master)
  + aging_bonus(req.waiting_cycles)
```

如果只关心平均吞吐，可能可以忽略 `max_wait_cycles`；但只要你要看 tail latency、关键控制流、DMA backpressure 或 AI 系统控制面/数据面的相互干扰，这个字段就不应省略。因为很多“系统为什么卡死”并不是因为总带宽不够，而是因为某个低带宽关键流长期抢不到服务。

一个更接近系统目标的观测量集合可以是：

```text
QosObservedMetrics {
  per_master_avg_latency[master]
  per_master_p99_latency[master]
  per_master_bw[master]
  starvation_events[master]
}
```

只要这些量进了模型，QoS 就不再是抽象口号，而会直接变成可验证、可比较的系统行为。
