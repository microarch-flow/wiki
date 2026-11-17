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

前置阅读：[采样与解码控制](../06-sampling-and-decoding/README.md)。继续阅读：[服务生命周期与副本管理](../08-serving-lifecycle/README.md)。
