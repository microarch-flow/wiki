# AI Dataflow NoC vs CPU Coherent NoC

上级：[AI Dataflow 系统视角](./README.md)

相关：[NoC 分类框架](../01-overview/taxonomy.md)

## 读这页前先统一几个词

- `coherent NoC`：服务于缓存一致性协议的片上网络，不只是搬数据，还要维护协议语义
- `dataflow NoC`：服务于 AI 数据流执行的网络，重点是吞吐、局部复用和依赖按时满足
- `snoop`：一致性协议里的查询消息，用来问其他 cache 是否持有某地址副本
- `invalidate`：让其他 cache 把某份副本作废
- `forward progress`：系统保证合法事务最终一定能完成，而不是永远卡住

## 为什么要先划清边界

两者都叫 NoC，但设计哲学不同。  
如果直接把 CPU coherent NoC（缓存一致性片上网络）的思路照搬到 AI tile（计算单元）NoC，很容易在建模重点上跑偏。

## AI Dataflow NoC 的核心目标

- 把权重和 activation（激活值）搬到计算位置
- 支持 tile-to-tile forwarding
- 支持 producer-consumer（生产者-消费者）pipeline（流水线）
- 降低回写全局存储的次数
- 让编译器能规划更稳定的数据流

典型流量：

- HBM（高带宽存储器）-> DMA（直接内存访问）-> tile SRAM（片上静态存储）
- tile -> tile stream
- reduce（归约）/ accumulate（累加）
- control / descriptor（描述符）/ barrier（同步屏障）

## CPU Coherent NoC 的核心目标

- 支撑共享地址空间
- 处理 cache miss（缓存未命中）
- 支撑 request / response / snoop（窥探）/ invalidate（无效化）
- 保证一致性、顺序语义和 forward progress（前进保证）

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
| 访问模式 | 很多训练/GEMM 类场景更规则、可编排；但 decode、MoE 等推理流量也可能高度动态 | 更动态、更程序依赖 |
| 编译器影响 | 很大 | 相对较小 |
| VC（虚通道）作用 | traffic class 隔离、QoS（服务质量）、避免 HOL（队头阻塞） | 协议隔离、避免 coherence deadlock（一致性死锁） |
| 重点风险 | backpressure（反压）影响 tile 利用率 | 协议正确性与事务死锁 |

## 对你的主学习线意味着什么

如果目标是 `Tensix / AI tile dataflow NoC`，主线应当是：

- packet（数据包）/ flit（流控单元）
- wormhole（虫孔路由）
- credit（信用计数）/ backpressure
- router pipeline
- VC / protocol separation
- workload traffic
- architecture exploration

CPU coherent NoC 需要了解，但主要作为：

- 协议隔离的参考案例
- request / response / snoop 资源分层的参考案例
- “复杂事务网络”如何组织 VN（虚网络）/VC 的参考案例

## 本页结论

AI NoC 首先是数据搬运与数据流执行网络，不是一致性协议网络。  
把这个边界先划清，后面的建模优先级才会对。
