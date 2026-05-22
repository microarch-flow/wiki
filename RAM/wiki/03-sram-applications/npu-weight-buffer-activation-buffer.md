# NPU 里的 SRAM buffer：weight、activation、accumulator

上级：[SRAM 应用形态](./README.md)
相关：[bank、sub-array、mat：SRAM 阵列怎么划分才高效](../02-sram-foundations/sram-array-organization.md), [NPU 的存储层次：L0/L1/L2 SRAM 与 HBM/LPDDR](../09-ai-chip-memory-architecture/npu-memory-hierarchy.md)

## 这页在回答什么问题

NPU 里的片上 SRAM 为什么不会被笼统地叫“cache”，而是按 weight、activation、accumulator 分成不同 buffer；这些角色为什么对应不同的数据复用和端口需求。

## 正文

NPU 的片上 SRAM 如果只被叫作“一块本地缓存”，通常说明设计视角还停留在过于粗的层次。因为在大多数 NPU 数据流里，权重、激活和部分和并不是同一种“数据对象”，它们的生命周期、搬运方向、复用距离和并发压力都不同。既然目标不同，底层 SRAM 的最优组织就不可能相同。把它们分成 `weight buffer`、`activation buffer` 和 `accumulator buffer`，不是命名癖好，而是在承认：片上存储要先服从数据流角色，再谈总容量。

先看 weight buffer。权重最典型的特点是 `读多写极少`。在推理场景里，一块权重通常从 HBM、LPDDR 或上一级 SRAM 装入片上后，会被重复读取很多次，直到当前 layer、tile 或 channel block 处理完成。它的设计价值不在“能不能随机写”，而在“能不能让一次装载服务尽可能长的复用距离”。这意味着 weight buffer 常常优先追求三件事：较高净容量效率、较高读带宽、以及按 PE 阵列分发时的并行供数能力。常见误解是把 weight buffer 简化成“只读 SRAM”；更准确的说法是，它是一个为读主导复用而优化的 staged storage。

activation buffer 的约束则不同。激活数据往往既要被写入，也要被较快地消费。它一方面承接外层输入流或上游 layer 输出，另一方面要按当前 tile 的计算节奏被多个计算单元重复读取。在卷积、attention 或 GEMM 映射里，activation 的复用可以很强，但这种复用通常更短、更依赖 tiling 和窗口滑动方式，也更容易被双缓冲节拍左右。所以 activation buffer 的关键设计变量，往往不是“尽量大”，而是“能否在当前 tile 被消费时，同时把下一块 tile 搬进来”。这也是为什么 activation buffer 天然和 DMA overlap、double buffering、bank interleave 绑得很紧。

accumulator buffer 或 partial-sum buffer 又是第三类完全不同的对象。它不主要承担长距离只读复用，也不只是输入 staging，而是承担 `高频读改写`。一次 MAC 之后，部分和要么继续留在本地等待下一次累加，要么在若干轮累加后再写回外层。于是 accumulator buffer 最敏感的不是“能放多少”，而是“局部读改写回路有多短、每拍能承受多少并发更新”。如果它的端口、bank 组织或本地带宽设计不够，算力阵列会先在 psum 更新路径上堵住。常见误解是把 accumulator 也视为普通输入 buffer；实际上，它更像一个为局部反馈回路定制的工作区。

把这三类 buffer 放在一起比较，会发现它们至少在四个维度上天然不同。第一，生命周期不同。权重可能跨多个 tile 常驻，activation 常随 tile 滚动，psum 往往在较短窗口内不断更新后被导出。第二，读写方向不同。权重偏只读，activation 常常是“边装边读”，psum 则偏“边读边写回”。第三，复用模式不同。权重更像广播到多个 consumer，activation 更像流经局部窗口，psum 更像围绕单个输出元素反复回流。第四，性能风险不同。权重 buffer 配小了，外层带宽压力会上升；activation buffer 组织不好，流水 overlap 会失效；accumulator buffer 扛不住，则会直接在最内层把阵列停住。

这些差异会直接反映到 SRAM 组织方式上。weight buffer 更适合围绕读带宽和容量效率组织，可以容忍较弱的写路径，但需要良好的银行化分发能力。activation buffer 更强调搬运与消费并行，因此更需要和 bank 切分、prefetch 粒度、双缓冲边界一起设计。accumulator buffer 更关注本地反馈路径和更新热点，往往要求更高的局部写带宽、更短的数据返回路径，甚至更贴近 PE 的分布式布局。如果把三者都抽成“一个通用 local SRAM”，你在模型里就会错过真正的瓶颈位置。

这也是为什么 NPU 里的这些 buffer 更像 scratchpad，而不像 cache。它们的价值不来自硬件去猜哪些数据可能会复用，而来自设计者提前知道哪些数据一定会复用、复用多久、该以什么顺序搬。对 weight，设计者通常知道这一块权重会服务哪一批输出通道；对 activation，通常知道当前 tile 的消费顺序；对 psum，通常知道哪一组输出元素会在本地累计多少轮。既然局部性是可设计的，而不是可碰运气的，把这些 buffer 交给 cache 式自动替换通常不是最优解。

还有一个很重要的后果是：NPU 的片上 SRAM 容量不能只看总量，必须看按角色切分后的结构。一个“16 MB 片上 SRAM”的说法，如果不说明其中多少给 weight、多少给 activation、多少给 psum，以及各自多少 bank、多少读写带宽，几乎没有分析意义。因为很多设计瓶颈根本不在总容量，而在某一类 buffer 的读写不对称、bank 冲突或 refill 节拍没有对齐。后面到了 `weight-buffer-design.md`、`activation-buffer-and-double-buffering.md` 和 `on-chip-bandwidth-budget.md`，这种按角色而不是按总量思考的必要性会进一步变得明确。

从系统角度回看，把三类数据分角色管理，本质上是在提前阻断外层内存压力向内层扩散。若权重、激活、部分和共享一个统一而粗糙的本地 SRAM 池，某一类数据的临时热点就可能挤占另外两类的空间和带宽，最后把内部瓶颈做成“谁都不够用”。分角色之后，代价是调度更复杂、结构更定制，但收益是每类数据都可以围绕自己的复用规律和访问方向去优化。对强调 deterministic dataflow 的 NPU，这通常比做一个更“通用”的大池子更合理。

因此，weight、activation、accumulator buffer 的区别，不是同一块 SRAM 的三个视图，而是三类不同的本地资源原型。它们共享 SRAM 这一底层介质，却不共享同一个最优目标函数。理解这一点，后面讨论 NPU 内存层次和带宽预算时，你就不会把片上 SRAM 误看成“只要够大就行”的单一资源。

## 一句话理解

NPU 把片上 SRAM 拆成 weight、activation 和 accumulator buffer，不是为了细分名词，而是因为三类数据在复用距离、读写方向和局部带宽模式上根本不同，必须分别组织。

## 建模启示

在架构模型里，NPU 片上 SRAM 不能只建成一个统一的 `onchip_buffer_bytes`。至少应拆成按数据角色区分的多个资源，因为它们的瓶颈和调度语义不同。weight buffer 更像 `read-mostly staged storage`，activation buffer 更像 `streamed tile buffer`，accumulator buffer 更像 `high-frequency read-modify-write workspace`。

一个最小可用的抽象草图可以是：

```text
NpuBufferModel {
  role: enum { WEIGHT, ACTIVATION, ACCUMULATOR }
  capacity_bytes: uint64
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

如果只做粗粒度 roofline 估算，可以把三者折成总片上容量和总片上带宽；但只要你想解释“为什么同样 16 MB 片上 SRAM，两个 NPU 的吞吐差这么多”，这三类角色就必须拆开。因为差异往往不在总量，而在某一类 buffer 的 bank 组织、读写不对称和与计算节奏的耦合上。
