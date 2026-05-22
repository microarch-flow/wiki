# NPU 的存储层次：L0、L1、L2 SRAM 与 HBM、LPDDR

上级：[AI 芯片内存架构](./README.md)
相关：[把 register、cache、scratchpad、DRAM、HBM 看作一个系统](../07-system-architecture/memory-hierarchy-as-system.md), [NPU 里的 SRAM buffer：weight、activation、accumulator](../03-sram-applications/npu-weight-buffer-activation-buffer.md)

## 这页在回答什么问题

NPU 为什么往往要自定义多级片上 SRAM 层次，而不能简单复用 CPU 式 cache hierarchy；外层 HBM 或 LPDDR 又在这套层次里扮演什么角色。

## 正文

如果把 NPU 的存储层次只画成 `L0 / L1 / L2 / HBM` 这样的名字表，你很容易产生一个错觉：这不过是把 CPU 的多级 cache 换了个外形。真正的情况不是这样。NPU 里的多级片上 SRAM，往往不是为了“自动捕获一般程序局部性”而分层，而是为了把一条高吞吐数据流拆成几段更短、更可控、更可复用的搬运路径。也就是说，NPU 的层次首先是数据流拓扑，其次才是容量层级。

先从最内层看。很多 NPU 会把离 `PE` 或 `MAC array` 最近的一层叫做 `L0`，但这层通常并不像 CPU 的 L1 cache。它更像一个极近、极窄作用域、强时序耦合的数据供给点。这里放的可能是当前 tile 的一小块 activation、当前迭代最活跃的一组 weight，或者最频繁读改写的 partial sum。L0 的首要任务不是“尽量大”，而是“在阵列需要的那个拍点把正确数据喂进去”。所以它的设计常常优先考虑端口结构、bank 冲突、读改写频率、与计算阵列的布线距离，而不是抽象上的命中率。

再往外一层，`L1 SRAM` 通常开始承担 `staging + reuse reservoir` 的角色。它不像 L0 那样拍级敏感，但又不能像更远层那样允许较大抖动。很多时候，L1 是某个 `cluster`、`core tile` 或一组 PEs 的共享缓冲。它负责把来自更远层的数据整理成更适合下游消费的块状形式，同时吸收一部分重用。例如，一块权重可能在同一 cluster 内多次被不同 PE 复用；一片 activation tile 可能要被多轮卷积窗口或多个 heads 反复消费。L1 的价值就在于把这些局部高频重用截留住，不让它们频繁回到更远的层。

`L2 SRAM` 再往外时，角色通常会从“拍级供数”进一步转向“芯片内全局调度缓冲”。这一级往往容量更大、离计算更远、访问时延更高，但它可以承担几件更系统化的工作：在多个 cluster 之间分发数据、缓存来自外存的一批 tile、吸收不同计算阶段之间的生产消费错位，或者作为跨引擎共享的中转池。换句话说，L2 不一定直接决定某个 MAC 阵列这一拍有没有数据，但它决定了下游很多 L1/L0 是否能持续被填满。

如果把这三层放在一起看，你会发现它们不是简单的“大一点、慢一点、小一点、快一点”的重复，而是三种不同的职责分工：

- `L0` 负责最后一跳供数
- `L1` 负责局部重用与下游整形
- `L2` 负责芯片级 staging、共享与跨阶段缓冲

这就是为什么很多 NPU 不能简单复用 CPU 式 cache hierarchy。CPU cache 的长处，在于面对通用程序时尽量自动挖出局部性；而 NPU 的数据流往往已经足够规则，真正的问题不在“能否猜中未来地址”，而在“能否在正确时间把正确形状的数据放在正确位置”。如果你把 NPU 片上 SRAM 完全包装成传统 cache，就会引入很多对通用性有利、对高吞吐数据流却未必有利的机制，比如不必要的 tag/check/replace 行为、不透明的数据驻留状态，以及对软件/编译器较差的可控性。很多 NPU 选择更显式的 scratchpad 式层次，本质上是在用管理复杂度换更高的数据流确定性。

外层 `HBM` 或 `LPDDR` 在这套体系里的角色，也必须按这个思路理解。它们不是“更大的最后一级缓存”，而是远距离容量与带宽资源池。它们提供的是大工作集承载能力和持续供数能力，但不会直接承担拍级平滑任务。因为无论是 HBM 还是 LPDDR，它们都具有外存共同特性：访问有 burst 粒度、启动开销不为零、带宽兑现依赖调度和请求形状、延迟和局部性对实际行为仍有影响。也就是说，外存可以很强，但它不是用来直接喂阵列每个周期的。它更像一个高通量但不够细粒度的上游水库，片上 SRAM 层次负责把这个水库的水变成下游能连续喝的小水流。

这也解释了为什么不同外存路线会推回片上层次设计。如果外层是 `HBM`，芯片往往会有更高的总外带宽预算，于是 L2/L1 设计可以更大胆地依赖持续 refill，但也必须面对更多并发流的分发问题；如果外层是 `LPDDR`，总带宽和带宽密度往往更紧，片上 SRAM 就更需要承担“尽量少回外面”的压力，于是 weight 驻留、tile 复用和 buffer 容量选择会更激进。换句话说，片上层次和片外路线不是两个独立模块，而是一套闭环：你选了什么外存，基本就决定了片上哪里必须更强；你限制了多少片上 SRAM，又会反过来决定外存流量有多粗。

在真实设计里，`L0/L1/L2` 的边界也不总是固定的。有些架构会把某一层做得很薄，强调流式 through-put；有些会把中间层做得较大，强调跨 tile 或跨算子重用；有些甚至不会显式命名成 L0/L1/L2，而是直接叫 operand buffer、shared SRAM、global buffer。名字不统一并不重要，重要的是它们是否覆盖了几种不可省的功能：近阵列供数、局部重用截留、芯片级 staging、外存回填对齐。如果某项功能缺位，系统就会在别处以更高成本把它补回来。

从 `Topology` 视角看，NPU 的内存层次更像一张多级供水网络，而不是一棵纯容量树。L0 连接单个 PE 或小阵列，L1 连接局部 cluster，L2 连接全芯片或大分区，HBM/LPDDR 位于更远的外部资源层。每一层不只提供容量，还决定了数据在芯片内部能被哪些计算单元共享、共享时需要经过哪些仲裁点、以及流量高峰会在哪些边界撞车。只看“有几 MB SRAM”会漏掉最关键的事：这些 MB 是分散在多少 bank、挂在哪些 cluster 上、是否能被多个数据角色并发使用。

这也说明了 NPU 内存层次设计里一个很常见、但经常被低估的 trade-off：`局部化` 和 `共享化` 的冲突。把 SRAM 做得更局部，离算力更近，访问更便宜，但容量碎片化、跨单元共享变难；把 SRAM 做得更全局，容量利用率和共享灵活性更好，但每次访问更远、仲裁更多、峰值带宽更难分发。L0/L1/L2 的真正意义，就是沿这条 trade-off 曲线做了几次有意的分段，而不是只是在芯片上画了几个名字不同的 buffer。

因此，本页真正要建立的不是“NPU 也有多级缓存”这种表面类比，而是更准确的判断：NPU 的多级 SRAM 层次，是为了把外存的粗粒度高吞吐资源转译成阵列可持续消费的细粒度稳定数据流。外层 HBM 或 LPDDR 提供远端容量与总带宽，内层 L2/L1/L0 负责在距离、作用域、复用和并发之间做逐级变换。只有这样理解，后面谈 weight buffer、double buffering、片上带宽预算时才不会变成孤立技巧。

## 一句话理解

NPU 的 `L0/L1/L2 SRAM + HBM/LPDDR` 不是 CPU 式 cache 名字平移，而是一套把远端粗粒度外存流量逐级变换成近阵列稳定供数的分层数据流拓扑。

## 建模启示

在模型里，不要把 `L0/L1/L2` 只当成三个不同容量和延迟的桶。更关键的是给每一级附上 `scope` 和 `role`，因为同样是 1 MB SRAM，挂在单 cluster 边上和做成全局共享池，系统行为会完全不同。

一个够用的分层抽象可以写成：

```text
NpuMemoryLevel {
  name: str
  level: enum { l0, l1, l2, offchip }
  scope: enum { pe, cluster, chip, external }
  capacity_bytes: int
  read_bw_Bps: float
  write_bw_Bps: float
  bank_count: int
  resident_roles: set { weight, activation, accumulator, metadata }
  refill_from: optional<NpuMemoryLevel>
}
```

然后显式表示层与层之间的供数关系：

```text
RefillPath {
  src_level: str
  dst_level: str
  bandwidth_Bps: float
  startup_latency_ns: float
  burst_bytes: int
  supports_overlap: bool
}
```

真正会影响结论的状态至少有四类：

- 某类数据当前驻留在哪一级
- 某一级是否被多个 cluster 或 data role 共享
- refill 是否能和当前计算重叠
- 下一级消费速度是否会把上一级拖成热点

如果这些状态在模型里都不存在，那么 `L0/L1/L2` 只会变成三个“延迟不同的数组”，无法反映真实 NPU 内存层次为什么这样设计。
