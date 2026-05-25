# 概览

上级：[`RAM/wiki/`](../)
相关：[为什么存储器是体系结构里最难的部分](./problem-statement.md), [学习路径与各章节依赖关系](./learning-roadmap.md)

## 这页在回答什么问题

开始学存储器时，最容易出错的不是“不懂某个术语”，而是把不同层级的问题揉成一团。这个章节的任务，就是先把 RAM 拆成几条清晰主线，再说明后面的章节为什么要按现在这个顺序展开。

## 正文

想象你面前有一座城市的交通系统。你不能只盯着某一条高速公路去理解拥堵问题，因为拥堵可能源自匝道设计、红绿灯策略、停车场容量、甚至是早高峰的通勤模式。存储器在体系结构中扮演的角色类似——它不是一个可以独立理解的模块，而是一张牵一发动全身的网。这一章的任务，就是先把这张网的主要经线和纬线理清楚。

后面你会同时看到 `SRAM / DRAM`、`DDR / LPDDR / GDDR / HBM`、`cache / scratchpad / register file`、`DIMM / PoP / HBM stack` 这些名词。如果不先说明它们分属哪一层，讨论会很快失真。比如”HBM 比 DDR 先进”这种说法，就像说”地铁比柴油更先进”——把交通工具、燃料类型和路线规划混成了一个判断句，没有分析价值。

本章先做三件事。第一，明确为什么存储器会成为体系结构里最难收敛的部分——它同时受物理单元、互连距离、并行组织、控制策略和工作负载形状约束，就像一块橡皮筋被五只手同时向不同方向拉。第二，交代为什么 `SRAM` 和 `DRAM` 必须分成两条主线去学。两者虽然都叫 RAM，但一个用双稳态换低延迟，一个用电容存储换高密度，它们后续推导出的访问模式和系统角色完全不同——就像汽油车和电动车共享”汽车”这个名字，但动力系统、补能方式、维护逻辑全然不同。第三，建立一张分类图，把”单元类型””阵列组织””协议家族””系统角色””封装形态”拆成正交维度，避免用同一个词同时指代不同层级。

这一章之后的顺序也是刻意安排的。`02-sram-foundations` 先讲 SRAM，不是因为 SRAM 在系统里更重要，而是因为它的基本电路骨架更干净——就像学乐器先从原声钢琴开始，把锤弦、共鸣、踏板这些机械原理搞清楚，再去理解电钢琴和合成器叠加了哪些电子化复杂性。6T cell、字线、位线、sense amp、端口数、阵列划分，这些概念在 SRAM 里可以先以最小完备模型建立起来。等到进入 `04-dram-foundations` 时，再把”破坏性读出、refresh、row buffer、bank 并行、prefetch/burst”这些额外复杂性一层层叠上去，因果关系会更清楚。

`05-dram-protocol-families` 和 `06-memory-controller` 则把问题从”器件和阵列为何这样设计”推到”系统如何与它打交道”。这一步很关键：很多人会把 DRAM 的时序参数当作几组需要记忆的常数，但架构研究真正关心的是，这些常数为什么存在，控制器如何在这些约束下做调度，以及调度如何反过来决定有效带宽和尾延迟。没有这两章，前面的电路知识就像学了乐理却没练过合奏——无法落到系统建模。

`07-system-architecture` 开始把前面的零件重新拼回一套完整系统。此时重点不再是某个单元的内部结构，而是 miss 之后发生什么、bandwidth 和 latency 为什么经常相互拉扯、多通道和 NUMA 为什么既扩展资源又引入代价。`08-packaging-integration` 继续往外推，说明为什么在 HBM 和 AI 加速器时代，封装已经不是后端工艺附录，而是内存架构的一部分。`09-ai-chip-memory-architecture` 最后把整套知识压到 NPU 场景，因为片上 SRAM、片外 HBM/LPDDR、NoC 和 DMA 的关系，正是”数据搬运优先”方法论最容易落地的地方。

读这套 wiki 时应该一直带着两个问题。第一，这个机制究竟是在为哪一个物理约束或系统约束付账——每一种设计都是一张支票，关键是看它开给了谁。第二，如果把它放进 cycle-level 或 event-driven 模型里，哪些状态必须显式保留。后面每一页末尾的「建模启示」都会按这个口径写，因此本章的作用不是提供答案，而是先把问问题的方式校正过来。

## 阅读顺序

建议按下面顺序阅读本目录：

1. [为什么存储器是体系结构里最难的部分](./problem-statement.md)
2. [速度、容量、成本、功耗——四角矛盾的根源](./memory-hierarchy-tension.md)
3. [同样是 RAM，为什么 SRAM 和 DRAM 走向了完全不同的工程路径](./sram-dram-divergence.md)
4. [学习路径与各章节依赖关系](./learning-roadmap.md)
5. [RAM 家族的分类与命名体系](./taxonomy.md)

如果你只是回来快速校正术语边界，优先看 [RAM 家族的分类与命名体系](./taxonomy.md)。如果你是第一次进入整套 wiki，还是按上面的 1 -> 5 顺序读最稳。

## 一句话理解

这一章的作用，是先把存储器问题拆到正确层级上，再按“SRAM 基础 -> DRAM 复杂性 -> 协议与控制器 -> 系统与 AI 场景”的因果链往后推。

## 建模启示

对架构探索来说，这一章对应的不是某个具体硬件模块，而是一个“模型分层框架”。最少需要显式区分三类对象：`storage_primitive`，例如 `SRAM_6T`、`DRAM_1T1C`；`interface_family`，例如 `DDR5`、`LPDDR5X`、`HBM3E`；`system_role`，例如 `L1_cache`、`scratchpad`、`offchip_main_memory`。如果把这些维度提前混掉，后面的性能模型会把“单元物理限制”“协议限制”“系统使用语义”错误地折叠为一个参数表。

如果只关心性能建模，这一章可以先抽象成一张概念依赖图，而不是一组时钟级状态机。一个够用的数据结构草图如下：

```text
MemoryNode {
  name: string
  primitive: enum { SRAM, DRAM }
  role: enum { RF, CACHE, SCRATCHPAD, MAIN_MEMORY, STACKED_MEMORY }
  interface: enum { NONE, DDR, LPDDR, GDDR, HBM }
  parent_links: list<MemoryNodeId>
  key_constraints: list<string>
}
```

这个层级图本身不产生周期事件，但它会决定后续每一类模型该接入哪些状态变量。例如 `primitive=DRAM` 就意味着后续必须考虑 `open_row`、`refresh_due`、`bank_busy_until` 这类状态；而 `role=SCRATCHPAD` 则意味着后续需要显式建模软件调度或 DMA 搬运事件，而不是默认存在 cache replacement。
