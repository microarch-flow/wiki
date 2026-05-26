# Workload GEMM On NOC

上级：[06 AI NOC Specifics](./README.md)

相关：[Broadcast Multicast Tree](./broadcast-multicast-tree.md)、[Reduction And Collective Networks](./reduction-and-collective-networks.md), [Tile Architecture And NOC](./tile-architecture-and-noc.md)

## 这页在回答什么问题

这页回答：GEMM 为什么适合作为 AI NoC 的第一批 workload 基线，以及它主要在逼问网络哪三类能力。

## GEMM 为什么重要

GEMM 的价值不只是常见，而是它能把三类典型流量一次串起来：

- broadcast / fan-out
- tile-to-tile forwarding
- gather / reduce

而且这些模式通常比较规则，适合做第一批 architecture exploration baseline。

## 它最常问的三件事

### 1. 权重和激活怎么分发

如果权重或激活需要扇出到多个 tile，那么就会逼问：

- software replication 够不够
- multicast 是否有价值
- source 侧热点是否严重

### 2. 中间结果要不要直接 forward

如果每个阶段都回写再读出，会明显增加：

- NoC 总流量
- local SRAM 压力
- HBM 往返压力

因此 GEMM 常常是最能体现 tile-to-tile forwarding 价值的 workload。

### 3. partial sum 怎么收

一旦出现 many-to-one gather 或 reduce，就会逼问：

- sink 端是否太集中
- ejection / local accumulation 是否扛得住
- tree / hierarchical reduce 是否值得

## GEMM 更常偏向 deterministic 设计

因为：

- 数据分块规则
- 邻接关系相对稳定
- hotspot 更容易提前分析

所以 GEMM 很适合：

- source routing
- static scheduling
- cluster-local reuse

这也是它成为 deterministic NPU 早期主力基线的原因。

## 它通常不是最难的动态案例

相比 MoE 或 decode，GEMM 往往没有那么动态。它更像是在问：

- 网络能否稳定支撑规则大流
- collective 支持是否值回票价
- tile / SRAM / forwarding 的系统边界是否合理

而不是在问极端不规则的实时适应能力。

## 一句话理解

GEMM 是 AI NoC 的基础体检项，因为它用规则的方式同时考 broadcast、forwarding 和 reduce。

## 建模启示

GEMM 模型至少要显式扫这些变量：

- tile block size
- local SRAM capacity
- forwarding on/off
- multicast on/off
- flat gather vs hierarchical reduce

如果模型只把 GEMM 当成“均匀 point-to-point 流量”，会错过它真正有价值的结构信息。
