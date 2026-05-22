# Weight buffer 的容量与组织：从 model size 反推

上级：[AI 芯片内存架构](./README.md)
相关：[NPU 的存储层次：L0、L1、L2 SRAM 与 HBM、LPDDR](./npu-memory-hierarchy.md), [NPU 的 on-chip 带宽预算从哪来、到哪去](./on-chip-bandwidth-budget.md)

## 这页在回答什么问题

weight buffer 不应该拍脑袋定容量；应该怎样从模型分块、复用距离和数据搬运代价反推它的容量、banking 和端口组织。

## 正文

weight buffer 是 AI 芯片里最容易被说得过于简单的一类本地存储。很多介绍会把它描述成“存权重的 SRAM”，这当然没错，但没有分析价值。真正重要的问题不是它存什么，而是它为什么要以这种容量、这种 banking、这种作用域存在。因为对大多数 NPU 而言，weight buffer 的价值不在抽象名词上，而在于它能否把一次从外层搬进来的权重，多服务几轮计算，少让外存反复参与。

所以，设计 weight buffer 时，第一个问题从来不该是“芯片上还有多少 SRAM 可分”，而应该是：`当前 workload 中，权重的有效复用距离有多长`。如果一组权重只会在很短的窗口里被消费一次，那么把它常驻很久没有意义；如果一组权重会在同一 tile、同一 batch、同一 head 或同一输出通道块上反复使用，那么多留它一会儿，往往比再扩一点算力阵列更值钱。换句话说，weight buffer 的本质不是一块“权重仓库”，而是一个把外存读取次数换成本地驻留时间的装置。

这就要求你从 `model blocking` 反推 buffer 需求，而不是从 SRAM 预算正推。以 GEMM 或 attention 中常见的 tile 计算为例，一块权重到底要在本地留多久，取决于你如何切 `M/N/K` 或 token/head/channel 这些维度。如果 mapping 让同一块权重被多个 activation tile 连续消费，那么 weight-stationary 就更有吸引力；如果 mapping 让权重块切换频繁，甚至每轮都要换，那么 weight buffer 只能承担较短期的 staging 角色。也就是说，weight buffer 容量不是独立参数，它和 tile 形状、数据流映射、阵列利用方式绑在一起。

因此，一个更合理的设计顺序通常是这样的。先确定算子如何分块，估计某块权重在片上能服务多少次 MAC 或多少轮 tile；再看如果不保留这块权重，需要多频繁地从 L2、HBM 或 LPDDR 重取；最后比较“多给一点本地容量”与“让外存多跑几轮”的代价。只有这样，weight buffer 才是在为一个清楚的复用目标付账，而不是在为模糊的“多放点权重总没错”买单。

从这个角度看，weight buffer 容量通常受三类因素共同决定。第一类是 `working set per tile`。也就是当前映射下，一轮稳定计算至少需要哪一批权重常驻。这个下界太小，阵列就会在 tile 内部也频繁等待换权重。第二类是 `reuse horizon`。如果你希望同一组权重跨多个 activation tile、多个时间步或多个 query block 复用，那么需要为更长驻留窗口付出更多容量。第三类是 `refill tolerance`。假设外层带宽足够强、且 refill 能完全和计算重叠，那么本地容量压力可以适当放松；反过来，如果外层带宽紧、回填抖动大，weight buffer 就需要更像一个“缓冲水库”，用更多容量吸收远端供数不稳定。

这里的关键 trade-off 可以写得非常直白：`更大的 weight buffer` 买到的是更长的权重驻留和更少的外存回取；`更小的 weight buffer` 则意味着要么缩小 tile，要么提高外层 refill 频率，要么接受阵列周期性断粮。哪种更优，不取决于哪种听起来更先进，而取决于外存路线、片上网络、模型层形状和目标功耗预算。

不过，容量只是第一层。weight buffer 真正经常让设计翻车的地方，是 `organization`。因为权重不是只要“在里面”就够了，它还必须在正确节拍、以足够并行度送到下游。如果一个阵列每个周期需要从多个 bank 取不同的权重片段，而你的 buffer 只有理论上够大的单体 SRAM，却没有足够的 bank 并发或读端口，那么容量再大也喂不饱阵列。也就是说，weight buffer 的可用性由两部分共同决定：`能存多久` 和 `每拍能吐多少`。

这就把容量问题自然推到 `banking` 上。一个常见误解是，把 weight buffer 设计理解成“容量定完后再切 bank”。其实在很多 NPU 里，banking 先于总容量成为一等公民，因为它决定了权重能否按阵列所需形状被同时读取。阵列如果是按列广播权重，bank 组织可能要优先匹配列分发；如果不同 PE cluster 需要并行读取不同通道块，bank 组织又要优先匹配 cluster 粒度。你最终不是在设计一块抽象 SRAM，而是在设计一个与下游消费拓扑对齐的“读出几何形状”。

除此之外，还要看权重在层次中的 `scope`。有的 weight buffer 更接近 L0/L1，只服务一个阵列或一个 cluster；有的更接近 L2，会在多个 cluster 之间共享。局部 buffer 的优点是距离短、读带宽便宜、冲突面小；缺点是容易碎片化，同一组权重若要被多个 cluster 用，复制成本上升。共享 buffer 的优点是容量利用率高、复用更灵活；缺点是仲裁更多、扇出更重、读热点更容易集中。也就是说，weight buffer 不只是一个容量问题，也是一个“权重应该在哪里停留最划算”的拓扑问题。

很多时候，你甚至不该把“weight buffer 大小”当成单一数字，而应该拆成两个问题：`最近一级是否够稳地喂阵列`，以及`上一层是否够久地留住当前层即将反复消费的权重`。前者更偏端口和 bank 带宽，后者更偏容量和驻留策略。把这两件事混成一块大 SRAM，常常会让某一个目标被另一个目标拖累。

在训练和推理之间，这个问题的形状也不同。推理里的权重通常长时间稳定，写入极少，因此更容易为 weight-stationary 路线辩护；训练里虽然前向和反向阶段也会强烈重用权重，但参数更新、梯度流和不同阶段的访问模式会让“纯只读仓库”这个假设变弱。也就是说，不能把某个推理芯片的 weight buffer 设计直接移植到训练加速器上，只因为它们都叫 AI 芯片。

把这些因素串起来，就能得到一个比较稳的结论：weight buffer 设计不是“看模型有多大，就给一个尽量大的权重 SRAM”，而是从算子 blocking、复用距离、外层回填代价、阵列消费几何和共享范围一起反推。真正合理的容量，应该是“能把最值钱的权重复用留在片上，但不为复用很弱的部分白白付本地面积和静态功耗”。真正合理的组织，应该是“能按阵列节拍把权重吐出来，而不是只在容量表上显得足够”。

这也说明了一个很常见的误区。有人会问：“模型都这么大了，片上几 MB 或几十 MB weight buffer 有什么用？”这个问题隐含的前提是，只有把整模型装进去才算有价值。实际上，weight buffer 的价值从来不是“装下全模型”，而是“装下当前最值得不回外存的那部分权重工作集”。只要这部分工作集能在合适的时间窗口内被高频复用，本地驻留就有巨大价值。反过来，如果某部分权重本来就只用一次，那你把它死撑在片上反而是在浪费面积。

因此，本页真正要建立的心智是：weight buffer 不是一个静态“容量配置项”，而是 AI 芯片数据流设计里的驻留策略载体。它用本地 SRAM 面积、banking 和作用域，去换外存流量、片上带宽压力和阵列稳定供数能力。后面到了 `activation-buffer-and-double-buffering.md` 和 `on-chip-bandwidth-budget.md`，这条因果链会进一步闭合。

## 一句话理解

weight buffer 的大小和组织应该从权重块的复用距离、外层回填代价和阵列每拍消费形状反推，而不是从“模型很大所以尽量多放点权重”正推。

## 建模启示

在模型里，weight buffer 至少要区分三件事：`能留多少权重`、`每拍能读出多少权重`、`这些权重服务的是哪个作用域`。只建一个 `weight_buffer_bytes` 会把最关键的瓶颈抹掉。

一个够用的抽象可以写成：

```text
WeightBuffer {
  scope: enum { pe_local, cluster_local, chip_shared }
  capacity_bytes: int
  bank_count: int
  read_bw_Bps: float
  refill_bw_Bps: float
  refill_latency_ns: float
  supported_weight_tiles: int
}
```

再把 workload 侧的需求显式写出来：

```text
WeightTileDemand {
  tile_id: int
  bytes: int
  reuse_count: int
  reuse_window_cycles: int
  consumer_clusters: int
  bytes_per_cycle_needed: float
}
```

仿真时至少保留三类事件：

- `WeightFillStart/Done(tile_id)`
- `WeightConsume(tile_id, bytes)`
- `WeightEvict(tile_id)`

如果要进一步判断某个设计是“容量不够”还是“bank/带宽不够”，可以再跟踪：

- 当前驻留 tile 数
- 每周期 bank 冲突次数
- 因 refill 未完成导致的 compute stall 周期

这几项状态一旦保留，很多原本模糊的讨论都会变得可诊断：到底是 weight buffer 太小，还是 refill 太慢，还是阵列每拍读口组织不对。
