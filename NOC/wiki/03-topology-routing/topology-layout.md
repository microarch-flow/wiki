# Topology 与物理布局

上级：[Topology 与 Routing](./README.md)

相关：[架构探索方法](../05-modeling-evaluation/architecture-exploration.md)

## 为什么拓扑不是“画图问题”

拓扑同时影响：

- 平均 hop count
- 最远路径长度
- bisection bandwidth
- wire length
- router radix
- floorplan 兼容性
- 编译器 placement 自由度

所以它既是通信问题，也是面积、功耗和实现问题。

## 架构探索中至少要会比较的几类拓扑

### Mesh

优点：

- 规则
- 易布局布线
- 易建模

缺点：

- 边角节点的访问不均匀
- 平均 hop 随规模增大而上升

### Ring

优点：

- 简单
- router 开销低

缺点：

- 延迟和带宽伸缩性差

### Tree / Fat-tree

适合聚合与分层流量，但高层链路和交换点成本敏感。

### Hierarchical NoC

例如：

- cluster 内 crossbar / shared SRAM
- cluster 间 global mesh

这是 AI accelerator 里非常重要的主线，因为它直接连接：

- tile group 的规模
- 本地数据复用
- router 数量
- cluster 内外 traffic 比例

## 对 AI 芯片特别关键的两个问题

### Flat mesh 还是 cluster-hierarchical

这通常不是纯 NoC 决策，而是与：

- tile 面积
- local SRAM 大小
- 编译器切分粒度
- workload 的空间局部性

共同决定。

### HBM / DMA / SRAM bank 放在哪里

端点位置会决定热点分布。  
同一套 router 参数，在不同 memory placement 下可能出现完全不同的拥塞图。

## 必须跟踪的拓扑指标

- average hop count
- diameter
- bisection bandwidth
- router radix
- link count
- physical wire length
- placement compatibility

## 一个实用判断

对 AI tile 架构来说，最重要的往往不是“理论最优拓扑”，而是：

在真实 floorplan、真实 memory placement、真实 workload 下，哪种拓扑能以最低复杂度获得更好的稳定吞吐。
