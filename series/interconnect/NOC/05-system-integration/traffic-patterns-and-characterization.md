# Traffic Patterns And Characterization

上级：[05 System Integration](./README.md)

相关：[Topology Design Metrics](../03-topology/topology-design-metrics.md)、[DMA Engine NOC Interaction](./dma-engine-noc-interaction.md)、[From Workload To Traffic Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)

## 这页在回答什么问题

这页回答：系统层面应该怎样描述 NoC traffic，为什么“平均注入率”远远不够，以及 workload、mapping、DMA、memory behavior 怎样一起定义真正的流量形状。

## traffic 不是一个数字

说“这个 workload 的 NoC traffic 很大”几乎没有分析价值。至少要分开看四个维度：

- `who talks to whom`
- `when they talk`
- `how large each transfer is`
- `which endpoint / memory system behavior shapes the transfer`

同样的总字节数，在不同的时间结构和空间结构下，NoC 体验会完全不同。

## synthetic traffic 仍然必要

synthetic traffic 的价值不是代表真实 workload，而是提供可控基线。

常见几类包括：

- uniform random
- hotspot
- nearest-neighbor / local traffic
- transpose / permutation

它们适合回答：

- 某个 topology 的一般性容量特征是什么
- routing 政策在经典压力下如何表现
- 模型是否基本可信

但它们不能替代 AI workload characterization。

## AI-like traffic 的本质差异

AI 流量通常和 synthetic 最大的不同在于：

- 更强阶段性
- 更强 burstiness
- 更强 endpoint / memory-system 耦合
- 更明显的空间非均匀性

典型例子：

- prefill：大块并发搬运，memory 与 on-chip fabric 同时高压
- decode：总流量可能没那么大，但 dependency 很长，memory response 更关键
- GEMM / systolic：高度规则，很多流可以静态预测
- MoE：通信更不规则，更接近动态热点

## characterization 至少要记录什么

对一个 traffic 场景，最少应记录：

- source / destination 分布
- transfer size 分布
- 注入时间分布
- traffic class
- 是否与 memory request / response 或 local refill 强耦合

这比只记录“平均带宽多少 GB/s”有用得多。

## 为什么 burstiness 比平均值更重要

很多 AI 系统慢，不是因为长时间平均负载超了，而是因为：

- 某些阶段边界瞬时冲高
- 多个 stream 同步发起
- response 在延迟后成批返回

这会让：

- queue 瞬时冲满
- control path 被淹
- 某些 memory port 出现短时尖峰

因此 characterization 必须显式记录 burst 结构，而不只是平均速率。

## 和系统集成的关系

traffic 不只是 workload 语义产生的，还会被系统边界二次塑形：

- address map 决定流量落向哪些 port
- DMA 决定注入节奏和 outstanding 深度
- NI 决定 packetization 粒度
- local memory 决定 ejection 端能否及时消费

所以 traffic characterization 本质上是 workload 与系统集成共同生成的结果。

## 一个更有用的分类法

系统分析里，比“这是 attention traffic”更有用的分类是：

- point-to-point stream
- fan-out / broadcast-like
- fan-in / reduce-like
- memory request / response
- control / descriptor / completion

因为这些类别更直接对应：

- topology 压力点
- QoS 需求
- 是否该多网络隔离
- 是否需要 collective 支持

## 常见误区

- 认为 synthetic 流量足够代表真实工作负载
- 认为总字节量相同，网络压力就差不多
- 认为 traffic 是 workload 给定的，和地址映射或 DMA 无关

更准确的说法是：

- synthetic 只能做基线，不替代 workload trace
- 同样字节量，不同 burst 和空间结构会产生完全不同的瓶颈
- traffic 是 workload、mapping、DMA、address map、memory behavior 共同塑造的

## 一句话理解

traffic characterization 的任务不是给出“流量大不大”，而是描述流量在时间、空间、粒度和系统边界上的真实形状。

## 建模启示

模型中最好把 traffic source 抽象成可配置生成器，至少暴露：

- source-destination pattern
- packet / transfer size
- inter-arrival distribution
- traffic class
- memory-coupling mode

真正面向 workload 的阶段，应进一步从 trace 中恢复：

- phase boundary
- burst cluster
- request/response pairing
- per-class overlap

否则模型很容易在平均值上看着合理，在真实 workload 下完全失真。
