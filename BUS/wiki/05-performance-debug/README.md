# 05 性能与调试

这一部分面向工程判断：如何衡量 BUS、定位争用、解释 stall。

## 本章入口

1. [带宽、延迟、利用率与拥塞](./bandwidth-latency-utilization.md)
2. [争用、QoS 与可观测性](./contention-qos-observability.md)
3. [Timeout、Fault 与 Hang 定位框架](./timeout-fault-hang-debug-framework.md)
4. [Counters、Trace 与观测点设计](./counters-trace-observation-points.md)
5. [AXI Waveform Debug 方法](./axi-waveform-debug-method.md)

## 一句话总纲

BUS 性能分析最忌讳只看一个平均带宽数字，真正要看的是 `利用率、排队、回压、长尾延迟、观测点`。
