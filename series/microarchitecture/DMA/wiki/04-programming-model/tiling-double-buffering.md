# Tiling、Double Buffer 与 Overlap

上级：[04 软件栈与编程模型](./README.md)

相关：[AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)、[HBM 到 Tile 的数据供给链](../07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)

## 这页在回答什么问题

为什么在 AI 和高性能系统里，DMA 最重要的价值往往不是单次搬运速度，而是支撑稳定 overlap；以及为什么 double buffering 不是“多开一块 buffer”这么简单，而是一个严格受搬运与计算时序约束的设计选择。

## 没有 tiling 和 buffering 时，系统节拍通常是串行的

先看最朴素的执行方式。假设一层计算需要处理很多数据块，而片上 buffer 放不下整份数据，于是系统只能按 tile 分批处理。若没有任何重叠机制，节拍通常是：

1. DMA 把 tile `i` 从外存搬到片上 buffer。
2. compute 消费 tile `i`。
3. DMA 再把 tile `i+1` 搬进来。
4. compute 再消费 tile `i+1`。

这条链是严格串行的。总时间近似等于每个 tile 的 `搬运时间 + 计算时间` 之和。只要外存 latency 不小，compute 就会大量空等。

## Tiling 先决定任务粒度，double buffering 再决定节拍组织

很多讨论把 tiling 和 double buffering 混成一件事，但它们解决的是两个不同层次的问题。tiling 回答的是“每次处理多大的一块数据”，它影响 local SRAM 占用、burst 形状、row locality 和单次 DMA 任务粒度。double buffering 回答的是“这些 tile 的搬运与计算是否能重叠”，它影响的是时间组织，而不是空间切分本身。

这也是为什么 tile size 选错时，double buffering 往往救不了系统。tile 太小，DMA 任务碎、burst 短、控制开销高；tile 太大，又会吃掉过多 SRAM，让双缓冲本身放不下。真正有效的设计必须把 tile 大小和 buffering 策略一起考虑。

## Double buffering 的核心是用空间换时间

double buffering 的最小结构，是准备两个可轮换的 buffer：A 和 B。当 compute 正在消费 A 时，DMA 同时向 B 填充下一块；两者完成后才能轮换角色。这个机制像餐厅的两个备菜台：一个台正被厨师取用时，另一个台在准备下一批菜，让厨师不必在每道菜之间停下来等。这个类比只在“取用”和“备菜”能并行时成立；它一旦被理解成“只要多一个台就一定不等”，就错了。

真正的边界条件是：只有当下一块数据准备速度足以跟上当前块消耗速度时，double buffering 才能把等待隐藏掉。否则厨师仍然会空等，只不过等待的位置从“每轮都显式停住”变成了“某个 buffer 迟迟没准备好”。

## 关键条件：收益取决于搬运时间和计算时间的相对关系

设单个 tile 的 DMA 搬运时间为 `T_dma`，计算时间为 `T_comp`。没有重叠时，每个 tile 大致花 `T_dma + T_comp`。有理想 double buffering 时，稳态每轮吞吐更接近 `max(T_dma, T_comp)`。

### 单次任务与有限批次

假设每块输入 DMA 要 `D=2` cycle，计算要 `C=5` cycle。DMA 与计算资源独立，各自一次处理一块；两个 buffer A、B 轮换；计算只能在对应搬运完成后开始，且 buffer 在计算结束前不可覆盖。忽略启动、写回和仲裁成本。

| 时间区间 | DMA | Compute | buffer 约束 |
|---|---|---|---|
| 0–2 | tile 1 → A | 等待 | A 写入中 |
| 2–4 | tile 2 → B | tile 1：2–7 | B 写入后等待 |
| 4–7 | 空闲 | tile 1 | A 不能提前复用 |
| 7–9 | tile 3 → A | tile 2：7–12 | A 已由 tile 1 释放 |
| 9–12 | 空闲 | tile 2 | tile 3 等待计算 |
| 12–17 | 空闲 | tile 3 | 结束后释放 A |

因此单 tile 完成时间为 `D+C=7`，三个 tile 的总时间为 17，理想稳态完成间隔为 `max(D,C)=5`。串行执行三个 tile 需要 21 cycle。一般情况下，`N≥1` 的理想有限批次是 `D+C+(N-1)×max(D,C)`。`N=0` 时没有工作。这里的稳态间隔既不是首块完成延迟，也不是有限批次总时间。

若 DMA 和 compute 共用单端口 SRAM，或 DMA 读、写争同一半双工互连，独立并行假设失效。即使有两个 buffer，操作也可能因端口冲突而串行。资源带宽的计算见 [参数与公式速查](../06-performance-modeling/parameter-reference.md#1-路径带宽上界与共享资源)。

这立刻给出三个判断：

- 若 `T_dma ~= T_comp`，重叠收益最大，因为两者都被较充分利用。
- 若 `T_dma >> T_comp`，系统本质上是 memory-bound。double buffering 只能把计算等待部分藏起来，但总瓶颈仍然是搬运。
- 若 `T_comp >> T_dma`，系统更偏 compute-bound。double buffering 能轻松隐藏搬运，但额外 buffer 可能收益有限。

所以常见误解“double buffering 总能消除 stall”是错的。它最多只能把总时间压向两者中的较大者，不能消除主导瓶颈本身。

## 为什么它总是和 DMA 绑在一起

没有 DMA，双缓冲很难成立，因为 CPU 不适合在后台稳定推动下一块 tile 的搬运。DMA 的价值正在于让搬运成为独立执行流，于是 compute 才能和它并行存在。更进一步，DMA 还要负责让这种并行不是偶尔成立，而是稳态成立：descriptor 不能断、outstanding 不能太小、SRAM 端口不能被 writeback 压死、completion 不能拖住下一轮切换。

所以 double buffering 不是“软件技巧”，而是 DMA、local memory 和 compute pipeline 的联合设计。

## Tiling 和 memory system 的耦合不能回避

tile 大小既决定 compute 的工作集，也决定 DMA 和 memory system 看到的访问形状。大 tile 常常更有利于长 burst、DDR/HBM row locality 和较低控制开销；但它也要求更大的片上 buffer，使双缓冲代价上升。小 tile 则可能更易调度、更易塞进 SRAM，却会让 DMA 任务碎裂、completion 更频繁、overlap 更难维持。

这正是为什么 tiling 不能只从算子映射角度选，而必须同时看 [RAM wiki 的 row locality](../../../../storage/01-memory-hierarchy/02-access-paths/sram-vs-dram-access-pattern.md) 和外存带宽利用率。某些数学上漂亮的 tile，可能在 memory system 视角里非常糟糕。

## 什么情况下需要 N-buffering 或 triple buffering

双缓冲不是唯一答案。若 `T_dma` 波动很大，或者路径里除了 refill 与 compute 之外还有显著 writeback / post-process 阶段，双缓冲可能不足以覆盖所有不确定性。这时会出现 triple buffering 或更一般的 N-buffering，用更多空间换更平滑的流水。

但这不是免费午餐。buffer 数量一增加，状态机、依赖关系、completion 追踪和 SRAM 占用都会变复杂。只有当时序波动或多级流水确实让双缓冲不够时，N-buffering 才值得。

## 一个简化时序图

```text
time ---->

DMA:   fill A      fill B      fill A      fill B
COMP:            use A      use B      use A

Buffer A: filling -> ready -> draining -> empty -> filling
Buffer B: empty   -> filling -> ready -> draining -> empty
```

这个图只表达稳态节拍，不表达启动阶段和尾部 bubble。真实系统里，第一块 tile 前面一定有 warm-up，最后一块后面一定有 drain；如果这些边角成本也重要，模型里就不能只用稳态 `max(T_dma, T_comp)` 近似。

## 常见误解

常见误解：`double buffering 就是多开一块 buffer`。实际上它的本质是把串行的搬运-计算链改写成可重叠的两条执行流。

常见误解：`double buffering 总能消除 stall`。实际上只在 `T_dma` 能大体跟上 `T_comp` 时才能最大化收益，memory-bound 时瓶颈仍然存在。

常见误解：`tile 只由算子计算逻辑决定`。实际上 tile 同时决定 DMA 粒度、burst 效率、外存 row locality 和片上 SRAM 压力。

## 一句话理解

double buffering 的本质是用额外 buffer 空间把 `搬运` 和 `计算` 组织成并行流水，而它能否真正隐藏延迟，取决于搬运时间和计算时间是否匹配。

## 建模启示

这页最关键的不是建带宽公式，而是建 buffer 状态机。event-driven 仿真里，至少要显式追踪两个或多个 buffer 的状态，以及 compute 请求下一块时目标 buffer 是否已经 ready。

一个最小结构草图是：

```text
TileBuffer {
  state: empty | filling | ready | draining
  tile_id
}
```

建议至少保留这些事件：

```text
fill_start
fill_done
compute_start
compute_done
buffer_flip
```

如果只关心稳态吞吐，可以用 `throughput ~= 1 / max(T_dma, T_comp)` 的近似；如果关心启动 bubble、尾部 drain 或偶发断供，就必须显式建模 buffer 状态转换。
