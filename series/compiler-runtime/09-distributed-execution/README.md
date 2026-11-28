# 分布式执行与通信编排

一个设备无法容纳模型或满足需求时，可以将计算、数据与状态分布到多个设备。切分方式决定需要交换什么数据，以及哪些任务必须等待通信结束。

## 贯穿算例与阅读边界

从两张卡分摊同一个小矩阵乘法入手，继续改变模型层划分与副本数。专家、上下文和 Prefill/Decode 分离分别引入各自的最小算例。

I01 复用 C01/D05 的 2×4 与 4×2 矩阵，建立 Rank、通信组、复制/分片/部分和布局以及通信依赖的基础。I02、I03、I04 可各自衔接 I01；I05 按需参考 I01/I02，并继承 G/H 的状态管理与调度知识。不重复物理协议、路由和链路实现。

## 知识关系

<figure class="micro-v2-map" markdown="1">

[![I01 → I02；I01 → I03；I01 → I04；I01 → I05（关联）；I02 → I05（关联）](assets/knowledge-map.svg)](assets/knowledge-map.svg)

<figcaption>图中实线表示本专题内的主要前置关系，虚线表示按场景参考；跨专题先修知识见下表。 点击可查看大图。</figcaption>
</figure>


## 阅读顺序 {#计划阅读顺序}

本专题五篇正文的初稿已全部完成。先读 I01，建立分布式数据布局与通信依赖的共同认知；再按工作负载和执行问题选择后续文章。

| 编号 | 文章 | 读完应理解什么 | 主要前置知识 | 状态 |
| --- | --- | --- | --- | --- |
| I01 | [同一次矩阵乘法分给两张卡，哪些数据必须交换？](i01-tensor-parallelism.md) | Rank、通信组、TP、行列切分、部分和、集合通信接口及通信量。 | A03、A04、F02、矩阵乘法 | 已发布 |
| I02 | [模型太大需要多张卡，还是请求太多需要多个副本？](i02-pipeline-and-data-parallelism.md) | PP、DP、流水线并行、微批、气泡、混合 Rank 布局、容量与吞吐。 | I01 的布局/通信基础、G01 | 已发布 |
| I03 | [每个 Token 选择不同专家，怎样将计算送到相应设备？](i03-expert-parallelism.md) | EP、MoE Dispatch/Combine、路由矩阵、通信量、容量限制与负载失衡。 | I01、MoE 基础 | 已发布 |
| I04 | [上下文太长，怎样将历史状态分给多张卡？](i04-context-parallelism.md) | CP、KV 头切分与位置切分、Prefill/Decode 上下文并行、Attention 局部计算与归并。 | I01、G04、Attention 基础；按需 D07 | 已发布 |
| I05 | [Prefill 和 Decode 分开执行时，KV 怎样完成交接？](i05-prefill-decode-disaggregation.md) | PD 分离、状态交接、数据布局、传输量、两池队列、背压及关键路径。 | G02、G05、H01/H03、F02；按需 I01/I02 | 已发布 |

## 从哪里来，接下来往哪读

主要衔接：[软件执行共同基础](../01-foundations/README.md)、[通用执行运行时](../06-execution-runtime/README.md)、[模型执行与生成控制](../07-model-execution/README.md)。

硬件机制参考[计算微架构](../../microarchitecture-v2/README.md)、[存储系统](../../storage/README.md)和[芯片与系统互连](../../interconnect/README.md)。

模型计算原理参考[算法与模型](../../workload/README.md)。重构期间也可查阅[旧版推理运行时](../../inference-runtime/README.md)。

后续方向：[推理服务系统](../10-serving/README.md)、[性能分析、建模与验证](../11-performance/README.md)。

更多阅读路线见[编译器与运行时系统系列首页](../README.md)。
