# 03 Topology

这一章只讨论一件事：router 之外，整个网络在几何上到底怎么连。

这里不讨论 packet 已经进网后下一跳怎么选，那是 `04-routing-and-flow-control` 的问题。这里先把结构层说清楚：

- topology 影响哪些一阶指标
- 为什么 mesh 在 NPU 上几乎总是 baseline
- ring、tree、fat-tree、crossbar、concentrated mesh 各自的真实边界
- 为什么很多“理论上更优”的拓扑一落到 floorplan 就开始变味
- 应该怎样从 workload 和物理约束反推选型

## 本章入口

- [Topology Design Metrics](./topology-design-metrics.md)
- [Mesh And Torus](./mesh-and-torus.md)
- [Ring And Hierarchical Ring](./ring-and-hierarchical-ring.md)
- [Tree And Fat Tree](./tree-and-fat-tree.md)
- [Crossbar And Concentrated Mesh](./crossbar-and-concentrated-mesh.md)
- [Flattened Butterfly Dragonfly](./flattened-butterfly-dragonfly.md)
- [Topology Physical Realization](./topology-physical-realization.md)
- [Topology Selection Framework](./topology-selection-framework.md)

## 一句话总纲

topology 决定的是网络的几何上限：路径长度、横截面带宽、router radix、长线代价和热点形状；routing 只能在这个上限之内做策略优化。
