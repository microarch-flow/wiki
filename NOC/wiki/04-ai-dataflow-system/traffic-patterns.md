# 流量模式

上级：[AI Dataflow 系统视角](./README.md)

相关：[指标与实验设计](../05-modeling-evaluation/metrics-experiments.md)

## 为什么 traffic pattern 是核心

NoC 不会脱离 workload 自己产生价值。  
真正把某条链路压满的，不是“mesh”这个词，而是 workload、mapping、placement 和 memory behavior 的共同结果。

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

### GEMM / weight-stationary

常见特点：

- 权重或 activation 广播
- 局部复用强
- cluster 内外流量差异明显

### Attention prefill

常见特点：

- 大块数据搬运
- 并行度高
- HBM 与 NoC 都可能形成压力

### Attention decode

常见特点：

- batch 小但访问动态
- KV cache 相关路径更敏感
- 系统瓶颈可能更偏 memory-centric

### MoE dispatch / gather

常见特点：

- all-to-all 倾向更强
- 热点更动态
- adaptive routing、QoS、collective 支持价值更高

## 你最应该关注的 traffic 问题

- tile-to-tile forwarding 是否比回写 HBM 更优
- memory placement 如何改变热点
- 哪些流量必须与 bulk data 隔离
- 哪些流量应支持 multicast / reduce
- destination buffering 多深才不会过早触发反压

## 本页结论

traffic pattern 不是评估用的附加项，而是 NoC 建模的输入主语。  
没有 traffic，NoC 参数比较大多只剩抽象意义。
