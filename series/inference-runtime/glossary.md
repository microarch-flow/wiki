# 推理运行时术语表

<div class="inference-legacy-anchors" aria-hidden="true"><span id="术语表-glossary"></span></div>

这里维护跨专题的简明定义。具体公式、实现条件与例子以对应文章为准；性能相关术语都需要明确统计或资源边界。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="ac"></span></div>

## 请求、阶段与指标

| 术语 | 定义 |
|---|---|
| <a id="autoregressive"></a>自回归（autoregressive） | 按已有输入和输出历史生成后续内容；单序列存在生成依赖，不同请求仍可并行。 |
| <a id="prefill"></a>预填充（Prefill） | 处理未复用的输入位置并建立状态，可整段或分块执行；性能限制取决于形状与实现。 |
| <a id="decode"></a>解码（Decode） | 使用历史状态继续生成；普通单步通常每条被选择的序列处理一个新位置。 |
| <a id="ttft"></a>首 token 时延（TTFT） | 从规定的请求起点到首个有效输出的时间，包含哪些阶段须明确。 |
| <a id="itl"></a>token 间时延（ITL） | 同一请求相邻输出 token 的时间间隔；只有 chunk 时间时不能还原真实逐 token 间隔。 |
| <a id="tpot"></a>每输出 token 时间（TPOT） | 本文指首 token 之后的平均间隔，输出多于一个 token 时为 (E2E−TTFT)/(N−1)。 |
| <a id="e2e"></a>端到端时延（E2E） | 从请求起点到规定终点的时间；最后 token 与协议结束可以是不同终点。 |
| <a id="throughput"></a>吞吐（throughput） | 单位时间的完成请求数或 token 数，必须明确计数对象与窗口。 |
| <a id="goodput"></a>有效吞吐（goodput） | 只计入满足预先定义成功与服务条件的请求或其 token；两种单位不能混同。 |
| <a id="mbu"></a>模型带宽利用率（MBU） | 逻辑字节模型除以时间和峰值带宽的比率；须与硬件计数器测得的带宽区分。 |
| <a id="mfu"></a>模型算力利用率（MFU） | 估算的模型 FLOP 除以时间和指定精度峰值；不等同于硬件忙碌比例。 |
| <a id="open-loop"></a>开环压测（open-loop） | 按预定到达过程发送请求，不以之前请求完成作为下一次发送的必要条件。 |
| <a id="closed-loop"></a>闭环压测（closed-loop） | 按固定并发或反馈规则补充请求；服务变慢时到达速率可能自动降低。 |

<div class="inference-legacy-anchors" aria-hidden="true"><span id="dk"></span></div>

## 执行、形状与内核

| 术语 | 定义 |
|---|---|
| <a id="compute-bound"></a>计算受限（compute-bound） | 指定工作和观察边界下，计算资源是实际主要限制；Roofline 只能提供资源界限。 |
| <a id="memory-bound"></a>访存受限（memory-bound） | 指定层级的数据访问是主要限制；需说明带宽、访问延迟或其他具体约束。 |
| <a id="arithmetic-intensity"></a>算术强度（arithmetic intensity） | 同一边界的工作量除以数据量，单位 FLOP/byte。 |
| <a id="roofline"></a>Roofline | 以计算与带宽资源上界约束可达性能的模型，不能独自证明实际瓶颈。 |
| <a id="hbm"></a>高带宽内存（HBM） | 高带宽堆叠 DRAM；与计算芯片上的 SRAM、缓存层级分别计数。 |
| <a id="gqa"></a>分组查询注意力（GQA） | 多个查询头共享一组 KV 头；容量需按 KV 头数计算。 |
| <a id="mqa"></a>多查询注意力（MQA） | 多个查询头共享一组 K/V 的注意力结构。 |
| <a id="flash-attention"></a>FlashAttention | 通过分块和在线 softmax 减少完整注意力中间矩阵的 HBM 物化。 |
| <a id="flash-decoding"></a>Flash-Decoding／split-KV | 沿 KV 范围划分部分计算后归约，以增加某些 Decode 形状的并行度。 |
| <a id="online-softmax"></a>在线 softmax（online softmax） | 维护最大值、指数和及加权和，通过重标度合并分块结果。 |
| <a id="ragged-layout"></a>变长打包布局（ragged／packed） | 连接有效 token 并保存序列边界；必须防止不同请求之间错误注意。 |
| <a id="padding"></a>填充（padding） | 补齐形状以匹配矩形张量、内核或执行桶，可能增加工作也可能提高计划复用。 |
| <a id="cu-seqlens"></a>cu_seqlens | 累积序列长度数组，为变长内核提供请求边界。 |
| <a id="execution-provider"></a>执行提供者（Execution Provider） | ONNX Runtime 中声明并实现节点或子图执行能力的后端接口。 |
| <a id="cuda-graph"></a>CUDA Graph | 表示设备操作及依赖的执行图，可减少重复提交开销；捕获与重放存在条件。 |

## 状态、缓存与内存

| 术语 | 定义 |
|---|---|
| <a id="kv-cache"></a>KV 缓存（KV cache） | 保存已计算位置的 K/V，减少历史位置重算；新查询仍需计算注意力。 |
| <a id="internal-fragmentation"></a>内部碎片（internal fragmentation） | 已分配单元中未装入有效载荷的空间，需与预留策略和块尾部口径对应。 |
| <a id="external-fragmentation"></a>外部碎片（external fragmentation） | 空闲空间被分割，导致总量足够却无法满足所需连续分配。 |
| <a id="paged-attention"></a>分页注意力（PagedAttention） | 用软件块与映射管理 KV，并由匹配内核读取；不代表所有显存浪费均被消除。 |
| <a id="block-table"></a>块表（block table） | 将请求逻辑块映射到缓存池块；是否跨层共享取决于缓存组与布局。 |
| <a id="cow"></a>写时复制（CoW） | 共享状态需要私有写入时先创建副本，避免改变其他使用者可见的内容。 |
| <a id="radix-attention"></a>RadixAttention | 用压缩前缀树组织可复用 KV 的一种设计，并配套引用与淘汰管理。 |
| <a id="prompt-caching"></a>提示缓存（prompt caching） | 服务接口中的输入复用能力；实际保存内容、保留期和计费由具体服务定义。 |
| <a id="apc"></a>自动前缀缓存（APC） | 按输入前缀及必要身份信息自动查找并复用已缓存状态。 |
| <a id="cache-identity"></a>缓存身份（cache identity） | 影响缓存状态语义的模型、输入、位置、适配器及隔离等条件。 |
| <a id="tiered-kv"></a>分层 KV／KV offload | 在设备内存、主机内存或其他介质间保存和恢复 KV，需显式处理一致性与完成。 |
| <a id="kv-transfer"></a>KV 传输（KV transfer） | 将指定位置与布局的状态送至接收方；传输完成和可执行就绪需分别定义。 |

## 批处理、调度与服务

| 术语 | 定义 |
|---|---|
| <a id="static-batching"></a>静态批处理（static batching） | 在一组执行中保持固定批成员的方式；适用性取决于请求与执行模式。 |
| <a id="continuous-batching"></a>连续批处理（continuous batching） | 在迭代边界调整批成员，减少完成后空槽位等待；不保证无排队。 |
| <a id="iteration-level-scheduling"></a>迭代级调度 | 以一次模型迭代为选择粒度，重新决定可运行请求及工作范围。 |
| <a id="chunked-prefill"></a>分块 Prefill | 将输入位置分多轮计算，后续块仍读取语义要求的历史状态。 |
| <a id="selective-batching"></a>选择性批处理（selective batching） | 按算子特性决定哪些工作合批；Orca 用它组织线性层和注意力。 |
| <a id="stall-free-scheduling"></a>无停顿调度（stall-free scheduling） | Sarathi-Serve 对其分块 Prefill 与 Decode 组织方式的命名，不是通用硬实时保证。 |
| <a id="head-of-line-blocking"></a>队头阻塞 | 前部任务或资源条件阻止后续可执行任务得到服务。 |
| <a id="admission-watermark"></a>准入水位 | 为增长或突发需求保留资源的策略参数，不存在统一默认最优比例。 |
| <a id="preemption"></a>抢占（preemption） | 暂停请求以让出执行或状态资源；恢复可采用保留、重算或迁移等实现。 |
| <a id="thrashing"></a>抖动（thrashing） | 频繁暂停和恢复消耗大量资源，却很少完成有用输出的状态。 |
| <a id="backpressure"></a>背压（backpressure） | 下游压力向上游传播，限制继续接收或生成工作。 |
| <a id="request-lifecycle"></a>请求生命周期 | 从接收到完成或失败的状态变化，以及与在途工作和资源回收的关联。 |

<div class="inference-legacy-anchors" aria-hidden="true"><span id="sz"></span></div>

## 采样、约束与低精度

| 术语 | 定义 |
|---|---|
| <a id="logits"></a>logits | 模型对候选 token 给出的未归一化分数，后续处理共同定义最终分布。 |
| <a id="speculative-decoding"></a>推测解码（speculative decoding） | 先提出多个候选再验证的生成方法；结果保证由具体接受算法决定。 |
| <a id="acceptance-rate"></a>接受率（acceptance rate） | 按指定位置与统计口径，候选被接受的比例或条件概率；不单独决定加速比。 |
| <a id="rejection-sampling"></a>拒绝采样 | 通过接受概率与拒绝后的残差采样保持目标分布，前提是分布和实现步骤一致。 |
| <a id="tree-attention"></a>树注意力（tree attention） | 用路径相关掩码并行计算候选树，禁止候选读取不属于自身路径的状态。 |
| <a id="constrained-decoding"></a>约束解码 | 限制合法续写集合并推进解析状态；合法前缀不等于完整或语义正确输出。 |
| <a id="token-mask"></a>token 掩码 | 标记当前允许候选的词表掩码，其计算成本依语法、分词和状态实现而定。 |
| <a id="fsm"></a>有限状态机（FSM） | 具有有限状态与转移的计算模型；一般递归 CFG 不能直接等同于有限状态机。 |
| <a id="weight-only-quant"></a>权重量化（weight-only） | 主要压缩权重表示，实际计算格式与解量化路径由匹配内核决定。 |
| <a id="w8a8"></a>W8A8 | 权重与激活均使用约 8 bit 表示的一类配置；具体编码与累加精度另行定义。 |
| <a id="awq"></a>AWQ | 利用激活信息优化权重量化误差的方法，质量与性能仍需按模型和任务验证。 |
| <a id="gptq"></a>GPTQ | 利用近似二阶信息和误差补偿进行权重量化的方法。 |
| <a id="kv-quant"></a>KV 量化 | 降低 KV 表示精度，改变载荷与读写路径，并引入需要验证的数值误差。 |
| <a id="outlier-channel"></a>离群通道 | 幅值或分布显著偏离其他通道的维度，可能影响量化范围与误差。 |

<div class="inference-legacy-anchors" aria-hidden="true"><span id="lr"></span></div>

## 分布式与框架

| 术语 | 定义 |
|---|---|
| <a id="tp"></a>张量并行（TP） | 在算子或层内切分张量，并通过必要通信形成后继所需结果。 |
| <a id="pp"></a>流水线并行（PP） | 按层或阶段分配计算，以激活传递连接各阶段。 |
| <a id="ep"></a>专家并行（EP） | 将专家分配到不同 rank，并按 token 路由派发与合并结果。 |
| <a id="dp"></a>数据并行（DP） | 将不同输入分配到并行执行组；稠密服务常采用模型副本，MoE 组合需另看 rank 布局。 |
| <a id="moe"></a>混合专家（MoE） | 按输入选择部分专家执行的模型结构，路由与通信成本仍需计入。 |
| <a id="all-reduce"></a>all-reduce | 集合规约并使各参与方得到规约结果；算法、次数和通信路径由实现决定。 |
| <a id="all-to-all"></a>all-to-all | 参与方互相交换各自面向不同目标的数据分片，可存在不均匀流量。 |
| <a id="pipeline-bubble"></a>流水线气泡 | 阶段缺少可执行工作形成的空闲，受依赖、失衡和调度影响。 |
| <a id="context-parallelism"></a>上下文并行 | 沿序列或状态位置维分配注意力工作与存储，保持规定的全局依赖。 |
| <a id="pd-disaggregation"></a>PD 分离 | 将 Prefill 与 Decode 分配到不同执行实例或池，并交接所需状态。 |
| <a id="vllm"></a>vLLM | 提供请求调度、状态管理、模型执行与服务接口等能力的推理项目，行为需注明版本。 |
| <a id="sglang"></a>SGLang | 包含模型服务运行时与相关生成能力的项目，不能仅按历史 DSL 定位理解。 |
| <a id="xgrammar"></a>XGrammar | 结构化生成引擎，结合可预处理的 token 信息与运行时语法状态生成约束。 |

## 继续查阅

- [请求与指标](01-request-and-metrics/README.md)
- [状态与 KV 管理](04-state-and-memory/README.md)
- [采样与解码](06-sampling-and-decoding/README.md)
- [写作与建模约定](_conventions.md)
