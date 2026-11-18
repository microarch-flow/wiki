# 批处理与请求调度

上级：[推理运行时](../README.md)

本专题将等待队列与资源状态转换为本轮执行计划。先解释批组成和 Prefill 分块，再讨论准入、排序、抢占与公平性。

## 阅读顺序

1. [连续批处理与分块 Prefill](04-dynamic-shape-batching.md)
2. [准入、抢占与公平性](08-scheduling.md)

## 本专题的边界

Token 预算控制工作规模，实际耗时还依赖形状和上下文。内存不足时必须有明确的等待、恢复或拒绝路径。

前置阅读：[状态与内存预算](../04-state-and-memory/runtime-state.md)和[分页 KV](../04-state-and-memory/06-paged-kv-cache.md)，了解调度器要预留和申请哪些资源。继续阅读：[采样与解码控制](../06-sampling-and-decoding/README.md)。
