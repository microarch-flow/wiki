# Bank group、prefetch、burst：高频接口下的必然演化

上级：[DRAM 基础](./README.md)
相关：[为什么要在时钟两边都传数据](../05-dram-protocol-families/why-double-data-rate.md), [DDR1 到 DDR5：每一代的核心改变是什么](../05-dram-protocol-families/ddr-generation-evolution.md)

## 这页在回答什么问题

为什么 DRAM 在容量继续做大、接口继续提速的过程中，会演化出 prefetch、burst 和 bank group 这些看起来很“协议味”的结构。更准确地说，这些机制到底在桥接什么矛盾，为什么它们不是可有可无的增强项，而是 cell 速度与 I/O 速度脱节之后的必然结果。

## 正文

到了这一章这里，DRAM 的基本矛盾已经很清楚了。1T1C cell 提供了高密度，但 cell 很弱；整行感测和 row buffer 提供了访问窗口，但 row 打开成本高；bank 提供了阵列级并行，但并不自动等于高速接口吞吐。接下来会出现的 prefetch、burst 和 bank group，本质上是在处理另一层越来越尖锐的矛盾：`DRAM core`，也就是 cell、sense amp 和 row buffer 这一侧的工作节奏，并不能简单线性跟上外部 I/O 接口的提速需求。

如果没有这层矛盾，最理想的情况当然是：core 每做一次细粒度访问，I/O 就同步送出同样粒度的数据，二者节奏一致，结构简单。但现实不是这样。cell 侧受位线感测、恢复、阵列尺寸和功耗限制，内部访问频率和能在单次感测后稳定取出的数据粒度都有限；而系统层又越来越希望引脚带宽继续增长。于是工程上会自然想到一个桥接办法：既然 core 侧不适合每拍都去碰一次原始 cell，那就让 core 每次多准备一点数据，再由 I/O 侧用更快节奏把这块数据分几拍送出去。这就是 prefetch 和 burst 背后的基本思想。

先看 `prefetch`。这里的 prefetch 不是 CPU 里那种“猜未来地址”的预取，而是 DRAM 内部的一种宽度转换机制。它表达的是：当一行已经被打开，core 并不是每次只从 row buffer 中取出最窄那一点点数据直接送到引脚，而是先在内部取出一个更宽的块，比如 4n、8n、16n 这类粒度，再交给 I/O 边界逻辑。这样做的结果，是外部接口可以在更高的 transfer rate 下持续输出数据，而内部阵列不需要按同样高的频率重新访问 row buffer。常见误解是把 prefetch 读成“缓存更多未来数据”；实际上，它更像一个把“内部较宽、较慢”的数据块，转成“外部较窄、较快”的节奏适配器。

再看 `burst`。一旦内部已经取出这样一个更宽的数据块，外部接口自然不会一拍只送其中一小部分然后停住，而会连续若干拍把它吐完。这个连续发送窗口就是 burst。也就是说，burst 不是独立于 prefetch 的另一个随机特性，而是 prefetch 在引脚侧的时间展开形式。内部先攒一块，外部再顺着这块连续发出去，二者是一体两面。你可以把 prefetch 看成“空间上一次取更宽”，把 burst 看成“时间上连续发多拍”。

一个简化的数据流可以这样看：

```text
Core side (row buffer)      : [ D0 D1 D2 D3 D4 D5 D6 D7 ]
Prefetch latch / boundary   : [ D0 D1 D2 D3 D4 D5 D6 D7 ]
I/O burst over time         : D0 -> D1 -> D2 -> D3 -> D4 -> D5 -> D6 -> D7
```

如果外部总线更窄，而目标带宽又更高，那么唯一现实的做法就是让 I/O 在时钟两边沿、多个拍子里持续搬运这块预取出来的数据。这也是为什么后面 DDR 的“双边沿传输”和 burst length 会和这里直接连起来。

但只靠 prefetch 和 burst 还不够，因为外部接口频率继续提高后，另一个问题会暴露出来：即使 row buffer 侧已经把一块数据准备好了，不同 bank 发出的命令和数据流也会开始在更高速度下互相挤压。你会希望有更多阵列并行来喂接口，但又不能让所有 bank 在高频下完全无约束地争同一组内部路径和 I/O 边界资源。于是 `bank group` 出现了。它可以理解为一种更细粒度的银行分组结构，用来在继续增加 bank 数和并行度的同时，把某些内部资源、时序约束和命令间隔组织得更可控。

这里最重要的不是记住某一代 DDR 有多少 bank group，而是理解它表达的工程信号：当 bank 数变多、I/O 变快之后，“所有 bank 平等且完全同质共享”的简单模型不再够用了。控制器和协议开始需要显式区分“同一 group 内的访问”和“跨 group 的访问”，因为它们在时序和资源争用上不再等价。也就是说，bank group 是高频接口时代，对 bank-level parallelism 再细分一次的结果。

为什么这种再细分是必要的，可以从两个角度理解。第一，cell/core 侧的并行度要继续提高，否则外部高速 I/O 会挨饿；第二，I/O 侧过快时，某些局部阵列或内部数据通路不能像理想无限资源那样无代价并发。因此协议层必须把“可以更紧密交错的访问”和“需要更保守间隔的访问”区分开来。bank group 提供的，就是这种区分的组织边界。它不是在改变 DRAM 是 banked 阵列这一事实，而是在高带宽时代给 bank 并行再加一层结构化管理。

把这三者连起来看，演化逻辑其实非常统一。因为 cell 侧慢、弱、感测成本高，所以不可能每送一点数据都重新碰一次 core，于是产生 prefetch；因为预取出来的是更宽的数据块，所以外部自然连续多拍发送，于是形成 burst；因为要让越来越多 bank 在越来越快的接口下持续供数，又不能把所有内部时序假设都压垮，于是出现 bank group。这整条链条，都是在桥接“内部阵列节奏”和“外部带宽需求”之间的剪刀差。

这也解释了为什么 “为什么不能一直加频率” 这个问题，不能只用板级信号完整性去回答。即使先不看封装和布线，DRAM 内部 core 与 I/O 的节奏失配本身也在推动结构演化。提高外部数据率，如果没有更深的 prefetch、更合理的 burst 组织和更细的 bank 并行管理，最终只会让 I/O 边界越来越空转，或者让内部时序约束变得不可收敛。也就是说，高频不是一个单独变量，它会反过来改写内部组织。

从系统性能角度看，prefetch / burst / bank group 的存在还意味着一件事：DRAM 的“最自然访问粒度”并不是单个字节或单个字，而更接近某个 burst 片段和某个行内局部窗口。这会影响控制器如何聚合请求、cache line 大小如何与外部 burst 对齐、以及连续访问是否真能高效摊薄 activate 成本。后面到了协议和控制器章节，这些问题都会进一步展开。

所以，这一页真正要建立的不是三组术语定义，而是一条演化路径：当高密度 DRAM core 无法与高速 I/O 同步提速时，系统只能通过“内部宽取、外部快发、bank 再分层”来桥接两者。这也是 DDR 家族后续代际演化的底层逻辑之一。

## 一句话理解

Prefetch、burst 和 bank group 本质上都是在桥接 DRAM core 慢而宽、I/O 快而窄的节奏剪刀差：先在内部一次取更宽，再在外部连续多拍发送，并对 bank 并行做进一步结构化管理。

## 建模启示

对建模来说，这一页最重要的结论是：不要把 DRAM 简化成“收到一个读请求就立刻按请求宽度吐数据”。更准确的抽象应该至少区分 `core-side fetch width` 和 `I/O-side transfer width`，并显式建模一个 burst 传输窗口。否则模型会错误低估突发粒度、总线占用时间和 bank 并行约束。

一个最小可用的抽象草图可以是：

```text
DramTransferModel {
  core_prefetch_words: int
  burst_length: int
  io_words_per_beat: int
  bank_groups: int
  same_group_gap_cycles: int
  cross_group_gap_cycles: int
}
```

对应事件流可以写成：

```text
event CoreChunkReady(bank_id, row_id, chunk_id)
event BurstTransferStart(req_id, bank_group_id)
event BurstBeat(req_id, beat_idx)
event BurstTransferDone(req_id)
```

如果只关心非常粗粒度带宽，可以把 `core_prefetch_words * burst_length` 折成一个平均事务大小；但只要你要分析 cache line 对齐、数据总线占用、或者不同 bank/bank group 的交错效率，就最好显式保留 burst 级事件。因为很多“理论带宽”落不到实测带宽的问题，正是发生在这层宽度与时间的桥接上。
