# NPU 里的 SRAM buffer：weight、activation、accumulator

上级：[SRAM 应用形态](./README.md)
相关：[bank、sub-array、mat：SRAM 阵列怎么划分才高效](../02-sram-foundations/sram-array-organization.md), [NPU 的存储层次：L0/L1/L2 SRAM 与 HBM/LPDDR](../09-ai-chip-memory-architecture/npu-memory-hierarchy.md)

## 这页在回答什么问题

NPU 里的片上 SRAM 为什么不会被笼统地叫“cache”，而是按 weight、activation、accumulator 分成不同 buffer；这些角色为什么对应不同的数据复用和端口需求。

## NPU 本地 buffer 的数据角色

NPU 的片上 SRAM 如果只被叫作”一块本地缓存”，就像把厨房里的冰箱、灶台和砧板统称为”厨房设备”——技术上没错，但在讨论工作流时毫无用处。在大多数 NPU 数据流里，权重、激活和部分和并不是同一种”数据对象”，它们的生命周期、搬运方向、复用距离和并发压力都不同。这些角色对容量和访问路径提出不同要求；具体物理组织可共享，也可分别配置。

先看 weight buffer。权重最典型的特点是 `读多写极少`——就像菜谱：你从书架上拿下来（从 HBM 装入），然后反复翻看（重复读取），直到这道菜做完才放回去。在推理场景里，一块权重通常从 HBM、LPDDR 或上一级 SRAM 装入片上后，会被重复读取很多次，直到当前 layer、tile 或 channel block 处理完成。它的设计价值不在”能不能随机写”，而在”能不能让一次装载服务尽可能长的复用距离”。这意味着 weight buffer 常常优先追求三件事：较高净容量效率、较高读带宽、以及按 PE 阵列分发时的并行供数能力。常见误解是把 weight buffer 简化成“只读 SRAM”；更准确的说法是，它是一个为读主导复用而优化的 staged storage。

activation buffer 的约束则不同。激活数据往往既要被写入，也要被较快地消费。它一方面承接外层输入流或上游 layer 输出，另一方面要按当前 tile 的计算节奏被多个计算单元重复读取。在卷积、attention 或 GEMM 映射里，activation 的复用可以很强，但这种复用通常更短、更依赖 tiling 和窗口滑动方式，也更容易被双缓冲节拍左右。所以 activation buffer 的关键设计变量，往往不是“尽量大”，而是“能否在当前 tile 被消费时，同时把下一块 tile 搬进来”。这也是为什么 activation buffer 天然和 DMA overlap、double buffering、bank interleave 绑得很紧。

accumulator buffer 或 partial-sum buffer 又是第三类完全不同的对象。如果说 weight buffer 像菜谱、activation buffer 像食材传送带，那 accumulator buffer 更像炒锅——食材进去之后不是放着不动，而是不断被翻炒、加料、再翻炒。它承担的是 `高频读改写`。一次 MAC 之后，部分和要么继续留在本地等待下一次累加，要么在若干轮累加后再写回外层。于是 accumulator buffer 最敏感的不是”能放多少”，而是”局部读改写回路有多短、每拍能承受多少并发更新”。如果它的端口、bank 组织或本地带宽设计不够，算力阵列会先在 psum 更新路径上堵住。常见误解是把 accumulator 也视为普通输入 buffer；实际上，它更像一个为局部反馈回路定制的工作区。

把这三类 buffer 放在一起比较，会发现它们至少在四个维度上天然不同。第一，生命周期不同。权重可能跨多个 tile 常驻，activation 常随 tile 滚动，psum 往往在较短窗口内不断更新后被导出。第二，读写方向不同。权重偏只读，activation 常常是“边装边读”，psum 则偏“边读边写回”。第三，复用模式不同。权重更像广播到多个 consumer，activation 更像流经局部窗口，psum 更像围绕单个输出元素反复回流。第四，性能风险不同。权重 buffer 配小了，外层带宽压力会上升；activation buffer 组织不好，流水 overlap 会失效；accumulator buffer 扛不住，则会直接在最内层把阵列停住。

这些差异会直接反映到 SRAM 组织方式上。weight buffer 更适合围绕读带宽和容量效率组织，可以容忍较弱的写路径，但需要良好的银行化分发能力。activation buffer 更强调搬运与消费并行，因此更需要和 bank 切分、prefetch 粒度、双缓冲边界一起设计。accumulator buffer 更关注本地反馈路径和更新热点，往往要求更高的局部写带宽、更短的数据返回路径，甚至更贴近 PE 的分布式布局。若三者共享 local SRAM，模型仍要保留各自访问轨迹并在共享端口仲裁；若独立，则各自建模。

这也是为什么 NPU 里的这些 buffer 更像 scratchpad，而不像 cache。它们的价值不来自硬件去猜哪些数据可能会复用，而来自设计者提前知道哪些数据一定会复用、复用多久、该以什么顺序搬。对 weight，设计者通常知道这一块权重会服务哪一批输出通道；对 activation，通常知道当前 tile 的消费顺序；对 psum，通常知道哪一组输出元素会在本地累计多少轮。既然局部性是可设计的，而不是可碰运气的，把这些 buffer 交给 cache 式自动替换通常不是最优解。

还有一个很重要的后果是：NPU 的片上 SRAM 容量不能只看总量，还须记录每个角色的同时占用和对物理资源的绑定。16 MB 若是共享池，应计算 weight/activation 等角色的合计占用峰值，并对共享 bank、端口和带宽仲裁；若是专用宏，则分别检查各宏容量与端口。psum 若驻留 PE 寄存器，不应强加一个 SRAM 容量分区。因为很多设计瓶颈根本不在总容量，而在某一类 buffer 的读写不对称、bank 冲突或 refill 节拍没有对齐。后面到了 `weight-buffer-design.md`、`activation-buffer-and-double-buffering.md` 和 `on-chip-bandwidth-budget.md`，这种按角色而不是按总量思考的必要性会进一步变得明确。

按角色管理可约束共享池中的容量与端口竞争。例如权重 refill 和 activation 读取争同一 bank 时，仲裁与预留决定两者何时前进。独立宏可提供隔离，但可能浪费闲置容量；共享池可提升容量利用率，却需要考虑冲突和调度。两种实现均需根据实际访问轨迹评估。

因此，weight、activation 和 partial sum 是不同的逻辑角色。它们可绑定到独立 SRAM，也可共享同一物理 SRAM 的容量、bank 和端口；partial sum 也可驻留在 PE 寄存器而非独立 buffer。实际绑定决定容量约束和仲裁，不能由角色数推断物理宏数。理解这一点，后面讨论 NPU 内存层次和带宽预算时，你就不会把片上 SRAM 误看成“只要够大就行”的单一资源。

## 一句话理解

weight、activation 和 partial sum 的生命周期、读写方向和带宽需求不同，必须按角色追踪；它们可绑定到专用或共享物理资源，psum 也可驻留 PE。容量和端口约束按实际绑定及同时占用计算。

## 建模启示

在架构模型里，NPU 片上 SRAM 不能只建成一个统一的 `onchip_buffer_bytes`。至少应区分数据角色，并显式绑定到实际物理资源，因为它们的瓶颈和调度语义不同。weight buffer 更像 `read-mostly staged storage`，activation buffer 更像 `streamed tile buffer`，accumulator buffer 更像 `high-frequency read-modify-write workspace`。

一个最小可用的抽象草图可以是：

```text
NpuBufferModel {
  role: enum { WEIGHT, ACTIVATION, ACCUMULATOR }
  physical_resource_id: id  # 不同角色可绑定同一资源
  capacity_bytes: uint64  # 共享时由物理资源统一约束占用峰值
  psum_location: enum { PE_REGISTER, SRAM, OTHER }
  bank_count: int
  read_bw_bytes_per_cycle: int
  write_bw_bytes_per_cycle: int
  refill_source: enum { DRAM, HBM, UPPER_SRAM }
  supports_double_buffer: bool
}
```

对应事件流可以写成：

```text
event BufferFillStart(role, tile_id)
event BufferFillDone(role, tile_id)
event BufferRead(role, bank_id, consumer_id)
event BufferWrite(role, bank_id, producer_id)
event BufferDrain(role, tile_id)
```

如果只做粗粒度 roofline 估算，可以把三者折成总片上容量和总片上带宽；但只要你想解释“为什么同样 16 MB 片上 SRAM，两个 NPU 的吞吐差这么多”，必须保留三类角色的访问轨迹及其物理绑定。共享宏时共同检查容量峰值、bank 和端口仲裁；独立宏则分别检查。
