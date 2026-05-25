# 系统视角

上级：[`RAM/wiki/`](../)
相关：[Memory Controller](../06-memory-controller/README.md), [AI 芯片内存架构](../09-ai-chip-memory-architecture/README.md)

## 这页在回答什么问题

前面几章已经把 SRAM、DRAM、协议和 controller 分别拆开讲清了，这一章要回答的是：当这些部件重新拼回同一个系统后，workload 实际看到的带宽、延迟、局部性和瓶颈形状是怎样被共同塑造出来的。就像你分别学会了发动机、变速箱、悬挂和轮胎的工作原理，但把它们装回同一辆车上之后，真正的驾驶体验——加速感、过弯极限、油耗——是由这些部件的配合方式决定的，而不是由其中某一个单独决定。也就是说，这里不再主要问“某个器件为什么这样设计”，而开始问“多个层次一起工作时，系统为什么会像今天这样表现”。

## 正文

到这里，存储器话题终于要从“器件与协议解释”进入“整机行为解释”了。前面你已经分别理解了 SRAM 为什么快但贵、DRAM 为什么大但上下文敏感、DDR 家族为什么按不同系统目标分叉、memory controller 为什么会直接塑造有效性能。现在真正困难也最有价值的部分来了：这些机制叠在一起后，系统对 workload 暴露出的并不是一组孤立属性，而是一套层层相互作用的行为。

例如，CPU 看到的一次 load miss，不只是“cache 没命中，去 DRAM 读一下”这么简单。它后面可能牵出 cache 的 tag/data 路径、controller 的地址映射、某个 bank 当前 open row 是否匹配、刷新是否刚好在挡路、总线是否处于写排空窗口，以及其他 master 是否也在抢同一条通路。NPU 看到的一次 tile 供数不足，也不只是“HBM 带宽不够”，而可能是片上 SRAM banking 没切好、DMA 节拍没对齐、外存 controller 为别的流量保了优先级、或总访问模式根本没把 row locality 用起来。系统层的意义，就在于把这些先前分散的局部机制重新组装成 workload 能感知的因果链。这就像医生诊断——心率、血压、血糖分别看都在正常范围内，但它们的组合和相互影响才能告诉你病人是不是真的健康。

因此，这一章的结构会从几种最稳定的系统问题出发，而不是从具体器件名词出发。`bandwidth-vs-latency-fundamental.md` 先回答最常见也最容易被说空的话题：为什么带宽和延迟不能被当作同一个优化方向。`effective-bandwidth-vs-peak.md` 接着追问，为什么规格书上的峰值带宽很少直接兑现到真实程序。`cache-dram-coordination.md` 则把片上局部性层和片外主存层接起来，说明 miss 之后到底会发生什么。`numa-multi-channel-multi-socket.md` 把问题继续扩展到更大的系统资源图上，讨论扩带宽为什么几乎总伴随更复杂的拓扑代价。

后面的 `memory-hierarchy-as-system.md` 和 `why-systems-choose-different-memory.md`，会进一步把视角从“一个控制器怎么调”扩展到“整个系统为何要这样分层”。也就是说，我们不再把 register file、cache、scratchpad、DDR、HBM 分别当作几个对象去背，而是要看它们在距离、容量、带宽和管理语义上如何构成一张互补网络。压轴的 `sram-vs-dram-access-pattern.md` 会回到最开始那条主线，把前面 SRAM 与 DRAM 的全部差异收成真正的系统判断：为什么同样叫“访问内存”，在 SRAM 上和在 DRAM 上的代价曲线完全不同。

这一章还有一个很重要的边界：它讨论的是“系统如何感知并使用这些内存层次”，而不是再重复某一层的物理细节。比如带宽与延迟的讨论，不会重新解释 6T cell 或 1T1C cell 的电路，而会直接用前面的结论去解释为什么大容量层次几乎天然离计算更远、为什么高带宽路径常常以更高前置成本为代价。换句话说，本章默认前面的基础已经成立，然后把这些基础抽象成系统层的行为变量。

这也是从建模角度看非常关键的一步。前面的章节大多在回答“某类资源自身有什么状态”；这一章开始更多回答“这些资源之间通过什么拓扑和交互关系塑造端到端行为”。因此，从这里开始，`Resource / Topology / Interaction / Capability` 这套抽象会更自然地浮现出来。比如：

- `Resource`：cache、scratchpad、HBM channel、DDR controller、NoC path
- `Topology`：谁和谁之间隔着几层、几条通道、几级互连
- `Interaction`：load miss、DMA fill、writeback、burst transfer、bank conflict
- `Capability`：带宽上限、延迟下限、并行服务数、可预测性边界

这套视角的好处，是它不会把存储层次误看成几块孤立容量，而会直接逼你去看“端到端一次数据搬运要穿过哪些资源，在哪些地方最容易排队，哪些能力只是峰值而不是可持续能力”。

从系统设计角度看，这一章还会不断提醒你一个容易被忽视的事实：很多性能瓶颈并不是单一资源”不够大”，而是资源之间的相互错配。就像一支乐队，每个乐手单独听都很棒，但如果鼓手打的是 4/4 拍、吉他弹的是 3/4 拍，合在一起就是噪音。比如有时 DDR 峰值带宽足够，但 cache line 行为和地址映射不匹配；有时 HBM 总带宽很高，但实际被片上 SRAM/NoC 节拍卡住；有时 NUMA 总容量很大，但远端访问把 tail latency 拉爆。系统层的价值，就在于把这种“单点都不算差，组合起来却很难看”的现象解释清楚。

所以，这一章真正的任务不是新增更多名词，而是把前面所有局部知识变成一张统一的系统地图。读完之后，你应该能从 workload 角度描述一条访问路径：它先经过哪一级 SRAM 形态，miss 后如何被送进哪种 DRAM 路线，再由怎样的 controller 和拓扑决定最终呈现出什么延迟、带宽和抖动。只要这张地图立住，后面进入 AI 芯片专章时，很多“为什么要这么设计 buffer 和外存”都会自然落位。

## 阅读顺序

建议按下面顺序阅读本目录：

1. [带宽与延迟：为什么不能兼得](./bandwidth-vs-latency-fundamental.md)
2. [峰值带宽 vs 有效带宽：损失发生在哪里](./effective-bandwidth-vs-peak.md)
3. [Cache 和 DRAM 如何协同——miss 之后发生了什么](./cache-dram-coordination.md)
4. [多通道、多 socket、NUMA：扩展带宽的代价](./numa-multi-channel-multi-socket.md)
5. [把 register/cache/scratchpad/DRAM/HBM 看作一个系统](./memory-hierarchy-as-system.md)
6. [SRAM 和 DRAM 在访问模式上的根本区别（压轴对比）](./sram-vs-dram-access-pattern.md)
7. [MCU/CPU/GPU/NPU 选择不同存储器的逻辑](./why-systems-choose-different-memory.md)

如果你这次主要想补“为什么系统里的内存表现总和器件参数表不一样”，优先看 1 -> 6。若你的重点是不同系统为什么选不同路线，再接着看 7。

## 一句话理解

这一章要把前面分开讲的 SRAM、DRAM、协议和 controller 重新拼回一套系统行为图，解释 workload 实际看到的带宽、延迟和瓶颈是如何由多层资源共同塑造出来的。

## 建模启示

从这里开始，模型最好从“单资源状态机”提升为“多资源交互图”。也就是说，不能只分别给 cache、controller、HBM 或 DDR 填参数，而要显式表达它们之间的连接关系、事务流和排队点。否则模型只能回答局部资源是否够快，回答不了端到端瓶颈在哪里。

一个适合作为本章各页公共底座的抽象草图可以是：

```text
MemorySystemGraph {
  resources: list<ResourceNode>
  links: list<ResourceEdge>
  transactions: list<TransactionType>
}

ResourceNode {
  id: string
  kind: enum { RF, CACHE, SCRATCHPAD, MC, DDR, HBM, NOC_LINK }
  capacity: object
  service_limits: object
}

ResourceEdge {
  src: ResourceId
  dst: ResourceId
  latency_cycles: int
  bandwidth_bytes_per_cycle: int
}
```

一个最小事务流可以写成：

```text
LoadMiss:
  L1 -> L2 -> LLC -> MC -> DRAM -> MC -> LLC -> L1
```

如果只关心很粗的系统趋势，这种图可以非常抽象；但只要你要解释“峰值带宽为什么没兑现”“为什么多通道后 tail latency 变坏”“为什么 NPU 还是 memory-bound”，这层显式的资源图就必须存在。因为从系统层开始，瓶颈经常不属于某一个节点，而属于多节点之间的交互形状。
