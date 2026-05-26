# Activation buffer 与 double buffering：数据搬运与计算如何重叠

上级：[AI 芯片内存架构](./README.md)
相关：[Weight buffer 的容量与组织：从 model size 反推](./weight-buffer-design.md), [“数据搬运优先”原则在 NPU 设计中的体现](./data-movement-first-principle.md)

## 这页在回答什么问题

activation buffer 为什么经常决定流水能不能跑满；double buffering 又是在什么条件下真的隐藏了外层访存，而不是只是把容量翻倍。

## 正文

如果说 weight buffer 更多是在解决“某块权重值不值得多留一会儿”，那么 activation buffer 更直接地在解决另一件事：`下一块将被计算消耗的数据，能不能准时到位`。这两件事看起来都属于片上 SRAM，但系统含义完全不同。权重更像读主导、重用拉长的驻留对象；activation 更像一条持续向前推进的输入流，它既要被搬进来，又要被按下游节拍稳定地消耗掉。于是 activation buffer 往往比 weight buffer 更直接决定流水线能不能跑满。

这件事在 AI 芯片里尤其关键，因为 activation 的生产和消费常常来自两个不同节拍域。上游可能是 HBM、LPDDR 或更高层 SRAM，它们按 burst 和 tile 粒度交付数据；下游则是阵列、PE cluster 或某个算子阶段，它们希望在每拍或每几个拍上拿到规整切片。activation buffer 的核心作用，就是把这两个节拍域接起来。它既像暂存池，又像节拍转换器，还像数据整形器。只要其中任一角色没做好，下游就会看到最糟糕的情况：算力明明够、权重也在本地，但输入块还没到。

从访问模式上看，activation 和 weight 的差别很大。weight 通常是“装一次，读很多次”；activation 更常见的是“写入一块，随后在较短窗口内被读若干次，然后很快被下一块替换”。这种生命周期更短、滚动更快的特性，使 activation buffer 天然和 `double buffering`、`prefetch`、`DMA overlap` 绑在一起。因为它不只是要存下当前 tile，还要在当前 tile 被消费时，尽可能把下一 tile 也准备好。

这就是 double buffering 的直观来源。它最常见的说法是“两个 buffer 轮流用，一个算，一个搬”，这当然没错，但还是太表面。更准确地说，double buffering 是在利用 activation 流的阶段性规律，把”数据搬入”和”当前计算消费”这两件原本串行的事情，尽量改造成并行。也就是说，它本质上不是容量优化，而是时间重叠优化。想象一个餐厅的传菜窗口：如果只有一个窗台，厨师做完一盘菜放上去，服务员端走，窗台空了，厨师才能放下一盘——做菜和上菜是串行的。如果有两个窗台，厨师可以在服务员端走 A 窗台的菜时，把下一盘放到 B 窗台上。两个窗台不是为了同时摆两倍的菜，而是为了让”出菜”和”上菜”同时进行。

如果写成最简单的节拍图，大致就是这样：

```text
time ---->

buffer A: [fill tile 0] [compute tile 0] [fill tile 2] [compute tile 2]
buffer B:                [fill tile 1] [compute tile 1] [fill tile 3]
```

理想情况下，当 tile 0 在 buffer A 中被下游消费时，tile 1 正在被搬进 buffer B；等 tile 0 结束，tile 1 就刚好就绪，然后两者交换角色。只要 `fill_time(next_tile) <= compute_time(current_tile)`，重叠就成立，外层访存的大部分表面延迟就能被隐藏在当前计算窗口里。

但这里也埋着一个极常见的误区：`有 double buffer` 不等于 `延迟被隐藏了`。它只有在几项条件同时成立时才真正有效。第一，下一 tile 的数据量不能大到填充时间明显长于当前 tile 的计算时间。第二，填充路径本身不能被别的流量严重抢占，例如权重 refill、输出写回或片上共享网络热点。第三，buffer 组织必须允许“边填一个、边读另一个”，也就是 bank、端口和控制状态不能互相卡死。第四，tile 边界必须足够规整，否则切换开销、尾块不齐或依赖关系会吃掉重叠收益。

换句话说，double buffering 真正在买的，不是“多一份容量”，而是“一个独立的下一拍准备窗口”。如果外层供数太慢，这个窗口会空；如果内部仲裁太重，这个窗口会堵；如果 tile 太小，窗口建立起来的管理成本反而不划算。所以判断 double buffering 是否有意义，不能只看架构图上有没有两个框，而要看它有没有形成稳定的 `producer-consumer overlap`。

activation buffer 之所以经常成为流水瓶颈，还因为它更容易受到 `数据整形` 的压力。上游吐出来的数据顺序，未必正好就是阵列最想要的顺序。尤其在卷积、attention、gather/scatter 或者带有 layout transform 的场景里，activation 往往需要在进入计算阵列前经历重排、打包、分 lane 或 bank interleave。也就是说，activation buffer 并不只是一个“把数据摆着等用”的箱子，它常常承担了一部分轻量 reformatting。这个过程如果和搬运、消费竞争同一组 bank 或同一条内部链路，就会让本该隐藏的延迟重新露出来。

从 `Topology` 视角看，activation buffer 还处在一个比 weight buffer 更容易被共享流量打扰的位置。因为 activation 常常是“来自上游算子输出，又流向下游算子输入”的中间态数据，所以它既可能承接外存 DMA，也可能承接片上其他 cluster、其他 stage 的结果。这样一来，它就不只是一个单一 source 的输入池，而更像一个局部交通枢纽。就像火车站的中转站台——同时有列车到站、有旅客换乘、有行李转运，站台的物理面积可能够大，但如果进出通道只有一条，高峰期照样堵死。交通枢纽的典型问题不是容量本身，而是同时到站、同时出站时的冲突。很多系统看上去 activation buffer 很大，但真跑起来吞吐上不去，问题往往不在字节数，而在同一时刻既要 fill、又要 read、还要做内部重排。

因此，activation buffer 的设计通常要同时回答三个问题。第一，`当前 tile` 如何被下游稳定消费。第二，`下一 tile` 能否在当前 tile 期间被无冲突地搬入。第三，如果 activation 来自多个上游路径，进入本地前是否需要额外整形。只有这三件事一起被解决，double buffering 才是有效的；少任何一项，它都可能沦为只是把 buffer 从一份做成两份。

这也说明了为什么 activation buffer 的容量不能单独分析。很多人会问：“这一级 buffer 要不要加倍？”但真正该问的是：“当前 tile 有多大、下游 compute 窗口有多长、下一 tile 的 refill 路径有多宽、两者能否物理并发？”如果 compute window 本来就很短，或者 refill path 明显更慢，那么加一个完整双缓冲可能仍然遮不住延迟；这时更合理的优化反而可能是改 tile 形状、提高上游 burst 效率、增加 bank 并行度，或者减小需要频繁切换的 activation 工作集。

在不同 workload 上，这个问题的形状也不同。卷积类 workload 常常更依赖滑窗与空间重用，activation buffer 会深度参与行列块滚动；attention 类 workload 常常面临更大、更动态的 token/block 组织，buffer 需要吸收更复杂的序列分块节奏；Mixture-of-Experts 或稀疏访问场景下，activation 的到达顺序和消费顺序可能更不规整，double buffering 的理想重叠更难维持。也就是说，activation buffer 的难点不是一个通用存储公式，而是它对 workload 的时间形状高度敏感。就像同一个行李传送带系统，在处理标准尺寸行李箱时运转流畅，但一旦来了超长滑雪板、不规则形状的乐器盒，传送带就可能卡顿——不是带子不够长，而是它的节奏和分拣逻辑没法适配这种非标形状。

因此，本页真正要建立的判断是：activation buffer 是 AI 芯片流水稳定性的关键节点，而 double buffering 只是它最常见的一种时序组织方法。double buffering 的价值来自重叠，不来自名字；activation buffer 的价值来自把上游粗粒度、可能有抖动的数据流，改造成下游阵列可以持续吞下的局部稳定流。后面到了 `on-chip-bandwidth-budget.md`，你会看到这种“重叠是否真的成立”最终会落到片上和片外两侧带宽是否同时够用。

## 一句话理解

activation buffer 的核心任务是把上游 bursty 输入流变成下游稳定供数流，而 double buffering 只有在 refill、banking 和 tile 窗口都匹配时，才真的能把搬运延迟隐藏在当前计算后面。

## 建模启示

在模型里，activation buffer 不能只用一个 `capacity_bytes` 表示。至少还要显式建出两个状态：`当前被消费的 tile` 和 `正在被填充的 tile`。否则你根本无法判断 double buffering 是否真的在工作。

一个最小可用抽象可以写成：

```text
ActivationBuffer {
  slot_count: int
  slot_bytes: int
  bank_count: int
  read_bw_Bps: float
  fill_bw_Bps: float
  supports_simultaneous_fill_and_read: bool
  format_transform_cost_ns: float
}
```

对应的 tile 生命周期可以写成：

```text
ActivationTileState {
  tile_id: int
  state: enum { empty, filling, ready, consuming, drained }
  bytes_total: int
  bytes_filled: int
  bytes_consumed: int
}
```

仿真时最值得保留的事件有：

- `ActivationFillStart/Done(tile_id, slot)`
- `ActivationConsumeStart/Done(tile_id, slot)`
- `ActivationSwap(slot_a, slot_b)`
- `ActivationStall(reason)`

其中 `reason` 至少区分：

- refill_not_done
- bank_conflict
- format_transform_busy
- downstream_backpressure

如果这些状态都在，模型就能回答一个真实问题：吞吐下降到底是因为 activation buffer 太小，还是 double buffering 没建立起来，还是其实建立起来了但 bank 和重排链路在中间漏水。
