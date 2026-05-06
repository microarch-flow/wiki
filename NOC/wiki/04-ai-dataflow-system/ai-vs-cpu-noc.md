# AI Dataflow NoC vs CPU Coherent NoC

上级：[AI Dataflow 系统视角](./README.md)

相关：[NoC 分类框架](../01-overview/taxonomy.md)

## 为什么要先划清边界

两者都叫 NoC，但设计哲学不同。  
如果直接把 CPU coherent NoC 的思路照搬到 AI tile NoC，很容易在建模重点上跑偏。

## AI Dataflow NoC 的核心目标

- 把权重和 activation 搬到计算位置
- 支持 tile-to-tile forwarding
- 支持 producer-consumer pipeline
- 降低回写全局存储的次数
- 让编译器能规划更稳定的数据流

典型流量：

- HBM -> DMA -> tile SRAM
- tile -> tile stream
- reduce / accumulate
- control / descriptor / barrier

## CPU Coherent NoC 的核心目标

- 支撑共享地址空间
- 处理 cache miss
- 支撑 request / response / snoop / invalidate
- 保证一致性、顺序语义和 forward progress

典型流量：

- load miss request
- cache line response
- snoop request
- invalidate ack
- writeback

## 两类 NoC 的主要差异

| 维度 | AI Dataflow NoC | CPU Coherent NoC |
| --- | --- | --- |
| 主流量 | tensor block、stream、DMA | cache line、snoop、response |
| 目标 | 吞吐与 pipeline 稳定性 | 一致性与低延迟事务 |
| 访问模式 | 更规则、更可预测 | 更动态、更程序依赖 |
| 编译器影响 | 很大 | 相对较小 |
| VC 作用 | traffic class 隔离、QoS、避免 HOL | 协议隔离、避免 coherence deadlock |
| 重点风险 | backpressure 影响 tile 利用率 | 协议正确性与事务死锁 |

## 对你的主学习线意味着什么

如果目标是 `Tensix / AI tile dataflow NoC`，主线应当是：

- packet / flit
- wormhole
- credit / backpressure
- router pipeline
- VC / protocol separation
- workload traffic
- architecture exploration

CPU coherent NoC 需要了解，但主要作为：

- 协议隔离的参考案例
- request / response / snoop 资源分层的参考案例
- “复杂事务网络”如何组织 VN/VC 的参考案例

## 本页结论

AI NoC 首先是数据搬运与数据流执行网络，不是一致性协议网络。  
把这个边界先划清，后面的建模优先级才会对。
