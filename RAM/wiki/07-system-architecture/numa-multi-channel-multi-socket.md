# 多通道、多 socket、NUMA：扩展带宽的代价

上级：[系统视角](./README.md)
相关：[地址映射：物理地址到 channel、rank、bank、row、col 的拆分艺术](../06-memory-controller/address-mapping-channel-rank-bank-row-col.md), [MCU、CPU、GPU、NPU 为什么选择不同存储器](./why-systems-choose-different-memory.md)

## 这页在回答什么问题

为什么系统一旦想继续扩容量或扩外存带宽，几乎总会走向多通道、多 socket 和 NUMA 这类拓扑结构。更关键的是，这些结构带来的不只是“更多资源”，还会同步带来更复杂的访问距离、一致性压力、地址放置问题和软件可见代价。

## 正文

当单个 memory channel 的带宽不够、单个 socket 可挂的主存容量不够时，最自然的扩展办法似乎就是“再加几个 channel”或“再加几个 socket”。从资源总量上看，这当然有效：更多 channel 意味着更多独立的数据总线和 bank 资源，更多 socket 意味着更多本地控制器和更多物理内存插槽。但系统层真正麻烦的地方在于，存储不是一个可以无代价横向复制的纯容量池。只要开始做多通道和多 socket，访问就会从“单控制器单路径”变成“多资源、多距离、多一致性边界”的问题。

先看多通道 `multi-channel`。它最直接的价值，是把原本一条 DRAM 路径上的峰值带宽和 bank 并行度横向扩展成多份。若地址映射合适，请求流能被分散到不同 channel，那么 controller 就能同时在多个独立通道上推进事务，总带宽和可并行 outstanding request 数都明显增加。也就是说，多通道本质上是在复制 memory controller + channel + rank/bank 这一整段资源链，而不是简单多挂几颗颗粒。

但多通道的代价很快就会出现。第一，地址映射更复杂，因为你必须决定哪些地址跨 channel striping，哪些地址尽量留在局部以保 row locality。第二，channel 之间虽然逻辑独立，但上游请求流不一定能自然均匀分布，某些 workload 会把热点继续压在少数 channel 上，导致“总资源很多，实际只热一部分”。第三，更多 channel 意味着更多板级走线、更多信号引脚、更多功耗和更多内存控制状态，系统复杂度不是线性免费增长。也就是说，多通道不是“自动更快”，而是“多了更多潜在并行资源，同时多了更多需要被正确喂养的资源”。

再看 `multi-socket`。它的扩展逻辑比多通道更重，因为它不仅复制了内存资源，还复制了计算节点和一致性域。每个 socket 往往有自己的本地 controller、本地 channel、本地主存，访问本地内存通常延迟和带宽都更好；而访问另一个 socket 的内存，则必须跨 socket 互连，把请求送到对方 controller 再进入 DRAM。于是，系统不再面对单一统一内存时间，而是天然出现“本地快、远端慢”的访问差异。这就是 NUMA，`Non-Uniform Memory Access`，名字本身就说明延迟和带宽已经不再统一。

NUMA 最值得先抓住的，不是定义，而是它改变了软件和系统的默认假设。在 UMA 或单 socket 直觉里，物理地址只是一个容量空间，放在哪里都差不多；到了 NUMA，地址放置本身变成性能变量。线程跑在哪个 socket，上游页分配在哪个节点，数据结构被谁 first-touch，甚至任务调度过程中线程是否迁移，都会直接改变访问到底是本地还是远端。也就是说，NUMA 不是“硬件多了几条路”这么简单，而是在把拓扑和放置策略暴露给整个软件栈。

这也解释了为什么“多 socket = 更大带宽和容量”这句话只对总量成立，对单个任务并不总成立。若应用能很好地按节点切分数据和线程，让大多数访问都落在本地 NUMA node，那么它确实能吃到更多 aggregate bandwidth；但若应用频繁跨 socket 共享数据、线程与数据放置错位，或者 allocator 根本没管 NUMA，本来为了扩展总资源而引入的远端路径，反而会把平均延迟和尾延迟拉高。常见误解是觉得更多 socket 自动意味着单任务更快；实际上，单任务可能只在“本地性感知很强”的情况下受益。

从控制器视角再看一层，多通道和 NUMA 也会改变仲裁问题的形状。单通道时，争用主要发生在一个 controller 内；多通道时，请求是否被均匀分散变得重要；多 socket 时，不同 socket 上的 controller 还会通过互连路径间接耦合，远端访问不仅占 DRAM，还占 socket 间链路。于是系统瓶颈不再只有“DRAM 忙不忙”，而要同时看“哪个 controller 忙、哪个 channel 热、哪个互连在拥塞”。这就是为什么大系统里的内存性能分析，往往必须同时看内存控制器和 NUMA 拓扑。

可以用一个很简单的三层对照来理解扩展路径：

```text
Single channel:
  one controller, one bandwidth pool, one latency domain

Multi-channel:
  multiple bandwidth pools, same socket, same coherence domain

Multi-socket NUMA:
  multiple bandwidth pools + multiple latency domains + remote access path
```

这三层每往上走一步，资源总量都更大，但“统一性”都更弱。统一性一弱，软件和系统就必须更明确地管理放置与调度。

还有一个经常被低估的代价是 `coherence and sharing traffic`。多 socket 系统如果仍然暴露共享内存编程模型，那么缓存一致性、目录状态、远端失效和跨 socket 共享数据的同步流量都会在互连上形成额外压力。这样一来，某次远端内存访问的成本，常常不只是“远一点的 DRAM 延迟”，还可能叠加一致性维护和链路争用。也就是说，NUMA 的代价不是单一的距离成本，而是距离 + 拓扑 + 协议共同叠加。

这正是为什么很多高性能系统软件会显式 NUMA-aware：线程绑核、页面 first-touch、对象按节点分区、跨节点通信尽量批量化。它们做的本质上都是一件事：把“更大总资源”重新塑形成“对大多数关键访问来说仍尽量像本地资源”。如果不这么做，系统就会在聚合资源上获益，在单次关键访问和 tail latency 上吃亏。

从前面几章的知识回看，多通道和 NUMA 其实是在把 `address mapping`、`controller scheduling`、`workload locality` 这些问题提升到更高层。单通道里，你主要关心请求落到哪个 bank/row；多通道里，你还要关心落到哪个 channel；多 socket 里，再加上落到哪个 node，以及请求者是不是本地。这不是几个新名词并列出现，而是同一类“资源几何形状”问题不断向外扩展。

所以，这一页真正要建立的不是“多通道、多 socket 可以扩带宽”这种显然正确但不够用的结论，而是更系统的一句判断：扩展带宽和容量，几乎总意味着把统一资源拆成多个带拓扑结构的局部资源。资源总量增加了，但延迟和带宽的均匀性变差了；如果软件与映射策略不能顺着拓扑工作，新增资源很可能一半变成复杂度，一半才变成性能。

## 一句话理解

多通道和 NUMA 扩展带来的不只是更多带宽和容量，而是把内存系统从“一个统一池子”变成“多个带距离和拓扑差异的局部资源”，因此地址放置和线程放置本身就成了性能变量。

## 建模启示

在模型里，多通道和 NUMA 不应只表现为“总带宽乘以 N”。至少应显式保留 `resource multiplicity` 和 `distance asymmetry` 这两类变化，也就是：有多少个独立服务池，以及访问本地/远端资源的成本是否不同。

一个够用的资源图草图可以写成：

```text
NumaMemorySystem {
  sockets: int
  channels_per_socket: int
  local_latency_cycles: int
  remote_latency_cycles: int
  local_bw_bytes_per_cycle: int
  remote_link_bw_bytes_per_cycle: int
}
```

配合地址和线程放置：

```text
PlacementState {
  page_home_socket[page]
  thread_home_socket[thread]
}
```

请求代价至少要区分：

```text
if req.thread_home_socket == page_home_socket:
    cost = local_latency + local_mc_queue_delay
else:
    cost = remote_latency + intersocket_link_delay + remote_mc_queue_delay
```

如果只关心 very-high-level aggregate throughput，可以把多个 channel 的贡献简单加总；但只要你要分析单任务性能、尾延迟或多租户隔离，就必须显式区分 local 和 remote 路径。因为 NUMA 的关键不是“资源总和更大”，而是“资源位置开始重要”。
