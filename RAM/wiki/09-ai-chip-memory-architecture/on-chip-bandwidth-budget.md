# NPU 的 on-chip 带宽预算从哪来、到哪去

上级：[AI 芯片内存架构](./README.md)
相关：[Activation buffer 与 double buffering：数据搬运与计算如何重叠](./activation-buffer-and-double-buffering.md), [多 master 场景下的 QoS 与公平性](../06-memory-controller/qos-multi-master-arbitration.md)

## 这页在回答什么问题

当算力扩张后，片上 SRAM、NoC、DMA 和 PE 阵列之间的带宽预算应该怎样拆；瓶颈为什么常常不在外存，而在片上数据搬运链路。

## 正文

很多 AI 芯片在宣传材料里会强调外存带宽，比如 HBM 有多少 TB/s，或者 LPDDR 有多少 GB/s。这些数字当然重要，但如果只盯着它们，你很容易错过一个更常见的现实：阵列喂不饱，往往不是因为外存峰值不够，而是因为 `on-chip bandwidth budget` 根本没算清。也就是说，数据也许已经被顺利搬进芯片，可它未必能继续顺利穿过 L2、片上网络、L1、局部 buffer、accumulator 回路，最后准时到达每个 PE。就像一座城市——从外地运来的货物已经到了城市高速入口，但如果市内道路拥堵、配送网络分发不开，货还是到不了每家每户的门口。外存带宽相当于高速公路，片上带宽则是城市内部的街道和配送网络。

这就是片上带宽预算的核心意义。它不是抽象地问“芯片内部快不快”，而是追问：`为了让当前算力规模稳定工作，每个周期到底要有多少字节在芯片内部哪些边界上流动`。只要这张税单没有算清，再大的总 SRAM、再高的外存带宽、再漂亮的 TOPS 数字，都可能因为内部某一段链路过窄而变成表面能力。

要理解这件事，先得把“带宽需求”看成是从算力阵列反推出来的，而不是从 SRAM 或 NoC 规格正推出来的。一个阵列如果每拍要做一定数量的 MAC，那么它每拍至少要消耗对应数量的 activation 和 weight，并产生对应数量的 partial sum 读改写或输出写回。哪怕这些数据都已经在片上，也并不等于它们能自动同时出现在正确位置。每一类数据都需要通过某些 bank、某些 crossbar、某些局部总线、某些 multicast 路径。于是，阵列的每拍算力会立刻翻译成一组片上流量需求。

这张需求表至少包含四类流量。第一类是 `weight read traffic`，从某级 weight buffer 或共享 SRAM 向阵列或 cluster 广播。第二类是 `activation read traffic`，从 activation buffer 按 tile 节拍送入下游。第三类是 `psum read/write traffic`，这类流量经常最容易被低估，因为 partial sum 不是简单输出，而是高频局部反馈回路。第四类是 `refill / drain traffic`，也就是来自上一级 SRAM 或外存 DMA 的补货流，以及结果写回流。真正的片上带宽预算，必须把这四条账同时列出来。

很多设计讨论只会关心前两项，因为它们看起来直接服务 MAC 阵列。但在真实系统里，后两项经常才是把吞吐拖垮的隐性税。原因很简单：当你只看 weight 和 activation 供数时，好像下游每拍只在“吃”数据；一旦把 psum 和 refill 也算进来，你会发现许多边界其实在同一时间既要服务读、又要服务写、还要服务跨层搬运。于是问题不再是“这条链路峰值有多高”，而是“同一时间有多少种流量在抢它”。

这也是为什么 `总 SRAM 很大` 几乎从不等于 `片上带宽够`。容量只回答“能不能装”，带宽才回答“能不能同时拿出来”。一个几十 MB 的片上 SRAM，如果 bank 数量太少、读口组织不对、和多个 cluster 的连接扇出太重、或者内部仲裁太保守，最后都可能表现成“阵列在等数据”。换句话说，片上带宽的真正单位不是 MB，而是 `bytes per cycle delivered at the right boundary`。打个比方：一个仓库有 10 万件库存，但出货口只有两个窗户——你不能说"仓库很大所以发货很快"。SRAM 容量是仓库面积，bank 和端口才是出货口数量。

从实现角度看，片上带宽预算至少会被四类因素切碎。第一类是 `bank geometry`。同样的总容量，如果 bank 切得更细、更贴近消费者，理论上能提供更高并发；但 bank 太细也会增加控制和碎片化成本。第二类是 `fanout topology`。权重如果需要从共享 buffer 广播到许多 PE cluster，那么读出带宽和分发带宽不是一回事，后者常常更难。第三类是 `read/write asymmetry`。activation 多读少写，psum 高频读改写，结果写回可能成批爆发，不同流量的最优路径不同。第四类是 `multi-role contention`。同一块 SRAM 或同一条 NoC 链路如果同时服务 weight、activation、psum 和 DMA，中高负载时冲突会迅速显性化。

把这些因素连起来看，你会发现片上带宽预算更像一张 `flow graph`，而不是一个全局数值。L2 到 L1 的路径有自己的带宽和并发数；L1 到阵列的路径有自己的 bank 冲突边界；psum 回写有自己的本地反馈路径；DMA refill 可能和别的流量共享芯片网络入口。任何一条边只要低于当前 tile 的持续需求，就会把整个系统拖进局部饥饿。重要的是，这种饥饿往往不是持续 0% 或 100% 的，而是周期性、阶段性出现，所以如果你只看总平均带宽利用率，常常会错判。

这也解释了为什么很多芯片在扩算力后，性能增长远低于理论线性值。算力翻倍时，片上带宽需求并不会只在一个点上翻倍，而是整张流图多处同时变粗。更糟的是，不同流量的相位关系也会变化。比如 weight refill 也许还能被更多复用抵消一部分，但 activation staging 和 psum 回路可能会近乎同步地变重。结果就是，某一段局部 crossbar 或某一层共享 SRAM 的 bank 带宽先撞墙，整个阵列的利用率就被它卡住。用户看到的是”TOPS 没跑满”，真正发生的是”片上某条小路先堵死了”。就像一条八车道高速公路连接到一个两车道的收费站出口——高速公路再宽，车流量还是被收费站的通过能力决定。

因此，片上带宽预算不能只从静态峰值出发，还要看 `时间重叠`。上一页讲过 activation double buffering 是否真的成立，这里同样成立。假设 L2 到 L1 的 refill 能和当前 tile 计算重叠，那么你会把一部分流量藏在时间后面；如果重叠失败，那条路径就会直接显露成 stall。也就是说，片上带宽需求并不只是“每层要多少 GB/s”，还包括“这些 GB/s 是否需要在同一时间发生”。同样一组总字节量，如果时序上分散得好，系统可行；如果集中爆发，局部瓶颈会立刻跳出来。

再进一步看，片上带宽预算还会被 `dataflow choice` 改写。weight-stationary、output-stationary、activation-stationary 这些路线之所以重要，不只是因为它们改变外存访问模式，更因为它们重新分配了片上谁最忙。weight-stationary 往往减轻权重搬运，却可能加重 activation 流和 psum 路径；output-stationary 往往缩短 psum 回路，却可能让输入分发更重。也就是说，dataflow 不是“计算侧策略”，它直接决定了片上带宽税单由谁来付。

从 `Capability` 角度讲，一个 NPU 真正能持续提供的吞吐上限，取决于最紧的那条内部供数路径，而不是宣传页上最大的那个峰值数字。外存带宽是必要条件，但绝不是充分条件。你必须同时看：SRAM banking 是否足够、跨 cluster 分发是否够宽、psum 回路是否够短、DMA refill 是否能与计算重叠、多个 data role 是否在同一边界上争用。少看任何一项，都会把“为什么喂不饱”讲成过于粗糙的“带宽不够”。

因此，本页真正要建立的是这样一种判断方式：对 AI 芯片来说，带宽预算首先是一张内部流量账单，而不是一个总峰值参数。你要从阵列每拍需求反推出每层、每条链路、每类数据角色的持续供数责任，再检查这些责任是否会在时间上、空间上和仲裁上撞车。只有这样，后面讨论 `HBM vs LPDDR` 或 `memory-bound vs compute-bound` 时，才不会把所有问题错误地推给外存。

## 一句话理解

AI 芯片的真实性能上限常常先被片上带宽税单卡住：不是总 SRAM 不够大，而是 weight、activation、psum 和 refill 这些流量无法在正确时间同时穿过正确的 bank 和链路。

## 建模启示

在模型里，片上带宽不能只写一个 `onchip_bw_GBps`。更有效的做法，是把每类数据流拆开，并且按边界记录容量与时间重叠关系。

一个够用的抽象可以写成：

```text
OnChipFlowEdge {
  src: str
  dst: str
  bandwidth_Bps: float
  arbitration_group: str
  supports_multicast: bool
}
```

每个 tile 再带出自己的流量需求：

```text
TileTrafficDemand {
  tile_id: int
  weight_read_bytes: int
  activation_read_bytes: int
  psum_read_bytes: int
  psum_write_bytes: int
  refill_bytes: int
  drain_bytes: int
  active_cycles: int
}
```

仿真时至少跟踪三类状态：

- 每条 edge 在当前周期承载了哪些流量
- 哪些流量属于同一个 arbitration group
- 哪些 refill/drain 能和 compute overlap

如果要定位瓶颈，再补几项计数器就够有用了：

- `bank_conflict_cycles`
- `noc_backpressure_cycles`
- `psum_path_stall_cycles`
- `refill_overlap_miss_cycles`

这样模型就能回答真正关键的问题：阵列没跑满，到底是外存慢、片上网络窄、局部 SRAM bank 组织不对，还是 partial sum 回路先把自己堵死了。
