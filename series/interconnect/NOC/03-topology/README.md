# 03 拓扑与物理组织

> 本页保留原章节入口。[查看现行分类与完整阅读顺序](../SUMMARY.md#03-topology)。

<span id="03-topology"></span>本章先定义拓扑指标，再比较连接方式、层次化组织和物理实现。连接图回答“哪里可以连接”；路由回答“具体选择哪条路径”。路径上的竞争、延迟与成本还取决于流量和实现。

## 本章入口

1. [拓扑设计指标](./topology-design-metrics.md)：统一距离、端口数和切面容量的统计口径。
2. [Mesh 与 Torus](./mesh-and-torus.md)：比较二维相邻连接与环回连接。
3. [Ring 与分层 Ring](./ring-and-hierarchical-ring.md)：分析单环路径及跨层资源。
4. [Tree 与 Fat-tree](./tree-and-fat-tree.md)：区分树形路径、复制、归约和上层容量。
5. [Crossbar 与 Concentrated Mesh](./crossbar-and-concentrated-mesh.md)：区分交换连接与多个端点的集中接入。
6. [Flattened Butterfly 与 Dragonfly](./flattened-butterfly-dragonfly.md)：阅读高端口数和分组连接的具体构造。
7. [层次化与混合互连](./hierarchical-and-hybrid-topology.md)：分析局部、全局和跨区边界。
8. [拓扑与物理实现](./topology-physical-realization.md)：把连接图映射到布局、链路和时序。
9. [拓扑选型](./topology-selection-framework.md)：在相同需求和明确约束下比较候选方案。

<span id="一句话总纲"></span>拓扑提供可能的连接；需要结合路由、流量和物理实现，才能判断系统行为。
