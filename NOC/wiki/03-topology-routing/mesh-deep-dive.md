<<<<<<< HEAD
# Mesh 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)、[Physical Realization 与 Floorplan-Aware NoC](../04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)、[Topology 量化对比](./topology-layout.md)、[Crossbar 与 Concentrated Mesh](./crossbar-concentrated-mesh.md)

## 为什么 mesh 仍然是主线

对大多数 tile-based AI accelerator（AI 加速器），mesh（网格拓扑）依然是最自然的第一选择，因为它同时兼顾：

- 规则性
- 可扩展性
- floorplan（芯片版图布局）兼容性
- 建模和验证成本

## Mesh 的核心优点

- 节点局部连接简单
- 适合二维 tile（计算单元）array
- deterministic routing（确定性路由）很自然
- 与编译器做 placement（放置）/ mapping（映射，将算子分配到硬件资源）配合相对容易

## Mesh 的核心问题

- 平均 hop（跳数）随规模上升
- 主干链路和中心区域容易形成热点
- 边缘 memory port（存储端口）可能导致路径不均匀

## 为什么它非常适合第一版 simulator

因为你可以快速把重点放在：

- wormhole（虫孔转发，数据包按 flit 逐跳流水前进）
- credit（信用计数流控）
- buffer（缓冲区）
- routing（路由）
- hotspot（热点，流量集中导致拥塞的链路或节点）

而不必先被过于复杂的拓扑结构干扰。

## 在 AI workload 里什么时候 mesh 很合适

- 流量较规则
- 局部性较强
- compiler 能把相互依赖的 tile 摆得较近
- memory port 不至于极端集中

## 什么时候 mesh 会开始吃亏

- all-to-all（全互连通信）或强 collective（集合通信）占比高
- memory 流量极其集中
- 芯片变得很大，长路径明显变多
- 物理长线开始显著改变 latency（延迟）/ credit round-trip（信用往返延迟）

## 你至少要做的 mesh 实验

- memory port 放边缘 vs 更分散
- cluster 化前后是否减轻全局热点
- packet size（数据包大小）/ buffer depth（缓冲区深度）对中心热点的影响

## 量化公式

对于 R×C 的 2D mesh（R 行 C 列，共 N = R×C 个节点）：

| 指标 | 公式 | 说明 |
|---|---|---|
| Diameter | R + C - 2 | 左上角到右下角的最短路径 |
| Average Hop (uniform random) | (R + C) / 3 | 所有 src-dst pair 的平均最短路径 |
| Bisection BW | min(R, C) × link_width | 沿长边方向切分时横跨的链路数 |
| Router Radix | 最大 5（4 方向 + 1 local） | 边角 router radix 更低（3 或 4） |
| Total Links | 2RC - R - C | 双向链路总数 |
| Router 总数 | R × C | 每个节点一个 router |

### 具体数值

| 规模 | Diameter | Avg Hop | Bisection BW (256-bit link, 1GHz) | Links |
|---|---|---|---|---|
| 2×2 | 2 | 1.33 | 64 GB/s (2 links) | 4 |
| 4×4 | 6 | 2.67 | 128 GB/s (4 links) | 24 |
| 8×8 | 14 | 5.33 | 256 GB/s (8 links) | 112 |
| 4×8 | 10 | 4.00 | 128 GB/s (4 links) | 52 |

## XY Routing 下的 Link Utilization 分布

在 uniform random traffic + XY routing 下，4×4 mesh 的链路利用率分布呈现明显的中心热点特征：

```text
列方向（vertical）链路利用率相对值：

     col0  col1  col2  col3
      |     |     |     |
row0  1     2     2     1
      |     |     |     |
row1  2     4     4     2
      |     |     |     |
row2  2     4     4     2
      |     |     |     |
row3  1     2     2     1

行方向（horizontal）链路利用率也类似：中心最高，边缘最低
```

为什么会这样：

- XY routing 先走 X 方向再走 Y 方向
- 位于中心的链路被更多 src-dst pair 的路径经过
- 中心四条链路（row1-col1、row1-col2、row2-col1、row2-col2 方向）承受最大压力
- 边角链路只被少数路径经过

实践意义：

- 网络饱和时，中心链路最先成为瓶颈
- 如果 memory port 放在边缘，从 memory 到中心 tile 的路径会经过高利用率区域
- 增加中心区域的链路带宽（asymmetric link width）可以提升整体吞吐

## Mesh vs Concentrated Mesh 量化对比

以 16 个 tile 为例：

| 指标 | 4×4 Mesh (16R) | Concentrated 2×2 Mesh (4R, k=4) |
|---|---|---|
| Router 数量 | 16 | 4 |
| Router Radix | 5 | 8 (4 mesh + 4 local) |
| Diameter (router hop) | 6 | 2 |
| Cluster 内延迟 | 0 (local) | 1 (crossbar 仲裁) |
| Bisection BW | 4 × link_width | 2 × link_width |
| Router 总面积 | 16 × area(radix=5) | 4 × area(radix=8) + 4 × crossbar(4) |
| 适合场景 | 流量分散、无明显局部性 | 流量有 cluster 局部性 |

关键取舍：

- Concentrated mesh 的 router 数量大幅减少（16→4），但每个 router 更大
- Concentrated mesh 的 bisection BW 降低（4→2 links），如果跨 cluster 流量多会成为瓶颈
- 如果 cluster 内流量占比 > 50%，concentrated mesh 通常更优

## 参数敏感度：Link Width 翻倍 vs Mesh 尺寸翻倍

当需要提升 mesh 的总带宽时，有两条路径：

| 策略 | 操作 | Bisection BW 变化 | Avg Hop 变化 | 面积代价 |
|---|---|---|---|---|
| Link width 翻倍 | 256b → 512b | 2× | 不变 | 布线面积 ~2×，router 稍大 |
| Mesh 尺寸翻倍 | 4×4 → 4×8 | 不变 (仍 4 links) | 增加 (2.67→4.0) | router 数量 2×，总面积 ~2× |
| Mesh 两维都翻倍 | 4×4 → 8×8 | 2× | 增加 (2.67→5.33) | router 数量 4×，总面积 ~4× |

结论：

- 如果目标是提升带宽且 tile 数不变 → **优先加宽 link width**，hop 不增加
- 如果 tile 数必须增加 → mesh 尺寸增长不可避免，考虑 concentrated mesh 控制 router 数量
- 8×8 以上的 flat mesh 通常应考虑切换到 hierarchical / concentrated 设计

## 本页结论

mesh 的价值，不在于它”最先进”，而在于它经常是最稳妥、最可落地、最适合建立第一版架构判断的基线。量化分析帮助你判断 mesh 在什么规模下仍然可用、什么时候需要切换到 concentrated mesh 或 hierarchical 设计。
=======
# Mesh 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)、[Physical Realization 与 Floorplan-Aware NoC](../04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)

## 为什么 mesh 仍然是主线

对大多数 tile-based AI accelerator（AI 加速器），mesh（网格拓扑）依然是最自然的第一选择，因为它同时兼顾：

- 规则性
- 可扩展性
- floorplan（芯片版图布局）兼容性
- 建模和验证成本

## Mesh 的核心优点

- 节点局部连接简单
- 适合二维 tile（计算单元）array
- deterministic routing（确定性路由）很自然
- 与编译器做 placement（放置）/ mapping（映射，将算子分配到硬件资源）配合相对容易

## Mesh 的核心问题

- 平均 hop（跳数）随规模上升
- 主干链路和中心区域容易形成热点
- 边缘 memory port（存储端口）可能导致路径不均匀

## 为什么它非常适合第一版 simulator

因为你可以快速把重点放在：

- wormhole（虫孔转发，数据包按 flit 逐跳流水前进）
- credit（信用计数流控）
- buffer（缓冲区）
- routing（路由）
- hotspot（热点，流量集中导致拥塞的链路或节点）

而不必先被过于复杂的拓扑结构干扰。

## 在 AI workload 里什么时候 mesh 很合适

- 流量较规则
- 局部性较强
- compiler 能把相互依赖的 tile 摆得较近
- memory port 不至于极端集中

## 什么时候 mesh 会开始吃亏

- all-to-all（全对全通信）或强 collective（集合通信）占比高
- memory 流量极其集中
- 芯片变得很大，长路径明显变多
- 物理长线开始显著改变 latency（延迟）/ credit round-trip（信用往返延迟）

## 你至少要做的 mesh 实验

- memory port 放边缘 vs 更分散
- cluster 化前后是否减轻全局热点
- packet size（数据包大小）/ buffer depth（缓冲区深度）对中心热点的影响

## 本页结论

mesh 的价值，不在于它“最先进”，而在于它经常是最稳妥、最可落地、最适合建立第一版架构判断的基线。
>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
