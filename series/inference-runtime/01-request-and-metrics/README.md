# 请求路径与服务指标

上级：[推理运行时](../README.md)

先建立请求的全局路径，再区分执行阶段、用户指标和朴素实现的限制。输入是一组请求与服务规则；这一章的输出是后续分析共用的状态和计时边界。

## 阅读顺序

1. [完整请求路径](request-path.md)
2. [Prefill 与 Decode](01-prefill-decode.md)
3. [延迟、吞吐与 SLO](02-metrics-slo.md)
4. [朴素引擎的瓶颈](03-naive-bottlenecks.md)

## 本专题的边界

读完应能说明：首 token 在哪里产生，哪些时间包含排队，为什么容量、带宽和尾延迟不能互相替代。

继续阅读：[模型加载与执行计划](../02-model-execution/README.md)。
