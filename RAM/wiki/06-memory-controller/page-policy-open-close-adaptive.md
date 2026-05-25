# Open、close、adaptive page policy 的权衡

上级：[Memory Controller](./README.md)
相关：[命令调度：FR-FCFS 及其变体](./command-scheduling-fr-fcfs.md), [SRAM 和 DRAM 在访问模式上的根本区别](../07-system-architecture/sram-vs-dram-access-pattern.md)

## 这页在回答什么问题

一行被激活之后，到底应该尽量继续保持打开，还是尽快预充关掉，为下一次潜在访问让路。更准确地说，page policy 的本质不是一个简单开关，而是 controller 在对未来访问模式下注——就像赌场里押大押小：你是赌”后面还会继续命中当前 row”（押大，open-page），还是赌”更可能很快要换别的 row”（押小，close-page）。押对了赚便宜，押错了赔更多。

## 正文

理解 page policy，最稳的起点是先记住 row buffer 的本质：它不是一个独立小 cache，而是当前 bank 已打开行的工作副本。只要这一行还开着，后续命中它的请求就能走便宜得多的 row-hit 路径；但只要未来请求更可能落到别的 row，那么继续留着当前 open row 反而可能制造 row conflict，让下一笔访问多出 `PRE -> ACT` 这条昂贵切换链。于是 controller 面前会一直存在一个无法回避的问题：`当前这行还值不值得继续留？`

`Open-page policy` 的思路最直接：假设当前打开的 row 后面还有价值，所以尽量保持它开启，除非后续请求明确需要换行。这种策略天然偏爱行局部性强的访问模式。例如顺序扫描一个大数组、流式读一个长 cache line 序列、或某些映射后连续地址确实落在同一 row 上时，open-page 能把一次 activate 成本摊给更多列访问，让 FR-FCFS 也更容易顺着 row-hit 一路吞吐最大化。也就是说，open-page 是在押注”未来请求会重用当前 row”。这就像你在做饭时把调料瓶全摆在灶台上——如果接下来几道菜都用同样的调料，伸手就拿，非常方便；但如果下一道菜完全换了口味，满灶台用不上的瓶子反而挡路。

`Close-page policy` 则是另一种下注方式：别对未来过于乐观，当前访问结束后尽快把 row 关掉，让 bank 回到更中性的可切换状态。这样做的好处是，如果后续请求大概率来自别的 row，那么 bank 就不必背着一个“已经打开但很快会冲突”的状态，可以更快切换到新 row。它对随机访问、低行局部性或 bank 内地址跳动频繁的工作负载更友好，因为它在主动减少“错留 open row”带来的冲突成本。换句话说，close-page 不是在追求命中更多，而是在避免押错注之后付出更重的 row-conflict 代价。

这两者的胜负，根本不在策略本身高不高级，而在未来访问模式到底长什么样。可以用一个简单对照把直觉拉清：

```text
If next requests are likely same row:
  open-page wins
  ACT cost is amortized across many column accesses

If next requests are likely different rows:
  close-page wins
  future switch pays less leftover row conflict penalty
```

这里最容易犯的错误，是把 open-page 理解成“总是更聪明”，因为它更会利用 row-hit；或者把 close-page 理解成“总是更保守”，因为它把行早早关掉。实际上，两者都只是在不同 workload 假设下做最优响应。常见误解是觉得 row-hit 总是越多越好；但如果为了守住当前 row 而让其他更急、更广泛的请求不断形成 conflict，系统整体可能反而更差。

看一个最小例子会很直观。假设 bank0 当前打开 row10，队列接下来可能有两种模式：

```text
Case A:
  bank0 row10 col1
  bank0 row10 col9
  bank0 row10 col17

Case B:
  bank0 row10 col1
  bank0 row22 col3
  bank0 row7  col8
```

在 `Case A` 里，open-page 显然是好主意。你继续保持 row10 开着，后两笔都能直接 row-hit，昂贵的 ACT 被充分摊薄。在 `Case B` 里，留着 row10 的收益几乎只存在于第一笔之后的极短瞬间，后面很快就会碰到 row22 和 row7；如果你一味 open-page，后续请求几乎必然变成 conflict。此时 close-page 提前清场，可能反而让整体时序更顺。

但真实系统里，controller 并不会提前拿到完整未来。它只能根据已有队列、历史统计、源 master 特征、地址分布甚至访问类型，去猜“未来更像 Case A 还是 Case B”。这就是为什么说 page policy 本质上是在押注未来访问模式，而不是在切换某个固定常量。只要 workload 变化，最优下注就会变化；只要地址映射变化，同样的程序地址流对应的 row locality 也可能变化。

这也说明了 page policy 和 FR-FCFS 的紧耦合关系。FR-FCFS 擅长利用当前已经 ready 的 row-hit，而 open-page 则是在给 FR-FCFS 创造更多 row-hit 机会；反过来，close-page 会减少这类机会，但也让某些未来 row 切换更便宜。换句话说，FR-FCFS 决定“当前 ready 的请求里先吃哪一个”，page policy 决定“未来 ready 的请求分布长什么样”。两者不能分开理解。

为什么后来会出现 `adaptive page policy`，原因也很自然：真实 workload 很少是永久稳定的一类模式。某些阶段强局部、某些阶段高度随机；某些 master 像流式读，某些 master 像稀疏访问；有些地址区域天然适合开着，有些一开就马上 conflict。既然未来模式不是单一分布，那么固定 open 或固定 close 都会在另一部分场景里押错注。adaptive policy 的目标，并不是发明第三种神奇规律，而是想办法根据队列观察、历史 hit/miss 行为、PC/source 特征或简单阈值，动态决定当前这一行更适合继续保持还是尽快关闭。

一个非常粗化的 adaptive 逻辑，可以写成：

```text
if recent_row_hits_high and queue_has_same_row_candidates:
    keep_row_open
else:
    precharge_early
```

当然，真实实现可能更复杂，会看更长历史、分 bank 统计、按源流分类、甚至配合 QoS 目标。但其底层思想都一样：不要用一种固定 belief 去解释所有 future access pattern。

这里还必须把“open/close”与“auto-precharge”区分开。open-page/close-page 是策略层概念，讨论的是 controller 整体想保留还是尽快释放 row 状态；auto-precharge 则是某些具体命令发出时附带的接口机制，用来在某次列访问后自动安排预充。前者是更高层的行为倾向，后者是实现这个倾向的一种工具。常见误解是把它们混成同一层。

从系统性能角度看，page policy 直接塑造了三个指标：row-hit-rate、row-conflict-rate 和尾延迟形状。open-page 通常提升第一项，但若工作负载不配合，第二和第三项会恶化；close-page 则可能牺牲一些命中收益，换来更稳定、更不易长尾的访问分布。对于强调吞吐的 GPU/NPU 大流量访问，若映射和访问模式可控，open-page 往往很有吸引力；对于随机控制流、混合多 master 或实时敏感流量，过于激进的 open-page 可能反而把系统拖进难看的 conflict 与 starvation 模式。

所以，本页真正要建立的不是“open 比 close 好”或反过来，而是更具体的判断：page policy 的实质，是 controller 在用 bank 状态为未来请求下注。下注对了，row-hit 会像被放大一样涌现；下注错了，当前 open row 就会从资产变成负债。adaptive policy 的意义，也正是在承认这个下注没有放之四海而皆准的答案。

## 一句话理解

Page policy 的本质，是 controller 在赌未来访问究竟会继续重用当前 row，还是更可能很快切到别的 row；open-page 赢在行局部性强，close-page 赢在行切换频繁。

## 建模启示

在模型里，page policy 不应只是一个布尔开关，而应该影响 bank 何时从 `OPEN(row)` 状态转回 `CLOSED`。这意味着它至少要显式作用于 `row_lifetime` 或 `precharge_decision`，而不是只通过一个静态 row-hit-rate 参数间接体现。

一个最小可用的策略抽象可以写成：

```text
PagePolicy {
  mode: enum { OPEN, CLOSE, ADAPTIVE }
  hit_threshold: float
  idle_close_cycles: int
}
```

对应状态转移逻辑可以写成：

```text
if mode == OPEN:
    keep row open until conflict or explicit close
elif mode == CLOSE:
    precharge after service completes
else:
    precharge based on recent row-hit evidence / queue lookahead
```

如果只关心平均带宽，page policy 也许可以通过经验性 row-hit-rate 吸收进去；但只要你要研究 tail latency、多 master 交互或不同 workload 的适配程度，最好显式保留 `precharge decision` 这一层。因为很多 controller 行为的差异，并不是调度器“选谁先”，而是它是否还给未来保留了一个有价值的 open row。
