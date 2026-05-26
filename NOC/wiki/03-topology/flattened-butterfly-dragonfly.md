# Flattened Butterfly Dragonfly

上级：[03 Topology](./README.md)
相关：[Tree And Fat Tree](./tree-and-fat-tree.md), [Topology Physical Realization](./topology-physical-realization.md)

## 这页在回答什么问题

flattened butterfly、dragonfly 这类高-radix 拓扑在 HPC 文献里为什么那么吸引人，以及在片上系统里到底还能借来什么。

这页不是为了把它们包装成 NPU 候选主流，而是为了把“哪些思想可借、哪些结构不宜照搬”讲清楚。

## 它们共同的核心直觉：用更高 radix 换更少 hop

mesh 家族的逻辑是：保持低 radix，让路径多走几跳。flattened butterfly、dragonfly 的逻辑相反：提高每个 router 的连接能力，让网络更扁平，减少 hop 数。

图论上这很诱人，因为它通常带来：

- 更低 diameter
- 更低 average hop
- 更强的跨区带宽组织能力

如果只看这些指标，它们会像“明显更先进的 topology”。

## 片上系统里真正的问题：高 radix 不是抽象参数

在片上，高 radix 意味着：

- 更大的 crossbar
- 更重的 allocator
- 更复杂的布线扇出
- 更难收敛的频率

也就是说，机柜级网络里“多接几根 cable”的代价，在芯片上会被翻译成 router 内部复杂度和物理布线问题。这里的代价结构完全不同。

所以高-radix 拓扑在片上最大的问题不是不可理解，而是它把“减少 hop”的收益和“单跳变重”的代价直接耦合了。

## Flattened butterfly 能借来的是什么

最值得借的不是它的全套拓扑，而是两个思路：

- 不要迷信所有 router 都必须低 radix
- 某些上层或边界节点可以有选择地更强

这在片上常被翻译成：

- 某些 gateway router 更高 radix
- memory-side aggregation node 更高带宽
- cluster 边界节点更像小型 flattened hub

也就是说，NPU 更常借它的“局部高-radix 思想”，而不是整个网络改造成 flattened butterfly。

## Dragonfly 能借来的是什么

dragonfly 的关键思路是：先组局部团，再用较少的全局高带宽连接把组与组串起来。这个思想对 chiplet 和多 cluster 系统很有启发。

在片上或跨 die 场景里，更现实的借法通常是：

- cluster / chiplet 内保持规则局部网络
- cluster / chiplet 间用更强聚合链路

这和 `chiplet + gateway + global fabric` 的思路很接近。真正有价值的地方，是它提醒你“全局带宽不必均匀地撒到每个点上”，而不是要求你真的实现经典 dragonfly 图结构。

## 为什么芯片上不常直接落地

原因通常不是理论不好，而是：

- radix 高得太快
- 物理布局不规则
- 不易和二维 tile array 对齐
- 编译器与实现复杂度上升

对 deterministic NPU 来说，这些问题尤其敏感，因为高-radix 不规则结构会让可分析性、映射规则和边界情况都变复杂。

## 最现实的使用方式：把它们当参照系

这些拓扑在 NPU 里的一个很实际价值，是作为参照系存在：

- 如果某 workload 明显被 hop 数拖死
- 如果 cluster 间带宽明显不够
- 如果 chiplet 间汇聚点过弱

那你可以用它们来测试一种假设：问题是不是值得靠“更扁平、更强上层节点”来解决。

很多时候答案不是“照搬它们”，而是“在 mesh 或 hierarchical mesh 基础上，只对少数节点局部加强”。

## 常见误解

常见误解：高-radix 拓扑在 HPC 里好，所以在芯片上也应该更好。  
实际上：HPC 和片上系统的代价结构不同；片上把高 radix 转成了更重的 crossbar、allocator 和布线问题。

常见误解：这类拓扑对 NPU 没意义。  
实际上：它们非常有意义，但常是思想意义和上界意义，不是照搬意义。

## 一句话理解

flattened butterfly 和 dragonfly 在片上最值得借的，不是完整图结构，而是“某些层级可以更扁平、某些节点可以更强”的设计思路。

## 建模启示

这类拓扑在 early-stage exploration 里很适合抽象成：

```text
TopologyClass {
  avg_hops
  max_radix
  global_links_per_group
}
```

如果你想拿它们做 chip candidate，就必须额外引入：

- `router_area_penalty(radix)`
- `placement_irregularity_penalty`
- `link_nonuniformity`

否则模型只会看到“更少 hop”，看不到“更重节点”。对 deterministic NPU，一种更实用的做法通常是：不直接建完整 dragonfly，而是在 mesh/hierarchical mesh 中引入少量 strengthened gateway node，测试收益是否足够。
