# Mesh 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)、[Physical Realization 与 Floorplan-Aware NoC](../04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)

## 为什么 mesh 仍然是主线

对大多数 tile-based AI accelerator，mesh 依然是最自然的第一选择，因为它同时兼顾：

- 规则性
- 可扩展性
- floorplan 兼容性
- 建模和验证成本

## Mesh 的核心优点

- 节点局部连接简单
- 适合二维 tile array
- deterministic routing 很自然
- 与编译器做 placement / mapping 配合相对容易

## Mesh 的核心问题

- 平均 hop 随规模上升
- 主干链路和中心区域容易形成热点
- 边缘 memory port 可能导致路径不均匀

## 为什么它非常适合第一版 simulator

因为你可以快速把重点放在：

- wormhole
- credit
- buffer
- routing
- hotspot

而不必先被过于复杂的拓扑结构干扰。

## 在 AI workload 里什么时候 mesh 很合适

- 流量较规则
- 局部性较强
- compiler 能把相互依赖的 tile 摆得较近
- memory port 不至于极端集中

## 什么时候 mesh 会开始吃亏

- all-to-all 或强 collective 占比高
- memory 流量极其集中
- 芯片变得很大，长路径明显变多
- 物理长线开始显著改变 latency / credit round-trip

## 你至少要做的 mesh 实验

- memory port 放边缘 vs 更分散
- cluster 化前后是否减轻全局热点
- packet size / buffer depth 对中心热点的影响

## 本页结论

mesh 的价值，不在于它“最先进”，而在于它经常是最稳妥、最可落地、最适合建立第一版架构判断的基线。
