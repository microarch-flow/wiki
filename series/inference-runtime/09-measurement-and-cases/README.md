# 测量、建模与框架案例

上级：[推理运行时](../README.md)

本专题把机制解释变成可核对的证据。先设计压测与观测，再建立事件模型，最后阅读固定版本源码并完成条件估算。

## 阅读顺序

1. [压测与性能定位](benchmarking-and-profiling.md)
2. [Trace 与事件模型](trace-and-event-model.md)
3. [框架源码剖析](14-framework-comparison.md)
4. [容量与性能估算](15-quantitative-estimation.md)

## 本专题的边界

公式复算、模型验证和硬件实测各自解决不同问题。没有执行目标硬件实验时，不给出性能排名或 SLO 通过结论。

前置阅读：[延迟、吞吐与 SLO](../01-request-and-metrics/02-metrics-slo.md)。事件模型接续[连续批处理与分块 Prefill 的 A、B 算例](../05-batching-and-scheduling/04-dynamic-shape-batching.md#一个两请求执行例子)。

上一专题：[服务生命周期与副本管理](../08-serving-lifecycle/README.md)。
