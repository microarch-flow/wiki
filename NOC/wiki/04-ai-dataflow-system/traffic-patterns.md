# 流量模式

上级：[AI Dataflow 系统视角](./README.md)

相关：[指标与实验设计](../05-modeling-evaluation/metrics-experiments.md)

## 为什么 traffic pattern 是核心

NoC 不会脱离 workload 自己产生价值。  
真正把某条链路压满的，不是”mesh（网格拓扑）”这个词，而是 workload（工作负载）、mapping（映射策略）、placement（放置策略）和 memory behavior 的共同结果。

## Synthetic traffic 是必要起点

至少应覆盖：

- uniform random
- hotspot
- neighbor / local traffic
- transpose / permutation

作用：

- 验证模型是否基本正确
- 暴露拓扑和 routing 的一般性行为

## AI-like traffic 才是主战场

### GEMM（通用矩阵乘法）/ weight-stationary（权重驻留）

常见特点：

- 权重或 activation（激活值）广播
- 局部复用强
- cluster 内外流量差异明显

### Attention（注意力机制）prefill（预填充阶段）

常见特点：

- 大块数据搬运
- 并行度高
- HBM（高带宽存储器）与 NoC 都可能形成压力

### Attention decode（逐token解码阶段）

常见特点：

- batch 小但访问动态
- KV cache（键值缓存）相关路径更敏感
- 系统瓶颈可能更偏 memory-centric

### MoE（混合专家模型）dispatch / gather（分发/收集）

常见特点：

- all-to-all 倾向更强
- 热点更动态
- adaptive routing（自适应路由）、QoS（服务质量）、collective（集合通信）支持价值更高

## 你最应该关注的 traffic 问题

- tile（计算单元）-to-tile forwarding（前传）是否比回写 HBM 更优
- memory placement 如何改变热点
- 哪些流量必须与 bulk data 隔离
- 哪些流量应支持 multicast（组播）/ reduce（归约）
- destination buffering（目的端缓冲）多深才不会过早触发反压

## 本页结论

traffic pattern 不是评估用的附加项，而是 NoC 建模的输入主语。  
没有 traffic，NoC 参数比较大多只剩抽象意义。
