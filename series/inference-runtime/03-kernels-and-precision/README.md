# 算子内核与低精度执行

上级：[推理运行时](../README.md)

本专题沿实际算子路径分析计算、数据访问与启动开销。先观察一般算子，再解释 Attention 的分块归一化，最后讨论低精度执行。

## 阅读顺序

1. [一般算子与融合](operator-execution.md)
2. [Attention 内核](05-attention-kernels.md)
3. [低精度执行](10-quantization.md)

## 本专题的边界

内核负责完成给定工作；KV 管理器负责状态生命周期。数值正确性、容量收益与性能收益分别验证。

前置阅读：[Prefill 与 Decode](../01-request-and-metrics/01-prefill-decode.md)的阶段解释，以及[动态形状与数据布局](../02-model-execution/dynamic-shapes.md)中的变长批表示。继续阅读：[运行时状态与 KV 管理](../04-state-and-memory/README.md)。
