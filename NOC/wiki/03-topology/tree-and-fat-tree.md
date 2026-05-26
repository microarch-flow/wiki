# Tree And Fat Tree

上级：[03 Topology](./README.md)
相关：[Topology Design Metrics](./topology-design-metrics.md), [Topology Physical Realization](./topology-physical-realization.md)

## 这页在回答什么问题

tree 和 fat-tree 为什么在广播、规约、上收型流量里有天然吸引力，但在片上通用数据面里又往往不是默认解。

这类拓扑的核心魅力在于层级流量与层级结构天然吻合；核心问题则在于，上层节点和链路会不会变成昂贵且拥挤的集中点。

## Tree：把流量方向性结构化

tree 最适合服务一种很明确的流量形状：许多叶子节点的数据逐层向上汇聚，或者从根节点向下分发。

这正好对应：

- gather
- reduce
- broadcast

在这类模式下，tree 的优点几乎是结构级的，不需要复杂 routing 才能显现。路径天然唯一，层次清楚，编译器也容易推导阶段性同步关系。

## Tree 的问题不是“慢”，而是上层太容易被压

普通 tree 的根本问题，是越往上越集中，但带宽和 router 资源未必同步变强。于是：

- root 附近最容易成瓶颈
- 共享越高层，越像把大量流量灌进漏斗口
- 一旦 workload 不再是单纯 gather/reduce，而变成 more general point-to-point，结构优势会迅速消失

这就是为什么 tree 对特定 collective 很强，对通用 NoC 却常常不够稳。

## Fat-tree：承认上层要更“胖”

fat-tree 的核心思想非常务实：既然普通 tree 的问题是越往上越拥挤，那就主动让上层带宽和交换能力更强。

换句话说，fat-tree 不是“另一种树”，而是给树的上层补容量。它通常带来：

- 更强的 bisection bandwidth
- 更好的高并发承载能力
- 对更复杂 traffic 的更高容忍度

但代价很重：

- 更多链路
- 更高 radix 的上层 switch
- 更难塞进规则二维 floorplan

所以 fat-tree 的逻辑价值很强，物理代价也很少能被忽略。

## 为什么片上通用主网络不默认选它

AI 芯片的大多数 tile 布局更接近二维阵列，而不是抽象树形层级。mesh 类结构与 floorplan 的贴合度天然更高。

而 tree / fat-tree 的尴尬在于：

- 逻辑结构是层次的
- 物理芯片却往往是平面的

这意味着高层节点和长链路需要被“额外安放”。在机柜级网络里，这不算大问题；在片上，它会迅速变成布线、面积和热约束问题。

## 为什么它们在 AI NoC 里又很重要

因为很多 AI workload 确实含有强 collective 子问题。partial sum reduction、权重广播、某些同步树，都天然适合树形结构。

所以在 AI 芯片里，tree family 经常最合理的角色不是取代主 NoC，而是：

- 作为 reduction overlay
- 作为 broadcast overlay
- 作为 memory-side hierarchy 的一部分

这时你不是在问“树能不能做全能网络”，而是在问“某个子流量是否值得给专用几何结构”。

## 一个关键判断：通用路径和专用路径不要混为一谈

很多讨论 tree 时会犯一个错误：拿它和 mesh 做全盘替代比较。更合理的比较方式通常是：

- mesh 作为通用 packet network
- tree 作为某类 collective 的专用补层

这样看，tree 的价值会非常清楚，因为它在特定模式下提供的是结构级匹配，而不是平均意义上的普适优势。

## Fat-tree 在芯片上的价值更多是上界参考

fat-tree 最有价值的地方，很多时候不是“直接照搬”，而是给你一个结构上界：

- 如果某 workload 明显受跨区带宽限制
- 如果你想知道“多给上层容量”理论上会带来什么收益

那 fat-tree 是非常好的参照物。它能帮助你判断：当前 mesh 或 hierarchical mesh 的瓶颈，是 routing 问题、调度问题，还是确实应该在结构上给上层更多带宽。

## 常见误解

常见误解：tree 的 hop 数少，所以一定更适合片上网络。  
实际上：对 gather/reduce 它很强，但一旦放到通用数据面，root 附近瓶颈和物理布局问题会迅速放大。

常见误解：fat-tree 只是更贵的 tree。  
实际上：它是在显式解决 tree 的上层带宽短板，因此更像“带容量补偿的层级网络”，不是简单昂贵版。

## 一句话理解

tree 用层级路径天然适配 gather/reduce，fat-tree 再用更胖的上层缓解汇聚瓶颈；它们在 AI 芯片里最常见的合理角色，是专用 collective 结构，而不是通用主 NoC。

## 建模启示

对 tree，至少保留：

```text
tree_height
root_fan_in
upper_level_bandwidth
```

对 fat-tree，还要显式增加：

```text
bandwidth_per_level[]
switch_radix_per_level[]
```

如果做通用 point-to-point 比较，不能只拿 hop 数和 mesh 比；还要把 root/upper-level hotspot 单独统计。  
如果做 collective overlay 分析，则可以把 tree 抽象成多级 reduce/broadcast pipeline，并记录 `level_service_time`，这会比把它硬塞进通用 packet network 更贴近真实用途。
