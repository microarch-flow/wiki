# Crossbar And Concentrated Mesh

上级：[03 Topology](./README.md)
相关：[Ring And Hierarchical Ring](./ring-and-hierarchical-ring.md), [Topology Physical Realization](./topology-physical-realization.md)

## 这页在回答什么问题

什么时候不分层的 crossbar 反而是最干净的解，什么时候应该把多个 tile 集中接到同一个 router 上，形成 concentrated mesh 或 cluster-local crossbar + global mesh。

这一页的重点不是重复“crossbar 面积 O(N^2)”，而是把 AI 芯片里最常见的 cluster 化互连思路讲清楚。

## Crossbar：局部系统里最接近“直连幻觉”的结构

crossbar 的吸引力在小系统里非常强：

- 单跳
- 任意输入到任意输出
- 没有 topology 级路由问题
- cluster 内共享 SRAM、低延迟控制流很好处理

在 4 到 8 个左右端点的局部区域，这种结构经常比小 mesh 更直接，因为你不需要为了形式统一引入多跳、buffer 和额外 routing 语义。

这和 BUS wiki 里 [Shared Bus、Bus Matrix 与 Crossbar](../../../BUS/wiki/04-microarchitecture-integration/shared-bus-bus-matrix-crossbar.md) 的判断一致：crossbar 的核心价值，是减少不相关流量之间的无谓串行化。

## Crossbar 的边界：规模一上来，代价成平方长

crossbar 的问题不在于不好用，而在于它把复杂度集中得过于彻底。端口数上升时：

- 交换矩阵变大
- 仲裁逻辑更重
- 全连接布线更难

所以 crossbar 很少是 chip-wide 主网络的合理选择。它更像局部最优工具，而不是全局骨架。

## Concentrated mesh：把多个端点集中到一个 router

concentrated mesh 的核心思路是：不是每个 tile 都挂一个 router，而是多个 tile 共享一个 router 的 local side。

这带来两个直接效果：

- 全局 router 数量减少
- 全局网络直径按 router 数量而不是按 tile 数量决定

代价则是：

- 每个 router 的 local side 更复杂
- local ingress/egress 带宽会成为共享点
- router radix 增高

所以 concentrated mesh 并不是“更便宜的 mesh”，而是“用更复杂的局部节点，换更简单的全局网络”。

## 为什么它在 NPU 上特别常见

AI accelerator 的 tile 往往本来就按 cluster 组织：

- 共用一块 local SRAM
- 局部复用强
- 编译器也倾向把强交互算子放近

这使得“若干 tile + local fabric + 一个 gateway/router”的组织非常自然。换句话说，concentrated mesh 不是凭空发明出来的网络技巧，而是 tile cluster 结构在 NoC 上的直接投影。

## Crossbar 与 concentrated mesh 的关系

在很多真实实现里，二者几乎是同一件事的两个视角：

- 从 cluster 内部看，是 local crossbar 或 local fabric
- 从全局网络看，是多个 tile 集中接到一个 router 上

所以 `cluster-local crossbar + global mesh` 往往就是 concentrated mesh 最工程化的表达。

## 它为什么比 flat mesh 更值得认真考虑

flat mesh 的优点是端到端规则统一；缺点是全网 router 太多、每个 tile 都要承担 router 成本。

concentrated mesh 则在你已经知道“局部流量远多于全局流量”时非常诱人，因为它让：

- 局部流量在 cluster 内消化
- 全局 router 只处理真正需要跨 cluster 的流量

这背后的判断非常重要：不是任何 workload 都值得 cluster 化，只有局部性交换足够强时，这种集中才是真收益。

## 它的主要风险

concentrated mesh 的风险不在全局，而在边界：

- local port 竞争
- gateway 注入/弹出带宽
- cluster 边界热点

也就是说，你把“全网很多小 router 的均匀成本”换成了“少数 gateway/router 的局部高压”。如果 cluster 大小、local SRAM 组织或 workload 映射不合适，这些点会先塌。

## 和 hierarchical mesh 的区别

hierarchical mesh 往往表示“局部也还是 mesh，只是分层了”；concentrated mesh 则更倾向“局部多个 tile 共用同一个 router 或一个很小的 local fabric”。

所以它们的核心差异是：

- hierarchical mesh 仍保留更多局部 router 结构
- concentrated mesh 更激进地把局部接入集中化

前者更像几何分层，后者更像端点压缩。

## 常见误解

常见误解：crossbar 和 concentrated mesh 是互斥选择。  
实际上：很多 concentrated mesh 的局部接入层，本来就是一个 crossbar 或 crossbar-like fabric。

常见误解：concentrated mesh 只是减少 router 数量。  
实际上：它同时改变了局部共享点、router radix、gateway 热点和 cluster 内外流量边界。

## 一句话理解

crossbar 是局部互连的单跳解，concentrated mesh 是把多个局部端点压到同一个 router 上；两者合起来，正是很多 NPU 最常见的 cluster 化互连模式。

## 建模启示

这类结构至少要分成两层建模：

```text
Cluster {
  local_endpoints[]
  local_fabric
  gateway_router
}
```

关键状态不只是全局 mesh 链路，还有：

- `local_fabric_wait`
- `gateway_injection_queue`
- `cluster_egress_utilization`

如果把 concentrated mesh 误简化成“更小的普通 mesh”，会漏掉最关键的 cluster 边界共享点。  
如果只关心全局链路利用率，也仍应保留一个 `local_access_latency` 项，否则 cluster 化收益会被系统性高估。
