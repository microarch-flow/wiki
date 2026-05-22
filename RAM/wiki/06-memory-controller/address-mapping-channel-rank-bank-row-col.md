# 地址映射：物理地址到 channel、rank、bank、row、col 的拆分艺术

上级：[Memory Controller](./README.md)
相关：[为什么说 DRAM 的实际性能由 MC 决定](./why-mc-is-the-real-bottleneck.md), [多通道、多 socket、NUMA：扩展带宽的代价](../07-system-architecture/numa-multi-channel-multi-socket.md)

## 这页在回答什么问题

为什么物理地址到 channel、rank、bank、row、column 的映射，不是一个低层实现细节，而是直接决定 DRAM 请求流最终长成什么冲突形状和并行形状的系统级策略。更具体地说，同一串程序地址在不同映射下，为什么会表现出完全不同的 row locality、bank hotspot 和通道均衡结果。

## 正文

很多人第一次看到 DRAM 地址映射，会把它想成一个“把若干位切给 channel/bank/row/col”的工程表格，好像只要切对了能寻址就行。这个视角最大的问题，是把映射当成被动翻译。真实系统里，地址映射远不只是把线接对，而是在决定：程序产生的一维地址流，最终会被投影成怎样的多维 DRAM 访问图形。投影方式不同，row-hit-rate、bank parallelism、channel balance、refresh 受扰形状，甚至不同 master 之间是否互相踩踏，都会跟着变。

理解映射最稳的起点，是先把地址流和 DRAM 结构同时摆出来。程序看到的是线性物理地址空间，但 DRAM 看到的是 `channel -> rank -> bank -> row -> column` 这样的层次结构。也就是说，controller 必须决定地址中的哪些位决定列内偏移，哪些位决定行，哪些位决定 bank/channel。这个决定本质上是在回答一个策略问题：相邻地址到底应该尽量留在同一 row 以提高 row hit，还是尽量打散到不同 bank/channel 以提高并行度？

如果把更多低位分给 `column`，那么连续地址更容易留在同一 row 内，只是列偏移在变化。这通常有利于提升 row locality，因为顺序访问更可能形成长 row-hit 序列。但代价是，如果 workload 本身已经流式且并行度高，你可能把太多流量都压在少数 bank 上，导致 bank hotspot。反过来，如果把一些较低位更早切给 `bank` 或 `channel`，相邻地址会更快被打散到不同 bank/channel，bank-level parallelism 和 channel balance 可能更好，但同一 row 连续命中的机会会减少。也就是说，地址映射天然是在 `row reuse` 和 `resource striping` 之间做 trade-off。

举一个极简对照会最直观。假设有一串顺序 cache line 访问：

```text
A0, A1, A2, A3, A4, A5, ...
```

在映射 `Map X` 下，也许它们变成：

```text
A0 -> bank0 row10 col0
A1 -> bank0 row10 col1
A2 -> bank0 row10 col2
A3 -> bank0 row10 col3
```

这意味着极强的 row locality，但并行度较低。另一种 `Map Y` 下，也许同样序列被打散为：

```text
A0 -> bank0 row10 col0
A1 -> bank1 row22 col0
A2 -> bank2 row7  col0
A3 -> bank3 row18 col0
```

此时 bank parallelism 很好，但单 bank 内 row hit 机会明显更少。哪种更优，根本取决于你的 workload、controller 策略和系统目标，而不是哪种“更先进”。

这也解释了为什么映射必须和 FR-FCFS、page policy 一起理解。FR-FCFS 喜欢 row hit，如果映射天然保住了更多同 row 连续性，它就更容易吃到收益；close-page 或随机访问负载下，过强的 row-local 映射反而可能把大量请求压在少数 bank 上，让冲突更严重。换句话说，地址映射不是单独的预处理步骤，而是在决定 controller 后续能看到什么样的优化机会。

映射还直接影响 `bank hotspot`。如果多个活跃流、不同行为模式的 master 恰好在某种映射下不断打到同一 bank，即使系统里其他 bank 很空，那个 bank 也会被排队、冲突和 refresh 影响压得很重。表面上看是“内存带宽没打满”，实则是映射把流量塑形成了坏的空间分布。常见误解是把热点归咎于 DRAM bank 数不够；很多时候 bank 数够，只是映射让你没用上。

这在多 master 场景下尤其关键。CPU 流、DMA 流、GPU 流、NPU 流看到的是不同粒度和不同节奏的地址序列。某种对单一流很好的映射，对混合负载未必好。比如把相邻地址 aggressively striping 到 bank/channel，也许对大流量带宽型访问很好，但对一条希望保住 row locality 的控制流或 latency-sensitive 请求却可能不友好。也就是说，映射策略天然具有 workload 偏好，而不是 universally optimal。

还有一个常被低估的点：地址映射实际上在改写 refresh 与写排空的冲击形状。因为 refresh 和 write drain 的影响都是在 bank/channel 这些结构上发生的，如果某个 workload 的热地址被映射得过于集中，那么 refresh 一旦打到那个热点 bank，体验会非常糟；若映射更均衡，refresh 干扰可能被局部化得更好。同理，写流若被映射得更分散，write buffer 排空时也更有机会利用多 bank 并行。换句话说，映射不只影响 row hit，还在塑造所有“共享资源碰撞”的空间分布。

从工程实现角度看，映射也不是只有一种教科书方案。控制器可以选择不同位交织顺序、不同 channel striping 粒度、甚至引入某种 hash 或 XOR 混合，来避免简单线性地址模式在物理结构上形成过于规律的热点。引入这类变换的目的并不是“把映射做复杂”，而是让一些常见访问模式更平均地散布到 bank/channel 上。不过它也不是免费午餐：一旦过度打散，局部性可见度会下降，row-hit-rate 可能被牺牲。

因此，地址映射从来不是“切位正确就行”，而是一个真正的系统策略。它在把程序地址映射成 DRAM 物理地址的同时，也在替 workload 选择“以后更像 row-friendly、还是更像 bank-friendly；更像局部复用、还是更像宽条带分发”的命运。后面系统里看到的有效带宽、bank 冲突、row hit、甚至 QoS 现象，很多都是它早早埋下的结果。

如果要压缩成最实用的一句判断，那就是：地址映射决定的是请求流在 DRAM 结构中的几何形状。你不是在给地址贴标签，而是在决定它们在 channel/rank/bank/row/col 空间里怎样聚、怎样散、怎样相撞。因此它一定是策略问题，不是小实现细节。

## 一句话理解

地址映射的本质，是把程序的一维地址流投影成 DRAM 的多维结构访问形状；它直接决定请求更像“留在同一 row 反复命中”，还是“被打散到不同 bank/channel 并行推进”。

## 建模启示

在模型里，地址映射不应被隐藏在 `addr -> bank,row,col` 的固定函数后面，而最好作为可替换策略显式存在。因为一旦你想比较 workload 行为、controller 政策或多 master 干扰，就需要改映射而不仅仅改请求流。

一个最小可用的抽象可以写成：

```text
AddressMappingPolicy {
  scheme: enum { ROW_LOCALITY_FIRST, BANK_STRIPING_FIRST, XOR_HASHED }
  channel_bits: bit_range
  bank_bits: bit_range
  row_bits: bit_range
  col_bits: bit_range
}
```

配合一个映射函数：

```text
map(addr, policy) -> {channel, rank, bank, row, col}
```

如果只关心粗粒度带宽，可以把映射效果折成两个经验指标：`row_hit_rate` 和 `bank_balance_score`；但只要你要比较不同 access pattern，或要解释“为什么两个 workload 在同一 DRAM 上表现差很多”，映射策略就应该显式保留。因为它决定的不是一个小常数，而是后续整个调度空间的形状。

一个实用的观测量集合可以直接定义成：

```text
ObservedMappingEffects {
  row_hit_rate: float
  bank_hotspot_score: float
  channel_balance_score: float
}
```

这三个量虽然简化，但已经足以把“映射只是实现细节”这个误解彻底打掉。
