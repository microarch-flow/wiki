# 工作负载怎样形成 NoC 流量？

<span id="why-ai-noc-is-different"></span>

上级：[07 工作负载与系统案例](../SUMMARY.md#workload-cases)；原章节：[06 AI NOC Specifics](./README.md)

相关：[GEMM 通信案例](./workload-gemm-on-noc.md)、[缓存一致性通信案例](../07-workload-cases/coherent-access-and-noc.md)、[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)

<span id="这页在回答什么问题"></span>工作负载描述要完成的任务；它不会单独决定 NoC 的流量。同一任务采用不同的数据分块、存储位置和执行顺序，可能形成不同的源、目的、数据量与依赖。

<span id="它们都叫-noc但主矛盾不同"></span>分析时可以沿这条路径逐步确定条件：

> **任务与数据 → 分块和放置 → 通信及依赖 → 共享资源 → 可观察结果**

例如，矩阵乘法的输入可以先放在计算 tile 中，也可以由存储端点分发。前者可能主要产生 tile 间转发，后者还会产生从存储端点到 tile 的流量。只有路径、时机和容量确定后，才能判断哪条资源可能成为瓶颈。

## 两种任务，同一组问题

| 问题 | 分块矩阵乘法 | 一次缓存一致性访问 |
| --- | --- | --- |
| 输入与参与者 | 输入块、输出块及计算 tile。 | 请求核心、负责地址的节点及可能持有数据的缓存。 |
| 通信 | 可能有分发、转发和部分和传递；取决于映射。 | 可能有请求、查询、数据和响应；取决于协议状态。 |
| 完成条件 | 消费者拿到所需数据并完成约定计算。 | 请求达到所选协议和接口规定的完成边界。 |
| 需要检查 | 数据复用、源注入、链路及接收端能力。 | 消息依赖、有限缓冲、共享链路和端点状态。 |

<span id="cpu-coherent-noc-更怕协议复杂度"></span>一致性协议定义数据副本和权限的规则，网络承载相关消息；二者需要共同满足前进条件。请求、snoop 和 response 如何映射到队列、VC 或物理网络，由具体设计决定。[缓存一致性通信案例](../07-workload-cases/coherent-access-and-noc.md)给出一条构造路径。

<span id="ai-noc-更受-compiler-和-placement-支配"></span>在分块计算中，编译器或运行时可以提前决定部分数据放置和执行顺序。硬件是否暴露路由或时隙控制、运行时如何处理动态变化，仍取决于系统。[编译器与 NoC 协同](./compiler-noc-co-design.md)讨论这份计划的接口。

## 先确定要统计什么

<span id="ai-noc-更常面对-collective"></span>一次通信可能从一个源发给多个消费者，也可能收集多个来源的数据。相同数据的复制与不同数据的交换，不能只按目的数量归为同一种流量。[多端通信与调度](../SUMMARY.md#06-ai-noc-specifics)介绍这些通信语义。

<span id="ai-noc-的关键路径经常是-memory-路径"></span>例如一次 KV 读取可能先经过存储端点，再将响应交给计算 tile。需要区分存储服务量、注入 NoC 的字节和接收端真正可用的时间。KV 位于本地、片上共享存储还是外部存储，会改变路径。[Decode 与 KV Cache 案例](./workload-attention-decode-kv-cache.md)给出完整的统计边界。

<span id="deterministic-诉求也更强"></span>提前知道分块和依赖，有助于构造静态计划；路径固定不等于完成时间固定。要判断时间是否有界，还需要输入、竞争、下游和端点服务条件，见[确定性与静态调度](./deterministic-noc-and-static-scheduling.md)。

## 避免按芯片名称推断流量

<span id="常见误区"></span>AI 加速系统可以包含显式数据搬运，也可以包含一致性访问；CPU 系统同样可能有大块 DMA 和流式数据。一个系统还可能在不同区域同时使用多种组织方式。

例如 AMD MI300A 在同一封装中连接 CPU、GPU 和统一内存，并提供一致性架构。这说明 AI 系统也可能需要一致性；公开的封装级描述不等于给出了每条片内 NoC 路径。[AMD MI300A 数据手册](https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300a-data-sheet.pdf)

<span id="一句话理解"></span>因此先问**谁在什么时候需要什么数据**，再选择如何发送和评估；不要仅根据“AI”“CPU”或算子名称推断固定的网络行为。

## 从案例走向评估

<span id="建模启示"></span>每个案例至少要说明：输入规模与数据类型、参与者和位置、通信触发条件、数据量及完成事件。评估时再加入包格式、路径、缓冲、其他流量和服务能力，分别统计本地交付、网络注入、链路负载和任务完成时间。

可先读[GEMM 通信案例](./workload-gemm-on-noc.md)，再比较 [Prefill](./workload-attention-prefill.md)、[Decode](./workload-attention-decode-kv-cache.md) 和 [MoE](./workload-moe-routing.md)。若关注事务与协议依赖，可直接读[缓存一致性通信案例](../07-workload-cases/coherent-access-and-noc.md)。
