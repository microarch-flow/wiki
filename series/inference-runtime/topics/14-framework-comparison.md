# 14 框架对比:vLLM vs SGLang / Framework Comparison

> 状态:草稿
>
> 一句话定位:把 [`04`](04-dynamic-shape-batching.md)–[`13`](13-constrained-decoding.md) 的机制映射到两个真实框架。**诚实前提:机制已大面积趋同**——比"谁有功能 X"已无意义;真正的差异是**设计重心、编程模型、各自擅长的 workload 类**。

## 概念 (Concept)

两者同源(高效 LLM serving),但**signature 创新与重心不同**:

| | vLLM | SGLang |
|---|---|---|
| 起点 | PagedAttention([`06`](06-paged-kv-cache.md),SOSP'23,Berkeley) | RadixAttention([`07`](07-radix-prefix-reuse.md),NeurIPS'24,LMSYS) |
| 重心 | **block 内存管理器** = 内存/吞吐引擎 | **radix 前缀树 + 前端 DSL** = 程序结构感知运行时 |
| 一句话定位 | 加载模型、收 HTTP、尽快返回的**通用推理服务器** | engine + **编程模型**,运行时理解多步推理/工具调用/分支并为其优化 |

**关键认知**:经过两年互相吸收,**机制集合已大面积重叠**(两者都有 paged KV、前缀缓存、continuous batching、chunked prefill、投机解码、量化、PD 分离、结构化输出)。所以本篇不列"功能差异表"(多半已失真),而是讲**重心**与**何时用谁**。

## 机制 (Mechanism):映射矩阵

| 机制(本 wiki) | vLLM | SGLang | 原创 |
|---|---|---|---|
| KV 管理([`06`](06-paged-kv-cache.md)) | **PagedAttention**(核心抽象) | paged/token attention(同类) | vLLM |
| 前缀复用([`07`](07-radix-prefix-reuse.md)) | Automatic Prefix Caching (APC) | **RadixAttention**(核心抽象)+ cache-aware 调度 | SGLang |
| 变长/批处理([`04`](04-dynamic-shape-batching.md)) | continuous batching + chunked prefill | 同 | Orca 系 |
| 注意力核([`05`](05-attention-kernels.md)) | FlashAttention/FlashInfer | FlashInfer(深度用) | 共用 |
| 调度([`08`](08-scheduling.md)) | **V1 重写**降 CPU 开销 | cache-aware 调度 | — |
| 投机([`09`](09-speculative-decoding.md)) | 支持(EAGLE 等) | 支持(EAGLE 等) | 共用 |
| 量化([`10`](10-quantization.md)) | GPTQ/AWQ/FP8,广 | 同 | 共用 |
| 并行([`11`](11-cluster-parallelism.md)) | TP/PP + **Wide-EP** | TP/PP + **大规模 EP** | 共用 |
| PD 分离([`12`](12-pd-disaggregation.md)) | 支持 | 支持(DeepSeek 实战) | DistServe/Mooncake 系 |
| 约束解码([`13`](13-constrained-decoding.md)) | XGrammar/outlines | **XGrammar**(前端一等公民) | 共用引擎 |
| 前端编程模型 | OpenAI 兼容 API(薄) | **SGLang DSL**(gen/select/fork/JSON,厚) | SGLang |

> 读法:**vLLM 的重心是 [`06`](06-paged-kv-cache.md) 那个 block 管理器**(一切围绕"把 KV 装好、把 GPU 喂满");**SGLang 的重心是 [`07`](07-radix-prefix-reuse.md) 的 radix 树 + [`13`](13-constrained-decoding.md) 的结构化前端**(一切围绕"识别程序结构、最大化复用")。其余机制两边都有,只是默认强调点不同。

## 量化与定位 (Performance & Positioning)

> ⚠️ **以下 benchmark 数字时效性极强、强 workload 依赖,release 之间会翻转;只看趋势,勿当定论。**【厂商/社区报告值】

- **趋同区**:唯一 prompt、无前缀重叠的纯 batch → **两者吞吐接近**(都靠 paged KV + continuous batching,见 [`04`](04-dynamic-shape-batching.md)/[`06`](06-paged-kv-cache.md))。
- **分化区**:prefix-heavy / 多轮 / agent → **SGLang RadixAttention 占优**(前缀重叠越多越大,[`07`](07-radix-prefix-reuse.md) 报告可达 6.4×;多轮约 ~10%)。**但有前提**:需真有前缀重叠 **且显存够放缓存**——低重叠 + 紧显存时,radix LRU 反而占了本可服务新请求的内存(见 [`07`](07-radix-prefix-reuse.md) 的命中率/容量耦合)。
- **大规模 MoE**:两者都走 **PD 分离([`12`](12-pd-disaggregation.md))+ 大规模 EP([`11`](11-cluster-parallelism.md))**,且都从 **TP attention 转向 DP attention + EP MoE**(MoE 的最优并行画像不同于 dense)。vLLM Wide-EP、SGLang DeepSeek 实战都是这条路线。
- **vLLM V1 的教训直接印证 [`08`](08-scheduling.md)**:重写动因是"**CPU 调度开销在某些场景可超总推理时间一半**"——decode 步只有毫秒级,host 侧调度若不够轻 / 不与 GPU 重叠,就成瓶颈。这是 [`08`](08-scheduling.md)「调度开销 ≪ GPU step」、[`13`](13-constrained-decoding.md)「host lane」在真实框架里的兑现。

## 与架构建模的接口 (Modeling Interface)

- **两个框架是你成本模型的两个"参照实现",对应两种重心**:
  - 用 vLLM 心智 → 建模"**通用吞吐 + 内存效率**"基线(中心抽象 = [`06`](06-paged-kv-cache.md) 的 block 池 + $\eta_\text{mem}$)。
  - 用 SGLang 心智 → 建模"**高前缀复用 + 结构化 workload**"(中心抽象 = [`07`](07-radix-prefix-reuse.md) 的命中率 $h$ + [`13`](13-constrained-decoding.md) 的 host lane)。
- **最重要的 takeaway:建机制,别建框架。** 机制([`04`](04-dynamic-shape-batching.md)–[`13`](13-constrained-decoding.md))是稳定的建模对象;框架只是这些机制的**不同默认参数组合 + 不同重心**。archax 应把每个机制建成可开关/可配的模块,然后"vLLM 配置"和"SGLang 配置"就是该模块空间里的两个点——这样工具不会随框架版本过时。
- **选型 = workload 落点**:高共享 / agent / 结构化输出 → SGLang 重心对路;通用高吞吐 / 广模型广硬件 / 生产默认 → vLLM。但因趋同,**选型差异在收窄,workload 特征(前缀重叠率 $h$、是否结构化、是否 MoE)比框架名更决定性能**——这正是你该扫的维度,而非"选哪个框架"。
- **host lane 必建**:V1 的教训说明纯 GPU roofline 不够;archax 要显式建 CPU 调度 + mask + CPU↔GPU 同步一条 lane(呼应 [`08`](08-scheduling.md)/[`13`](13-constrained-decoding.md))。

## 延伸阅读 (References)

- 上游:本篇是 [`04`](04-dynamic-shape-batching.md)–[`13`](13-constrained-decoding.md) 的综合;重点回看 [`06`](06-paged-kv-cache.md)(vLLM 重心)、[`07`](07-radix-prefix-reuse.md)+[`13`](13-constrained-decoding.md)(SGLang 重心)、[`08`](08-scheduling.md)(V1 教训)。
- 下游:[`15` 算例](15-quantitative-estimation.md)(代入具体框架/硬件的数字)。
- 外部(已核实,数字时效性强):
  - vLLM:[PagedAttention SOSP'23](https://arxiv.org/abs/2309.06180);V1 重写(CPU 调度开销动因);[Wide-EP 大规模 serving 博客](https://blog.vllm.ai/2025/12/17/large-scale-serving.html)。
  - SGLang:[RadixAttention NeurIPS'24](https://arxiv.org/abs/2312.07104);DeepSeek PD 分离 + 大规模 EP 实战。
  - `TODO(核实)`:本篇所有 tok/s / 倍数为某时点社区报告;若进 `15` 或对外引用,取你测试时点的官方 benchmark 复核。
