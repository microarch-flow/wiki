# Workload Attention Prefill

上级：[06 AI NOC Specifics](./README.md)

相关：[Traffic Patterns And Characterization](../05-system-integration/traffic-patterns-and-characterization.md)、[Memory Centric NOC](./memory-centric-noc.md)

## 这页在回答什么问题

这页回答：attention prefill 为什么更像 bulk throughput 协同问题，而不是 decode 那种 response-sensitive 问题。

## prefill 的本质

prefill 的典型特征是：

- 已知整段 prompt
- 并行度高
- 数据块大
- HBM 与 NoC 都要承载明显 bulk traffic

因此它更像在考：

- HBM 注入与 NoC 分发的匹配
- 大块流量的空间热点
- placement 和 cluster-local reuse

## 它最容易暴露的瓶颈

最常见的不是 router 微小仲裁细节，而是：

- HBM port 附近主干链路
- weight / activation 分发方式
- flat mesh 与更分层组织的差别

也就是说，prefill 更偏结构性带宽问题。

## 为什么它和 decode 必须分开

虽然都叫 attention，但 prefill 和 decode 在 NoC 上问的是不同问题：

- prefill：bulk throughput、injection、distribution、overlap
- decode：response latency、control、dependency chain

把两者混成一个“attention 流量模型”，通常会让结论失真。

## multicast 和 memory placement 在这里更值钱

如果某些 activation 或 weight 需要被多处消费，那么：

- multicast 的收益会更容易体现
- HBM port 的分布和 address interleaving 会很关键

因为这类大块流一旦用普通重复单播，很快会把靠近 source 的路径打热。

## 一句话理解

prefill 更像“大规模 bulk movement 怎么和 memory system 协同”，而不是“小响应能不能及时回来”。

## 建模启示

prefill trace 至少要显式包含：

- 大块 burst
- source-side concentration
- HBM port placement
- phase overlap

评估时优先看：

- main-trunk utilization
- injection hotspot
- overlap 成功率
- workload completion time

这比单看平均 packet latency 更贴近 prefill 的真实问题。
