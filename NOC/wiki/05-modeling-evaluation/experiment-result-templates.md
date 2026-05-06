# 实验模板与结果模板

上级：[建模与评估](./README.md)

相关：[指标与实验设计](./metrics-experiments.md)、[架构探索方法](./architecture-exploration.md)

## 为什么需要模板

没有统一模板，NoC 实验很容易变成：

- 参数记不全
- 流量条件不一致
- 结果难横向比较
- 结论边界说不清

模板的目的不是形式化，而是让每次实验都能留下可复用的判断材料。

## 实验记录模板

建议每次实验至少固定下面 6 部分。

### 1. 实验目的

示例：

- 比较 flat mesh 和 hierarchical NoC 在 GEMM-like traffic 下的差异
- 评估 response priority 是否改善 decode tail latency

### 2. 输入配置

至少记录：

- topology
- routing
- VC / traffic class 设置
- link width / bandwidth
- buffer depth
- packet size / flit size
- endpoint / ejection 限制
- memory port placement

### 3. Workload / Traffic 描述

至少记录：

- synthetic 还是 workload trace
- traffic class 构成
- source / destination 分布
- tile placement
- 是否有 forwarding / multicast / reduce

### 4. 输出指标

至少记录：

- packet latency
- tail latency
- per-link utilization
- stall breakdown
- tile utilization
- workload completion time

### 5. 根因分析

至少回答：

- 最先饱和的是哪里
- 主要 stall 是哪一类
- 根因在 NoC、endpoint、memory 还是 mapping

### 6. 结论边界

至少说明：

- 结论适用于哪些 traffic
- 哪些假设会显著改变结论
- 当前模型还没覆盖哪些因素

## 一个推荐的实验记录格式

```md
# Experiment: <name>

## Goal

## Configuration

## Workload / Traffic

## Key Metrics

## Stall Breakdown

## Bottleneck Analysis

## Conclusion

## Validity Boundary
```

## 结果汇总模板

当你开始扫参数时，建议用统一矩阵汇总：

| Experiment | Topology | Traffic | Key change | Main bottleneck | Best metric change | Residual risk |
| --- | --- | --- | --- | --- | --- | --- |

这样你很容易看出：

- 哪类优化最稳定
- 哪类 workload 对 NoC 最敏感
- 哪类结论只是局部有效

## 对 stall breakdown 的记录建议

不要只写“拥塞增加了”，建议至少记录：

- `NO_CREDIT`
- `SWITCH_CONFLICT`
- `LINK_BUSY`
- `EJECTION_BLOCKED`
- `INJECTION_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`

最好同时提供：

- 总周期占比
- 最常出现的位置
- 最常出现的 traffic class

## 对图表的最低要求

如果后续要做汇报，最值得保留的图一般是：

- per-link utilization heatmap
- latency CDF 或 tail latency 对比
- stall breakdown bar chart
- workload completion time 对比

## 一个简单但很重要的原则

每次实验最好只改 1 到 2 个主参数。  
否则你很难判断改进到底来自 topology、QoS 还是 memory placement。

## 本页结论

实验模板的价值，不在于“把结果写整齐”，而在于把每次 NoC 对比都变成可追溯、可复用、可横向判断的证据。
