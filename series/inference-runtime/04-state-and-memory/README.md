# 运行时状态与 KV 管理

上级：[推理运行时](../README.md)

本专题回答状态存在哪里、归谁所有、何时增长以及何时可释放。先建立完整预算，再讨论固定块、前缀共享与分层迁移。

## 阅读顺序

1. [状态与内存预算](runtime-state.md)
2. [分页 KV](06-paged-kv-cache.md)
3. [前缀复用](07-radix-prefix-reuse.md)
4. [KV 分层存储](tiered-kv.md)

## 本专题的边界

共享存储不代表读取一次，命中率不等于加速比。所有收益都应回到同一容量和流量边界。

前置阅读：[Prefill 与 Decode](../01-request-and-metrics/01-prefill-decode.md)中的阶段关系和 KV 状态。上一专题：[算子内核与低精度执行](../03-kernels-and-precision/README.md)。继续阅读：[批处理与请求调度](../05-batching-and-scheduling/README.md)。
