# Attention Prefill 案例：分块和掩码怎样改变通信？

<span id="workload-attention-prefill"></span>

上级：[07 工作负载与系统案例](../SUMMARY.md#workload-cases)；原章节：[06 AI NOC Specifics](./README.md)

相关：[Decode 与 KV Cache 案例](./workload-attention-decode-kv-cache.md)、[GEMM 通信案例](./workload-gemm-on-noc.md)、[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)

<span id="这页在回答什么问题"></span><span id="prefill-的本质"></span>Prefill 处理输入序列并生成后续计算需要的状态。一个阶段可以并行处理多个 token，但具体通信仍由注意力掩码、分块方式、数据位置和执行计划决定。

<span id="为什么它和-decode-必须分开"></span>Prefill 与逐 token decode 使用相同的注意力基础，却不一定形成相同的流量：前者可以处理多个已知输入位置；后者通常要在每一步访问历史 KV 并受生成依赖约束。两者都可能受算力、存储带宽、片上网络或同步等待限制，不能只按阶段名称指定瓶颈。

## 同一个分块，两种掩码

<span id="一个分块通信例子"></span>构造例：batch=1，输入有 4 个 token，1 个 head，head dimension=4，Q/K/V 均为 FP16，即每元素 2 B。每个完整的 Q、K 或 V 张量是 4×4×2 = **32 B**。

两个相邻 tile 分别负责 token 0–1 和 token 2–3 的 Q，且各自已经持有同一组 token 的 K 和 V。每个 tile 的 K 块为 2×4×2 = **16 B**，V 块也是 16 B。只统计 tile 间 K/V payload；不计先前生成、加载、包头、填充和其他流量。

| 注意力范围 | 需要的远端 K/V | 两个方向合计 |
| --- | --- | ---: |
| 双向：每个 Q 都需要全部 token | 两个 tile 各接收对方 16 B K 和 16 B V。 | 64 B |
| 因果：每个 Q 只看自己和此前 token | 后两个 token 的 tile 接收前两个 token 的 K/V；前者不需后者的 K/V。 | 32 B |

因果行假设整块 K/V 只发送一次，且本地数据无需入网。它不是所有自回归实现的固定流量：分块、窗口大小、缓存和数据放置改变时，交付量与路径也会变化。原始 Transformer 的 decoder 使用掩码阻止位置访问后续位置。[Attention Is All You Need](https://arxiv.org/html/1706.03762v7)

## 数据什么时候可用

一个 Q 块可以在所需 K 块到达后计算对应 score；所需 V 可按实现提前预取或随后送达。若实现支持逐块累积，部分结果可以在其他块仍在传输时推进。是否需要等待完整结果、是否存在 barrier，应由算法和实现的依赖定义。

FlashAttention 用分块和在线归约减少 GPU HBM 与片上 SRAM 间的读写，并避免将完整注意力矩阵物化到 HBM。它提供了数据移动随算法改变的例子；论文的具体 GPU 内存层次和测量不等于任意 NoC 的流量。[FlashAttention 原论文](https://proceedings.neurips.cc/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html)

## 比较哪些资源

<span id="它最容易暴露的瓶颈"></span><span id="multicast-和-memory-placement-在这里更值钱"></span>如果多个消费者需要同一块权重或 activation，共享分发路径可能减少重复传输；若数据已在消费者本地，收益可能不同。存储端口、NoC 注入、共享链路和接收缓冲都可能成为瓶颈，需要比较实际需求与可用服务，而不是假定 HBM 或某条主干必然饱和。

<span id="建模启示"></span>实验应固定 prompt 长度、batch、head 布局、掩码、数据类型、映射及初始位置；记录本地交付、网络注入、每条链路的 byte-hop、端点等待与任务完成时间。再分别改变分块或放置，观察是否改变关键路径。第八章的[逐拍小 trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md#可手算的-prefill-小-trace)采用双方交换 K/V 的假设，详细说明包头与逐拍时序。

<span id="一句话理解"></span>Prefill 的并行机会来自已知输入；网络要搬多少数据，仍由实际可见范围、放置和执行方式共同决定。
