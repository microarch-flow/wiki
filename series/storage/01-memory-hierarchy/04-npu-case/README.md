# AI 芯片内存架构

上级：[存储层级与数据路径](../README.md)
相关：[系统视角](../01-system-basics/README.md), [封装与集成](../../06-system-integration/packaging/README.md)

## 这页在回答什么问题

这一章把前面所有存储器知识落到 AI 芯片与 NPU 场景，讨论数据搬运、带宽预算、片上 SRAM 组织和外存选型。

## 数据供应如何约束计算阵列

到这一章为止，前面的铺垫应该已经足够清楚：SRAM 和 DRAM 不是谁更先进，而是两类完全不同的资源契约；memory controller 决定外存能被兑现成什么样的行为；封装与集成决定带宽密度、距离和成本边界。AI 芯片要做的，不是重新发明这些规律，而是把它们推到一个更极端的位置上。因为在很多 NPU、训练加速器和推理芯片里，真正先撞墙的往往不是乘加阵列本身，而是数据怎么搬、搬多远、搬几次、在哪一级被卡住。就像一个大型工厂——生产线上的机器并不缺，真正让产能上不去的，往往是原材料从仓库到工位的传送带不够快、中转站太少、或者不同车间之间的物流通道太窄。

所以这一章的出发点，不应该是“某个 AI 芯片用了几级 cache”或者“用了 HBM 还是 LPDDR”，而应该是更朴素的问题：`一次计算所需的数据，沿着什么路径流动`。只有把这条路径画清楚，你才能理解为什么 AI 芯片往往会出现多级片上 SRAM、显式 double buffering、weight/activation/accumulator 分角色管理、极宽片上互连，以及外存路线必须和数据流一起设计。

从这个角度看，AI 芯片内存架构需要协调计算与数据供应。算力阵列需要足够的数据，否则 MAC 可能空转；外部 DRAM（例如 HBM 或 LPDDR）可能提供较高的聚合带宽，但其访问粒度、共享和延迟也会影响供数；片上 SRAM 的容量、面积和 bank 冲突受到约束。系统可以按复用和时序要求组织数据放置，减少不必要的跨层搬运；同时也要检查计算、依赖和其他资源是否成为瓶颈。

这也是为什么 NPU 的存储层次通常看起来不像 CPU。CPU 更依赖对通用程序访问模式的平均优化，所以 cache hierarchy 很重要；而 AI 芯片面对的是更规则、更可预测、但数据量极大的张量流。打个比方：CPU 的 cache 更像超市——提前猜你可能想买什么并摆到货架上，猜对了就快，猜错了就得去仓库取；NPU 的 scratchpad 更像工业流水线旁的物料暂存区——每个工位要什么零件、什么时候要、从哪里运来，全部按生产计划提前编排好，根本不需要"猜"。这里真正昂贵的不是偶发 miss，而是持续的数据供应失配。所以很多 NPU 不把片上 SRAM 包装成“尽量透明的 cache”，而是更接近结构化 scratchpad 或 role-specific buffer：某一级负责喂 tile，某一级负责存 weight，某一级负责中间 partial sum，另一层负责跨 cluster 或跨 PE 共享。也就是说，AI 芯片的内存层次往往更像一套显式数据流管线，而不是一棵纯粹为 locality 猜测服务的缓存树。

这一章会沿着这条主线展开。先从 `npu-memory-hierarchy.md` 开始，把 NPU 常见的 `L0/L1/L2 SRAM + HBM/LPDDR` 层次讲清楚，建立各层的角色边界。然后进入 `weight-buffer-design.md` 和 `activation-buffer-and-double-buffering.md`，分别把权重驻留、输入 staging、双缓冲和流水重叠讲透。接着在 `on-chip-bandwidth-budget.md` 里把片上带宽预算从口号落成真正的数字关系，说明为什么“总 SRAM 很大”并不自动代表“阵列喂得饱”。

再往后，`hbm-vs-lpddr-for-npu.md` 会把外存路线选择收成一个系统决策框架，而不是只比理论带宽；`data-movement-first-principle.md` 会把这一整章的底层原则钉住，说明为什么很多 AI 芯片优化本质上都在减少无效搬运；最后 `memory-bound-vs-compute-bound.md` 会把常见的“算力瓶颈还是带宽瓶颈”问题真正讲清楚，避免把 roofline 那类判断简化成一句口号。

如果用更抽象的话说，前面章节更多是在建立 `memory resource` 本身的物理与系统性质；这一章开始，我们关心的是这些资源如何被组织成一张面向张量数据流的 `topology`，不同层之间发生哪些 `interaction`，最终系统能提供什么样的 `capability`。这里之所以允许显式使用这组抽象，是因为 AI 芯片里“存储器是什么”已经不能只靠单层器件定义，而要看它被放在数据通路的哪个位置、承担哪种供数义务、暴露给软件什么放置接口。

所以，读这一章时最重要的心智切换是：不要先把注意力放在“某级存储器名字叫什么”，而要先看它在整条数据路径里负责什么。如果某层负责消化 bursty 外存带宽，把它做成可双缓冲的 staging buffer 就合理；如果某层负责高频 partial sum 回写，把它做成高 RMW 带宽的 accumulator buffer 就合理；如果某层负责跨 tile 重用权重，把它做成 weight-stationary 友好的本地仓库就合理。名字只是表象，数据角色才是内核。

## 阅读顺序

建议按下面顺序阅读本节：

1. [NPU 存储层次](./npu-memory-hierarchy.md)
2. [Weight buffer 设计](./weight-buffer-design.md)
3. [激活缓冲与双缓冲](./activation-buffer-and-double-buffering.md)
4. [片上带宽预算](./on-chip-bandwidth-budget.md)
5. [数据搬运优先](./data-movement-first-principle.md)

需要诊断限制资源时，可读[存储瓶颈与计算瓶颈](../03-performance/memory-bound-vs-compute-bound.md)。需要比较外存路线时，可读[HBM 与 LPDDR 选型](../../06-system-integration/hbm-vs-lpddr-for-npu.md)；这两篇位于不同分组。

## 一句话理解

AI 芯片内存架构需要按数据流角色组织片上 SRAM、片外 DRAM 和层间带宽，并结合计算资源分析能否持续供数。HBM 是 DRAM 的一种。

## 建模启示

做 AI 芯片仿真时，最容易犯的错误是把 memory subsystem 压成一个 `global_bandwidth_limit`。这样会直接抹掉两类最重要的信息：`哪一级先堵`，以及`堵塞会不会沿流水线向前后传播`。

更稳的做法，是把每一级存储资源都建成带角色的节点：

```text
MemoryNode {
  name: str
  level: enum { l0, l1, l2, offchip }
  capacity_bytes: int
  read_bw_Bps: float
  write_bw_Bps: float
  bank_count: int
  access_scope: enum { pe_local, cluster_local, chip_global, external }
  data_roles: set { weight, activation, accumulator, metadata }
}
```

层与层之间再显式建链路：

```text
DataLink {
  src: MemoryNode
  dst: MemoryNode
  bandwidth_Bps: float
  startup_latency_ns: float
  burst_bytes: int
  concurrent_flows: int
}
```

最后，用 workload 的 tile 流来驱动这些节点和链路。真正会改写结论的，不是某一层名义上多快，而是：

- 哪个 data role 在哪一级驻留
- 哪几条链路需要同时供数
- 某一级 buffer 是否支持 double buffering
- 某些数据能否跨 tile 复用而不回到更远层

后面几篇会把这些抽象一层层具体化。
