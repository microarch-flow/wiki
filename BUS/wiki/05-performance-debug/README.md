# 05 性能与调试

这一章面向工程判断：如何衡量 BUS、定位争用、解释 stall，并把波形、counter、trace 和软件症状收敛成可复盘结论。

## 本章入口

1. [带宽、延迟、利用率与拥塞](./bandwidth-latency-utilization.md)
2. [争用、QoS 与可观测性](./contention-qos-observability.md)
3. [Timeout、Fault 与 Hang 定位框架](./timeout-fault-hang-debug-framework.md)
4. [Counters、Trace 与观测点设计](./counters-trace-observation-points.md)
5. [AXI Waveform Debug 方法](./axi-waveform-debug-method.md)

## 本章主线

BUS 性能分析最忌讳只看一个平均带宽数字。真正要看的是：请求在哪里排队，哪个共享点在仲裁，回压如何传播，response 是否释放 slot，completion 何时对软件可见，错误是 timeout、fault 还是 hang。

| 主题 | 关键问题 |
| --- | --- |
| 带宽、延迟、利用率 | 如何避免把总带宽当成体验结论 |
| 争用与 QoS | 如何找出哪类流量在哪个共享点等待 |
| timeout / fault / hang | 如何先分类，再决定调试入口 |
| counters / trace | 如何设计能复盘的观测点 |
| AXI waveform | 如何把信号变化转成 transaction 状态 |

## 阅读顺序

建议先读指标框架，再读争用和 QoS；出现系统卡住时读 timeout/fault/hang；设计观测能力时读 counters/trace；已经打开波形后再读 AXI waveform debug。这样可以避免从波形细节直接跳到错误结论。

## 建模启示

第 05 章给模型提供可观测性和调试状态。性能模型需要记录 bandwidth、latency histogram、queue occupancy、arbiter wait、QoS class、outstanding age、response wait、completion latency 和 timeout threshold。功能模型需要记录 fault source、error mapping、resource release、interrupt/clear、last forward progress 和 transaction ledger。

调试模型的目标不是复刻所有信号，而是复刻可解释事件：`request_accept`、`arbiter_grant`、`queue_full`、`backpressure_assert`、`response_release`、`timeout_fire`、`fault_recorded`、`completion_visible`、`id_slot_release`。这些事件让性能问题、错误路径和波形现象进入同一套分析语言。
