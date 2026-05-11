# 03 Topology 与 Routing

本章讨论的不是 router（路由器）内部，而是整个网络”怎么连、怎么走、哪里会堵”。

## 本章入口

- [Topology 与物理布局](./topology-layout.md)
- [Routing 与 Arbitration](./routing-arbitration.md)
- [Source Routing 与 Compiler-Driven NoC](./source-routing-compiler-driven-noc.md)
- [Hierarchical NoC 深化](./hierarchical-noc-deep-dive.md)
- [Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)
- [Mesh 专题](./mesh-deep-dive.md)
- [Torus 与 Ring 专题](./torus-ring-deep-dive.md)
- [Tree / Fat-Tree 专题](./tree-fat-tree-deep-dive.md)

## 一句话总纲

router 决定局部行为，topology（拓扑，网络节点的连接方式）与 routing（路由，数据包的路径选择策略）决定全局流量如何分布。架构探索里最有价值的问题，往往都发生在这一层。
