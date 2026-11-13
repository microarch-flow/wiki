# Scratchpad 和 cache 都是 SRAM，差异在哪

上级：[SRAM 应用形态](./README.md)
相关：[Cache 里的 SRAM：tag 阵列与 data 阵列的差异](./cache-sram-tag-data-arrays.md), [“数据搬运优先”原则在 NPU 设计中的体现](../../01-memory-hierarchy/04-npu-case/data-movement-first-principle.md)

## 这页在回答什么问题

当底层介质都还是 SRAM，为什么 scratchpad 和 cache 会在可预测性、面积效率、编程模型和性能风险上呈现完全不同的性格。真正需要回答的问题不是“哪个更快”，而是谁在负责管理局部性，谁在为局部性判断失误承担代价。

## 地址管理与数据放置方式

Scratchpad 和 cache 最容易被混淆，是因为两者表面上都像”离计算很近的一小块 SRAM”——就像自动挡和手动挡的车表面都是”能开的汽车”。如果只看介质，这个判断没错；但如果把系统语义也纳入，就会发现它们几乎站在两种相反的设计哲学上。cache 是自动挡：硬件替你决定什么时候换挡（哪些数据值得暂存），你只管踩油门。scratchpad 是手动挡：什么时候换挡、换几挡，完全由你自己控制。两者的根本差异，不在 cell，不在 bank，而在”谁管理局部性”。

先看 cache。它选择替软件承担一部分复杂性，于是硬件必须增加 tag array、比较逻辑、替换状态、脏位管理、refill/writeback 路径，以及由此带来的命中不确定性。好处很明显：对通用代码友好，程序员不需要显式安排每一次数据搬运；若访问模式与硬件的局部性假设契合，平均延迟会显著下降。代价同样明确：你把性能的一部分交给了硬件猜测，猜对了收益大，猜错了就会出现 miss、污染、抖动、尾延迟上升，且这些现象不总是容易从软件侧直接解释。

再看 scratchpad。它基本拿掉了 cache 的那层猜测。没有 tag compare，就没有“命中/未命中”这一层概率事件；没有自动替换，就不存在因为某条 line 被驱逐而产生的隐式副作用。取而代之的是，软件必须明确知道数据什么时候需要在本地、什么时候可以被覆盖、什么时候需要和外层存储同步。显式放置可以让数据生命周期更容易分析，但不能保证访问时间固定。即使数据已在本地，DMA、bank、端口、仲裁或下游背压仍可能造成等待；只有在明确访问与资源条件后，才能判断时间界限。

这组差异立刻会反映到面积效率上。cache 要为 tag、比较器、替换状态、coherence 或维护逻辑付费，因此它的一部分面积预算用于非 payload 结构。实际可用容量还取决于阵列、端口、控制及实现约束。scratchpad 没有这些元数据和命中判断路径，因此在同面积下往往能提供更高的数据净容量，也更容易按业务需求定制 bank 划分和端口组织。常见误解是认为 scratchpad 只是”没有 tag 的简化 cache”——就像说手动挡只是”没有自动变速箱的简化版”。更准确的说法是，scratchpad 把 cache 的硬件管理成本转移给了软件控制与调度复杂度：硬件更简单了，但驾驶员的技术要求更高了。

性能行为上的差异更值得架构师关注。cache 优化的是”平均情况”——就像出租车司机凭经验选路线，大多数时候走得不错，偶尔踩雷堵在路上。scratchpad 优化的是”计划内情况”——更像按预定路线行驶的公交车，仍可能受其他交通流影响。如果 workload 有较好的时间/空间局部性，cache 会让大量访问自动命中本地 SRAM；如果软件能提前看见数据流结构，scratchpad 就可以在计算前显式搬运、双缓冲、复用和排布数据，从而把局部性从”希望硬件猜到”变成”设计时就确定好”。因此，cache 更适合控制流复杂、访问模式难静态预测的通用负载；scratchpad 更适合访问模式规则、块化明显、可由编译器或运行时调度的数据流型负载。这里的差别不是谁绝对更先进，而是谁在当前 workload 上更接近正确的责任分配。

可预测性要结合资源和访问条件判断。cache 的服务时间随命中、替换和争用状态变化；如果初始状态、访问序列与规则均已知，也可以确定性地模拟。Scratchpad 虽然显式放置数据，但同一 bank 或端口上的并发请求仍可能排队。实时系统需要进一步约束或分析这些竞争，不能只凭存储角色判断最坏情况。

[NVIDIA 的 CUDA Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#shared-memory-and-memory-banks)介绍了 GPU shared memory 的 bank 冲突及其对吞吐的影响。它是具体平台的例子；其他 scratchpad 的 bank 映射、广播和冲突规则应以目标实现为准。

与此同时，scratchpad 并不天然更优。它把复杂性往软件侧推之后，软件必须真的能承担这件事。若工作负载变化大、数据依赖复杂、复用关系不稳定，scratchpad 的显式管理成本会很高，错误也更难被抽象掉。你可能需要写复杂的 tiling、prefetch、double-buffering、eviction 和同步逻辑；如果容量估计、分块边界或搬运时序算错，性能会明显崩。cache 至少还能在你不完全理解访问模式时给出一个“够用的自动近似”。因此，两者的 trade-off 从来不是“硬件复杂 vs 硬件简单”，而是“硬件多承担一点不确定性，还是软件多承担一点调度责任”。

从数据流角度看，这个差异在 AI/NPU 中尤其尖锐。很多 NPU 工作负载的复用模式是结构化的：tile 大小、权重块、激活块、部分和生命周期都相对可推导。此时 scratchpad 式本地 buffer 往往比 cache 更合适，因为你不是在赌局部性，而是在设计局部性。相反，在 CPU 的通用负载里，程序控制流和数据访问模式常常变化更复杂，硬件 cache 的透明性价值就更高。后面到 `npu-memory-hierarchy.md` 和 `data-movement-first-principle.md` 时，这条分界会变成一个更明确的系统结论。

还有一个常见误解值得单独指出：scratchpad 的“确定性”不等于“没有冲突”。除了不使用 cache 的自动替换，系统仍需处理 bank 冲突、DMA 争用、容量不足或双缓冲节拍失配。能否由软件观察和推导这些冲突，取决于接口及实现。也就是说，scratchpad 并没有消灭存储器复杂性，而是把复杂性从“猜测与替换”换成了“显式规划与调度”。这也是为什么 scratchpad 经常和 DMA、banked SRAM、软件流水、tile 调度一起出现，而不是独立存在。

把两者放回 SRAM 应用谱系里看，就能得到一个更稳的判断：cache 是“让硬件管理局部性”的 SRAM 形态，scratchpad 是“让软件管理局部性”的 SRAM 形态。前者用管理结构换取透明性；后者用显式放置与调度换取对数据生命周期的控制。净容量和时延可预测性要在相同约束下分别评估。这个结论后面会在 MCU、NPU 和系统级建模里不断复用。

## 一句话理解

Cache 由硬件管理数据放置和替换；scratchpad 通常由软件、编译器或显式调度机制安排数据。两者的响应时间和可预测性仍取决于访问与资源条件。

## 建模启示

在性能模型里，是否区分 cache 和 scratchpad 取决于要回答的问题。如果问题依赖 cache 命中或替换，应表达相关状态和访问规则；scratchpad 则要按问题考虑 `placement / prefetch / DMA schedule / bank conflict`。两者都可能受共享资源和到达次序影响；统计近似应说明输入与适用范围。

一个并列抽象草图可以写成：

```text
CacheResource {
  hit_latency_cycles: int
  miss_latency_cycles: int
  hit_rate_model: object
  replacement_policy: enum
}

ScratchpadResource {
  local_latency_cycles: int
  dma_fill_latency_cycles: int
  bank_count: int
  software_visible_capacity_bytes: uint64
  requires_explicit_schedule: bool
}
```

对应事件流也应不同：

```text
event CacheAccess(req_id, addr)
event CacheHit(req_id)
event CacheMiss(req_id)

event DmaFillIssue(buf_id, tile_id)
event DmaFillDone(buf_id, tile_id)
event ScratchpadRead(buf_id, bank_id, tile_id)
```

若每次请求从发出到数据返回独立统计，且 `miss_penalty` 定义为 miss 相比 hit 的增量，则平均访问时间可写为 `hit_latency + miss_rate * miss_penalty`；若 `miss_latency` 是 miss 的完整耗时，则等价写成 `hit_rate * hit_latency + miss_rate * miss_latency`，其中 `hit_rate + miss_rate = 1`。该平均式不能直接相加为重叠的程序 stall 时间，也不包含未计入的排队或并发影响。scratchpad 的关键问题通常也不是用命中率表达，因为它的关键问题往往不是平均命中率，而是某次 tile 是否按时搬到位、某几个 bank 是否被同时打爆。反过来，如果把 cache 也建成“只要软件安排好就总命中”，模型就会严重高估它在通用负载上的稳定性。
