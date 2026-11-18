# 分布式执行与阶段分离

上级：[推理运行时](../README.md)

本专题解释计算和状态如何分布到多个设备。由 TP、PP、DP 进入专家和上下文切分，最后处理 Prefill 与 Decode 的跨实例交接。

## 阅读顺序

1. [TP、PP 与 DP](11-cluster-parallelism.md)
2. [MoE 专家并行](moe-expert-parallelism.md)
3. [上下文并行](context-parallelism.md)
4. [PD 分离与 KV 交接](12-pd-disaggregation.md)

## 本专题的边界

先画张量与 rank 布局，再计算容量、通信和同步。集合通信与链路细节通过 Scale-up 系列继续阅读。

前置阅读：[状态与内存预算](../04-state-and-memory/runtime-state.md)和[连续批处理与分块 Prefill](../05-batching-and-scheduling/04-dynamic-shape-batching.md)。读上下文并行前，可先看[在线归一化](../03-kernels-and-precision/05-attention-kernels.md#分块与在线归一化)。

上一专题：[采样与解码控制](../06-sampling-and-decoding/README.md)。继续阅读：[服务生命周期与副本管理](../08-serving-lifecycle/README.md)。
