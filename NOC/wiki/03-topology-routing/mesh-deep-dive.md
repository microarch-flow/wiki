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
