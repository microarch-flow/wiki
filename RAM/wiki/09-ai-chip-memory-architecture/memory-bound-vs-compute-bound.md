# Memory bound vs compute bound 的本质与缓解策略

上级：[AI 芯片内存架构](./README.md)
相关：[NPU 的 on-chip 带宽预算从哪来、到哪去](./on-chip-bandwidth-budget.md), [峰值带宽 vs 有效带宽：损失发生在哪里](../07-system-architecture/effective-bandwidth-vs-peak.md)

## 这页在回答什么问题

为什么“算力不满”很多时候不是 compute 问题，而是 memory 问题；怎么判断瓶颈在哪一层，以及缓解策略应该落在哪一层。

## 正文

`memory-bound` 和 `compute-bound` 是 AI 芯片分析里最常见、也最容易被说得过于粗糙的一对词。很多讨论会把它们讲成一个二选一标签，好像一个 workload 不是算力瓶颈，就是带宽瓶颈。真正的系统里，这种说法通常不够。因为所谓 `memory-bound`，往往不是单一的“内存慢”，而是多层数据路径中的某一段先堵了。你如果不把堵点分层拆开，后面的缓解策略大概率会打错地方。

先看 `compute-bound` 的严格含义。它不是“系统很快”，也不是“带宽完全不重要”，而是说在当前映射、当前数据放置、当前工作集条件下，决定吞吐上限的主要因素是可用计算资源本身。更直白一点：如果你进一步增加外存带宽、扩大片上 SRAM、优化数据搬运，性能也不会明显上升，因为阵列已经大部分时间在饱和计算。只有在这种前提下，把问题叫作 compute-bound 才成立。

对应地，`memory-bound` 的严格含义也不是“用了很多内存”，而是说计算资源的可用吞吐没有被真正兑现，上限被某一段数据供应或结果回收路径限制住了。关键是，哪一段路径。对 NPU 来说，至少要分四类。第一类是 `off-chip bandwidth bound`，也就是外存持续供数能力不够，权重、激活或 KV 工作集反复从 HBM/LPDDR 拉取仍然把阵列饿住。第二类是 `on-chip distribution bound`，也就是外存也许够、总片上 SRAM 也许够，但 NoC、共享 SRAM 扇出或局部链路无法把数据送到正确的 cluster。第三类是 `local SRAM/bank bound`，也就是某一级 buffer 的 bank、端口或并发读写组织撑不住。第四类是 `feedback path bound`，最典型就是 psum 的本地读改写回路太短板，结果阵列不是缺输入，而是缺更新输出的路径。

这四类问题在表面症状上可能很像，都是“TOPS 没跑满”或“阵列利用率不高”，但本质完全不同。假设你看到阵列利用率只有 60%。如果原因是外存长期供不上，那换更大的片上 buffer 也许帮助有限；如果原因是某一级 activation buffer 的 double buffering 没建立起来，那换 HBM 也许根本不解决；如果原因是 psum bank 冲突，那你继续加算力只会把冲突放大。也就是说，`memory-bound` 这个词本身几乎不提供行动信息，真正有用的是：到底是哪一层 memory path 在 bound。

这也是为什么很多简单 roofline 图只能当起点，不能当结论。roofline 会告诉你算术强度和某个带宽上限之间的大致关系，这很有用，但它常常把 memory system 折成一条边。对通用判断足够，对 NPU 细节不够。因为 NPU 的 memory path 往往不是一条边，而是 `off-chip -> L2 -> NoC -> L1 -> L0 -> array -> psum path` 这样一串边。任何一段都可能先撞墙，而它们的缓解策略差得很远。

从诊断角度看，判断是否 compute-bound，最可靠的方法不是看“带宽利用率高不高”，而是看 `额外供数资源` 是否还能换来明显吞吐。如果你提高外存带宽、增加片上 buffer 命中工作集、改善 overlap、减少 bank 冲突之后，吞吐几乎不动，那才说明 compute 已接近主瓶颈。反过来，只要这些 memory-path 优化还能稳定换来性能，系统就还没有进入真正的 compute-bound 区域。

同样地，判断 memory-bound 的时候，也要追问“在哪个时间尺度、哪条链路上 bound”。有些 workload 是长期平均外存带宽就不够，这属于持续型 `off-chip bound`；有些 workload 平均带宽够，但每个 tile 切换时 refill 没能藏起来，属于相位型 `staging bound`；有些 workload 平均上看所有链路都还行，但局部 bank hotspot 或 multicast 扇出把某些 cluster 周期性饿住，属于空间型 `local distribution bound`。把这些都叫 memory-bound 没错，但如果不区分，你就会把应该改 tiling 的问题误判成应该换 HBM，把应该改 banking 的问题误判成应该加 cache。

这也说明为什么缓解策略必须按层落。对 `off-chip bandwidth bound`，更大的片上复用、更少的外层往返、更强的外存路线、压缩或更合适的 batch shape 都可能有效。对 `on-chip distribution bound`，关键在片上流图，可能要改 NoC、改 multicast、改 cluster 切分、改共享 SRAM 作用域。对 `local SRAM/bank bound`，更多是 bank geometry、端口组织、buffer role 分离、tile 读写并发关系。对 `feedback path bound`，常常要改 output-stationary 策略、本地 accumulator 组织或 psum 生命周期。也就是说，memory-bound 不是一句“加带宽”能打发掉的。

再进一步，`compute-bound` 自身也可能是“伪 compute-bound”。比如某个 workload 因为过于保守的 tiling，片上数据都放得很舒服，于是暂时不缺带宽，但阵列规模又没被充分展开，看上去像算力主瓶颈。可一旦你把并行度开大，它立刻变成片上带宽瓶颈。换句话说，compute-bound 往往是相对于当前映射和当前资源配置成立的，而不是 workload 的永久属性。真正有价值的判断，不是贴一个静态标签，而是理解系统在设计空间里向哪个方向再推一步，会先撞哪堵墙。

从 `Capability` 的角度看，一个 NPU 的吞吐上限，本质上是 `compute envelope` 和 `memory-delivery envelope` 的较小者；而后者又不是一个单一 envelope，而是多层路径中最窄一截的合成结果。这就是为什么同样的外存带宽，两个架构可以表现差很多；同样的 TOPS，两个芯片也可以表现差很多。差别不只在算子支持，而在数据路径各层是否同时够宽、够近、够重叠。

因此，本页真正想建立的判断框架是：

1. 先确认算力阵列有没有真的忙起来。
2. 如果没忙起来，不要立刻说“memory-bound”，而是继续定位是哪一层 memory path 把它卡住。
3. 再把缓解策略准确落在对应层，而不是一律加外存带宽或一律缩模型。

只有这样，`memory-bound vs compute-bound` 才不是一句概念标签，而是一套能指导架构修改、编译映射和系统选型的诊断方法。

## 一句话理解

对 NPU 来说，`memory-bound` 不是单一状态，而是一族不同层级的数据路径堵塞；只有先找出是外存、片上分发、局部 SRAM 还是 psum 回路在限速，缓解策略才不会打错地方。

## 建模启示

在模型里，不要只输出一个 `bound = memory | compute`。更有用的做法，是把瓶颈类型做成分层标签和计数器。

一个够用的抽象可以写成：

```text
BottleneckBreakdown {
  compute_busy_cycles: int
  offchip_wait_cycles: int
  onchip_network_wait_cycles: int
  local_buffer_wait_cycles: int
  psum_feedback_wait_cycles: int
}
```

然后给每个 stall 打原因码：

```text
StallReason = enum {
  offchip_refill_not_ready,
  l2_to_l1_congestion,
  bank_conflict,
  activation_tile_not_ready,
  weight_tile_not_ready,
  psum_path_busy,
  compute_dependency
}
```

这样仿真结束后，就不只是知道“利用率 63%”，而是知道 37% 的空洞里到底是谁造成的。

如果还想做更进一步的诊断，可以看一个简单的灵敏度实验：

- 外存带宽增加 x%
- 片上 NoC 带宽增加 x%
- 局部 bank 数增加 x%
- MAC 数增加 x%

看哪一项最能抬吞吐，系统当前就更接近被哪一层绑定。这个方法虽然粗，但比直接贴一个 `memory-bound` 标签有用得多。
