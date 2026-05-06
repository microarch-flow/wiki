# Hierarchical NoC 深化

上级：[Topology 与 Routing](./README.md)

相关：[Topology 与物理布局](./topology-layout.md)、[Physical Realization 与 Floorplan-Aware NoC](../04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)

## 为什么 hierarchical NoC 值得单独深挖

很多 AI accelerator 的真实选择，不是“mesh 还是不是 mesh”，而是：

- 全平铺 flat mesh
- cluster 内局部互连 + cluster 间全局 NoC

这实际上是系统组织方式，而不是单个网络参数。

## Hierarchical NoC 的基本结构

一个典型分层方案可能是：

- cluster 内：crossbar / local ring / local fabric
- cluster 间：mesh / tree / global fabric

也可以进一步分成：

- tile
- cluster
- super-cluster

所以 hierarchical NoC 往往天然和架构层级一致。

## 它为什么对 AI workload 有吸引力

很多 AI workload 具备：

- 局部通信多
- 跨大范围通信少但关键
- 数据复用有明显空间层级

这意味着如果你把“高频局部流量”困在 cluster 内，通常能显著减轻全局网络压力。

## 它带来的主要好处

### 1. 降低全局 hop 与长链路使用

不是所有流量都要穿越整个芯片。

### 2. 强化局部数据复用

cluster 内更容易共享 SRAM、权重、partial sum。

### 3. 缩小全局 router 数量

相比每个 tile 一个 full router，分层设计可能更省。

### 4. 更贴近真实 floorplan

很多芯片本来就是按 cluster / tile group 组织的。

## 它的代价也很明确

### 1. 软件映射更受限

如果 workload 无法很好贴合 cluster 边界，可能出现：

- 局部互连闲置
- 跨 cluster 流量暴涨

### 2. 局部资源会形成新瓶颈

例如：

- cluster 内 crossbar
- local shared SRAM
- cluster egress port

### 3. 结构更复杂

你要同时理解：

- local traffic
- global traffic
- local/global 交界点的拥塞

## 最关键的设计问题

### Cluster 大小怎么定

太小：

- 局部复用收益不明显
- 全局流量仍然很多

太大：

- local fabric 成本上升
- cluster 内部也会变复杂

### Local SRAM 多大

这直接决定：

- 能否把热点数据留在本地
- cluster 内通信比例能否上升

### Egress / Ingress 口多少

即使 local 很强，只要 cluster 出入口太弱，跨 cluster 流量仍会成为瓶颈。

## 对不同 workload 的敏感性

### GEMM / 规则 pipeline

通常更适合 hierarchical，因为局部复用更明显。

### Prefill

取决于大块流量是否能在 cluster 内消化一部分。

### Decode

若关键 response 路径频繁跨 cluster，hierarchical 优势可能减弱。

### MoE / all-to-all

这是 hierarchical NoC 的硬仗。  
如果大部分通信都跨 cluster，层级结构的收益会下降，甚至暴露 cluster 边界瓶颈。

## 建模时至少要加入的对象

- cluster 内 local fabric
- cluster 间 global fabric
- local shared SRAM
- cluster ingress / egress 端口
- local / global traffic 分类统计

## 你至少要看的 5 个指标

- local traffic ratio
- global traffic ratio
- cluster boundary link utilization
- cluster egress stall
- end-to-end workload completion time

## 一个高价值实验

比较：

- flat mesh
- 4-tile cluster hierarchical
- 8-tile cluster hierarchical

观察：

- local/global traffic 分布
- 主干链路利用率
- cluster boundary 是否成新热点
- 哪类 workload 最受益

## 一个很实用的判断原则

hierarchical NoC 并不是“更高级的 mesh”，而是用结构分层换局部性收益。  
所以你必须先确认 workload 确实有可利用的局部性，否则分层可能只是徒增复杂度。

## 本页结论

hierarchical NoC 的真正价值，在于把架构层级、数据复用层级和物理实现层级尽量对齐。  
但它只有在 workload、mapping 和 memory organization 共同支持局部性的前提下，才会稳定优于 flat mesh。
