# 学习路线图

上级：[01 概览与问题定义](./README.md)

相关：[知识地图](../SUMMARY.md)、[按目标学习 DMA](./goal-oriented-navigation.md)

## 这页在回答什么问题

如果你的目标不是背概念，而是系统掌握 DMA，该按什么顺序学；以及为什么“先看寄存器和 API”通常会把注意力带偏。

## 先学角色，再学对象，再学节奏

DMA 最容易学歪的地方，是一开始就扎进驱动接口、寄存器表或某个 IP 数据手册。那样确实能很快记住若干名词，但很难解释两个更重要的问题：为什么很多系统里 DMA 比 compute 更像真正瓶颈，以及为什么不同系统的 DMA 软件接口差异这么大。

更合理的顺序是先回答“DMA 在系统里代替谁承担了什么工作”，再回答“它实际操作的对象是什么”，最后才进入“它如何以硬件节奏把这些对象组织起来”。只有这样，后面读 AXI、PCIe、NoC、HBM、local SRAM 或 completion path 时，才不会把每个现象都当成孤立细节。

## 路线 1：建立最小判断力

1. [DMA 在解决什么问题](./problem-statement.md)
2. [DMA 分类框架](./taxonomy.md)
3. [传输对象与基本语义](../02-fundamentals/transfer-basics.md)
4. [地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)
5. [DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)

这条路线的目标不是学会调优，而是先建立“一个 DMA 任务是如何从软件声明变成系统事务”的骨架。走完后，你至少应能区分 descriptor-level、transaction-level 和 software-visible completion 三层语义。

## 路线 2：学会从系统角度看 DMA

1. [缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)
2. [软件栈与编程模型](../04-programming-model/software-stack.md)
3. [同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)
4. [DMA 与 NoC](../05-system-integration/dma-and-noc.md)
5. [DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)
6. [指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)

这条路线的核心收益，是把 DMA 从“某个 IP 的接口问题”提升为“软件、互连、内存共同决定的系统问题”。如果你已经完成了 BUS、RAM、NOC 几套 wiki，这条路线会最自然，因为你会不断看到 DMA 如何把 [BUS wiki 的 AXI outstanding](../../BUS/wiki/03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[RAM wiki 的 row locality](../../RAM/wiki/06-memory-controller/address-mapping-channel-rank-bank-row-col.md) 和 NoC traffic pattern 串到一起。

## 路线 3：面向 AI / 高性能系统深化

1. [调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)
2. [Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)
3. [DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)
4. [AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)
5. [HBM 到 Tile 的数据供给链](../07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)
6. [从抽象模型到系统诊断](../06-performance-modeling/modeling-method.md)

这条路线针对的是“数据搬运优先”的系统视角。它不再把 DMA 看作附属模块，而是把 DMA 看作决定 compute 是否能持续吃到数据的执行骨架。真正的重点不是某个 burst 有多长，而是 refill、compute 和 writeback 能否形成可持续重叠。

## 学完以后你应该能回答

- 为什么某些系统里 DMA 比 compute 更像真实瓶颈
- 为什么理论带宽看着够，系统仍然会出现 stall 或 tail latency
- 为什么同一个 DMA IP 放到不同总线、不同 memory hierarchy 里效果差异很大
- 如何把一个 DMA 问题拆解到 software submit、engine scheduling、NoC、memory endpoint 和 completion path

## 常见误解

常见误解：`先学驱动 API 最务实`。实际上 API 只是某种系统契约的表面表现，过早进入 API 容易把系统问题误读成接口问题。

常见误解：`AI 加速器 DMA 比 SoC DMA 高级，所以应该先学它`。实际上 AI DMA 建立在更扎实的基本语义之上，先把 descriptor、completion、一致性和 outstanding 学清楚，后面看 AI 供数链才不会漂。

## 一句话理解

学 DMA 的正确顺序不是“先记接口”，而是 `先懂角色，再懂对象，再懂执行节奏，最后再懂系统瓶颈和建模`。

## 建模启示

学习路线本身也决定建模路线。一个稳妥的仿真推进顺序是先建 `logical transfer model`，再加 `queue/descriptor model`，最后再补 `system coupling model`。如果一开始就把 NoC、DDR、cache coherence、completion interrupt 全塞进来，模型会过早复杂；如果一直停留在理想带宽模型，又解释不了 stall 和 tail latency。

可以把学习顺序直接映射成三个模型层级：

```text
L1: transfer = {src, dst, bytes}
L2: dma_task = {descriptor, queue, outstanding, completion}
L3: system = {noc_path, mem_port, cache_visibility, consumer_ready}
```

这三个层级对应的事件复杂度逐级上升。L1 只要 `transfer_start/transfer_end`，L2 要有 `descriptor_fetch` 和 `completion_visible`，L3 则必须再加 `response_blocked`、`bank_conflict` 或 `consumer_stall` 这类系统事件。
