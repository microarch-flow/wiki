# DMA 对照矩阵

上级：[08 DMA IP 与产业视角](./README.md)

相关：[CPU / GPU / NPU 系统中的 DMA 分工](../07-workloads-case-studies/cpu-gpu-npu-comparison.md)、[DMA IP 评估清单](./dma-ip-checklist.md)

## 这页在回答什么问题

把不同类型 DMA 放在同一张矩阵里时，最该对照什么；以及如何避免把来自不同系统画像的 DMA，用一套误导性的“统一评分尺”硬比。

## 先说明这张表不在比较“谁更强”

DMA 对照表最容易滑向一种错误用法：拿不同系统里的 DMA 做简单排名，好像可以选出“最先进的 DMA”。这张表不该这样用。它真正的用途是帮助你快速判断：某类 DMA 的设计中心是什么，它最怕什么，它的关键能力应该如何被解释。

因此，表格里每一行都不该被理解成“一个名字类别”，而应被理解成一个 `系统位置 + 主传输路径 + 控制模式 + 完成语义` 的组合画像。

## 对照矩阵

| 类型 | 典型位置 | 主要路径 | 最核心约束 | 最关键能力 |
| --- | --- | --- | --- | --- |
| SoC AXI DMA | 片上互连 | DDR/SRAM/外设 | burst、仲裁、memory return path | 高效片上事务组织 |
| Peripheral DMA | 外设旁 | FIFO <-> memory | 实时性、稳定节拍、低复杂度 | 低 CPU 介入与周期稳定 |
| PCIe NIC DMA | 设备侧 | host <-> NIC buffer | ring、小包压力、completion/moderation | batching 与 steady-state |
| NVMe DMA | 设备侧 | host <-> storage queue | 深队列、completion 回收、块导向稳态 | completion 驱动的高并发 |
| GPU Copy Engine | GPU 内外边界 | host <-> device / device <-> device | copy-compute overlap、stream 争用 | 异步执行图中的 copy 通路 |
| AI Local DMA | tile/cluster 附近 | HBM/NoC/SRAM/tile | bank/port、buffer flip、供数节拍 | 与 compute 强耦合的局部供数 |

## 怎么用这张表

最正确的用法不是问“哪一行最好”，而是先问：

- 我的系统更像哪一行
- 我的主瓶颈更像哪种约束
- 我需要的是更强通用性，还是更强局部匹配

这三个问题能帮你快速决定后续该看哪类 feature、哪类 counter、哪类案例，而不是被大而全的功能表拖着走。

## 这张表最容易被误读的地方

第一，`AI Local DMA` 不会因为没有 host queue 或 PCIe feature 就“更弱”，因为它本来服务的是另一条路径。第二，`GPU Copy Engine` 也不该因为不强调 per-packet moderation 就被拿来和 NIC DMA 比短长。第三，`Peripheral DMA` 不会因为没有复杂 virtualization 就显得落后，它可能恰恰在自己的目标系统里是更合理的点。

也就是说，这张表的价值在“保留差异”，不是“抹平差异”。

## 常见误解

常见误解：`DMA 对照矩阵就是一张功能排行榜`。实际上它首先是一张系统画像对照表。

常见误解：`feature 多的一行就更先进`。实际上 feature 是否有价值取决于它服务的路径和完成语义。

常见误解：`同名能力可以直接横比`。实际上例如 queue、completion、channel 这些词在不同系统里的含义和负载完全不同。

## 一句话理解

不同 DMA 的差异，本质上来自它们服务的数据路径、完成语义和系统瓶颈完全不同，所以对照矩阵的第一任务是保留这种差异。

## 建模启示

这页适合把不同 DMA 类型压成统一的 high-level profile，再让后续模型按 profile 选择细节。

```text
DMATypeMatrixRow {
  type
  dominant_path
  dominant_bottleneck
  completion_boundary
}
```

如果只做横向比较，这四项就足够；如果要进入架构探索或 IP 评审，再分别展开到更细的状态和能力项。
