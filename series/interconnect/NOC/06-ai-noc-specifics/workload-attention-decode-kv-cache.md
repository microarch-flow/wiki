# Attention Decode 与 KV Cache：数据怎样支持下一步生成？

<span id="workload-attention-decode-kv-cache"></span>

上级：[07 工作负载与系统案例](../SUMMARY.md#workload-cases)；原章节：[06 AI NOC Specifics](./README.md)

相关：[Attention Prefill 案例](./workload-attention-prefill.md)、[NoC 与存储系统](../05-system-integration/noc-meets-memory-system.md)、[端到端服务保证](../04-routing-and-flow-control/service-guarantees-and-latency-bounds.md)

<span id="这页在回答什么问题"></span><span id="decode-同时受流量和依赖链约束"></span>常见的自回归 decode 中，每条序列逐步生成输出。下一步需要使用前一步的结果；每步的计算还可能依赖历史 KV、权重和其他状态。批处理、投机解码及调度可以改变一次执行处理的 token 数。

## 从请求到可用数据

<span id="kv-cache-让它天然-memory-centric"></span>一种映射把历史 KV 放在存储端点，计算 tile 读取所需数据：

> 读取请求 → 存储服务 → 数据返回 → 接收端交付 → 依赖计算

真实系统可能把 KV 放在本地 SRAM、片上共享存储或外部内存；也可能分块读取、预取并和计算重叠。先确定请求和数据是否经过所研究的 NoC，再统计各段资源占用。新 token 的 K/V 还需要写入或追加到指定位置；写入何时对后续步骤可见由接口与调度契约决定。

## KV 逻辑读取量

<span id="kv-带宽和依赖延迟都可能主导"></span>假设每层有相同数量的 KV head、相同 head dimension 和 K/V 元素字节数。每条序列每层都需要其指定的全部历史 K/V，且每个所需 KV 元素恰好逻辑读取一次；暂不计新 token、跨请求共享、压缩、元数据或额外重读。令：

- L：层数；H<sub>KV</sub>：KV head 数；D：每个 head 的维度；P：每元素字节数。
- S<sub>i</sub>：本步骤第 i 条序列需要读取的历史 token 数。

则所有活跃序列在一个步骤中的 KV 逻辑读取量为：

> V<sub>KV</sub> = 2 × L × H<sub>KV</sub> × D × P × Σ S<sub>i</sub>。

前面的 2 对应 K 和 V。窗口或稀疏注意力只读取部分历史时，S<sub>i</sub> 应按实际需要定义；各层配置不同时，要分别逐层求和。

例：batch=1、L=32、S=4096、H<sub>KV</sub>=8、D=128、FP16 的 P=2 B，则：

> V<sub>KV</sub> = 2 × 32 × 4096 × 8 × 128 × 2 = **536,870,912 B，即 512 MiB/step**。

这是逻辑量，不是实测 HBM 或 NoC 字节。缓存命中、同一 KV 被多个计算分片重复取用、对齐、包头和物理位置都会改变相应边界的计数。GQA 中多个 query head 可以共享 KV head，因此公式按实际 KV head 数计；物理读取能否共享仍取决于实现。[GQA 原论文](https://arxiv.org/abs/2305.13245)

## 哪些等待会进入关键路径

<span id="placement-在这里特别值钱"></span>数据位置影响路径和端口负载，但“更近”不自动等于更快：实际结果还取决于端口能力、共享流量、缓存命中和下游接收。权重和 KV 的持续服务率可能限制完成时间；短消息、同步或最后一块关键数据也可能在特定负载下成为关键路径。

比较两个 placement 时，固定序列长度、batch、请求窗口、端点能力及竞争流量。分别观察存储服务、NoC 注入与链路等待、接收端等待和依赖计算；QoS 或不同路径是否改善最终时间，应以同一工作负载和资源预算验证。

<span id="它和-prefill-的最关键区别"></span>Prefill 具有多个已知输入位置，decode 有逐步生成依赖；但 prefill 不必然算力受限，decode 也不必然只受单次响应延迟限制。[Prefill 案例](./workload-attention-prefill.md)展示分块和掩码如何改变通信。

## 时间与流量的边界

<span id="建模启示"></span>模型可记录每条序列需要的历史范围、KV 位置、读取和追加事件、数据到达、消费者接收及下一步依赖。完成时间要注明是某个 flow、一个计算步骤，还是整个服务请求。

<span id="一句话理解"></span>用户看到的首 token 时间、相邻输出间隔和吞吐不是同一指标，也未必等于一次 NoC 传输时间。vLLM 的 benchmark 文档分别定义了客户端 TTFT、ITL 和 TPOT；在不同系统中应重新检查起止事件。[vLLM 延迟指标](https://docs.vllm.ai/en/v0.33.0/benchmarking/cli/)

PagedAttention 将 KV 组织成可映射的块，支持灵活分配和共享；这种管理方式影响位置和访问方式，但不会单独保证某个固定的 HBM 或 NoC 流量比例。[PagedAttention 原论文](https://arxiv.org/abs/2309.06180)
