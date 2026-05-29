# AI 加速器里的 DMA

上级：[07 工作负载与案例](./README.md)

相关：[Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)、[DMA 与 NoC](../05-system-integration/dma-and-noc.md)、[HBM 到 Tile 的数据供给链](./hbm-to-tile-data-supply-chain.md)

## 这页在回答什么问题

为什么在 AI accelerator 里，DMA 往往比传统 SoC 里的 DMA 更核心、更复杂，也更值得单独研究；以及为什么很多 AI 芯片里真正的“执行骨架”不是 compute pipe，而是 DMA 驱动的数据供给链。

## AI 系统里的 DMA 不只是 I/O 辅助块，而是供数骨架

在通用 SoC 里，DMA 常被理解为“帮 CPU 搬数据的外设”；在 AI accelerator 里，这个定位通常完全不够。因为 compute 阵列是否高利用率，往往首先取决于 HBM、NoC、cluster SRAM、tile buffer 之间的数据能否按节拍稳定到位。DMA 在这里承担的不是偶发搬运，而是持续供数。

这意味着 AI DMA 的成功标准也变了。它不再只是“单次传输很快”，而是“能否在 steady-state 下持续把 compute 喂饱，同时不把 NoC、SRAM 和 writeback 自己堵死”。

## AI DMA 典型会跨哪些路径

最典型的路径通常包括：

- HBM -> cluster SRAM
- cluster SRAM -> tile local buffer
- partial result -> writeback buffer -> HBM
- parameter / metadata / control flow 的小粒度补充路径

这些路径里，真正难的不是哪一条单独存在，而是它们必须同时存在。refill、compute、writeback 常常并行发生，DMA 因此不只是“某一条搬运通道”，而是多条路径间的节拍协调器。

## 为什么它比传统 DMA 更难

AI 系统里的 DMA 更难，至少因为四件事会同时出现：

- 数据量巨大，而且长时间稳定存在
- stream 数多，常按 layer、cluster、tile、tensor role 交织
- overlap 是刚需，不是锦上添花
- local memory 和 NoC 都会显著反作用到 DMA 行为

换句话说，AI DMA 面对的是一个“持续供给链”，不是一个“独立搬运任务”。这就是它和普通 memory-to-memory DMA 的根本差异。

## 最重要的能力不是通用性，而是节拍组织能力

AI DMA 最关键的能力通常不是“支持多少花样接口”，而是：

- 能否维持足够的 outstanding 来隐藏 HBM latency
- 能否用合适 burst 和 stride 喂出对 DRAM/NoC 友好的流量形状
- 能否与 double buffering / N-buffering 配合形成稳态 overlap
- 能否让 refill 和 writeback 不互相放大波峰

如果这些能力缺一，compute 很容易表面上很强，实际上大部分时间都在等数据。

## 常见误解

常见误解：`AI 芯片的关键还是 MAC 数和算子映射`。实际上在很多 deterministic NPU 里，真正先把利用率拉跨的是供数链，而不是算力阵列本身。

常见误解：`AI DMA 只是更大带宽的 SoC DMA`。实际上它还承担了更强的节拍协调、overlap 组织和 local memory 耦合职责。

常见误解：`HBM 带宽够大，DMA 就不会是瓶颈`。实际上 HBM latency、NoC return path、SRAM port 和 writeback 冲突都可能先卡住。

## 一句话理解

AI 加速器里的 DMA 已经不是“辅助搬运器”，而是连接 HBM、NoC、SRAM 和 compute pipeline 的执行骨架。

## 建模启示

这页最适合显式接入 `Resource / Topology / Interaction / Capability`：

- `Resource`：HBM port、NoC path、cluster SRAM bank、tile buffer、writeback slot
- `Topology`：HBM 到 cluster，到 tile，再回写的层级链
- `Interaction`：refill、consume、writeback、buffer flip、completion visible
- `Capability`：tile size、buffer count、burst policy、outstanding depth、stream priority

一个最小结构草图是：

```text
AISupplyStage {
  stage_id
  src
  dst
  bytes
  overlap_group
}
```

如果只关心上界，可以把整条链折叠成最大瓶颈带宽；如果关心断供、尾延迟或 steady-state 稳定性，就必须显式保留各 stage 的状态与切换事件。
