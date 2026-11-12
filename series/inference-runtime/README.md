# 大模型推理与推理引擎 · 学习 Wiki

> 视角:**系统软件架构师 / 成本模型**。不是通用入门教程——每个机制尽量落到可量化的量(roofline、算术强度、KV 字节、带宽、流量、固定成本摊薄),并标注「与硬件建模 / 架构探索的接口」。写作约束见 [`_conventions.md`](_conventions.md),术语见 [`glossary.md`](glossary.md)。

## 状态总览

编号已按**阅读顺序(依赖自底向上)**重排。状态取值:`未开始 → 草稿 → 已审阅`。

### 地基 (Foundations)

| # | 条目 | 文件 | 状态 |
|---|---|---|---|
| 01 | LLM 推理基础:自回归、Prefill/Decode、compute vs memory-bound、KV 字节公式(含 GQA/MQA) | [`01-prefill-decode.md`](topics/01-prefill-decode.md) | 草稿 |
| 02 | 服务指标与 SLO:TTFT / ITL / TPOT / throughput / goodput(被各篇与 SLA 判定引用) | [`02-metrics-slo.md`](topics/02-metrics-slo.md) | 草稿 |
| 03 | 朴素实现的瓶颈:KV 显存碎片、静态批尾部浪费、prefill/decode 互相干扰 | [`03-naive-bottlenecks.md`](topics/03-naive-bottlenecks.md) | 草稿 |

### 单机服务栈 (Single-node serving stack)

| # | 条目 | 文件 | 状态 |
|---|---|---|---|
| 04 | 动态 shape 与变长:不 padding、cu_seqlens/ragged、continuous batching、chunked prefill | [`04-dynamic-shape-batching.md`](topics/04-dynamic-shape-batching.md) | 草稿 |
| 05 | 注意力核与解码 kernel:FlashAttention / FlashDecoding / paged kernel(为何 prefill 与 decode kernel 形态不同) | [`05-attention-kernels.md`](topics/05-attention-kernels.md) | 草稿 |
| 06 | KV cache 管理:PagedAttention(分页、block table、按层分桶、CoW 前缀共享) | [`06-paged-kv-cache.md`](topics/06-paged-kv-cache.md) | 草稿 |
| 07 | 前缀复用:RadixAttention(radix tree、最长前缀匹配、LRU)、与 API 层 prompt caching | [`07-radix-prefix-reuse.md`](topics/07-radix-prefix-reuse.md) | 草稿 |
| 08 | 调度:iteration 内调度循环、准入水位、抢占(recompute vs swap) | [`08-scheduling.md`](topics/08-scheduling.md) | 草稿 |

### 加速与扩展 (Acceleration & scale-out)

| # | 条目 | 文件 | 状态 |
|---|---|---|---|
| 09 | 投机解码:draft-verify、rejection sampling 无损、加速比、Medusa/EAGLE/lookahead、与 batch 的张力 | [`09-speculative-decoding.md`](topics/09-speculative-decoding.md) | 草稿 |
| 10 | 量化:权重 + KV(FP8/INT8/AWQ/GPTQ);精度档 $p$ 作为可扫参数对成本模型的影响 | [`10-quantization.md`](topics/10-quantization.md) | 草稿 |
| 11 | 集群并行:TP / PP / EP、推理 vs 训练的差异 | [`11-cluster-parallelism.md`](topics/11-cluster-parallelism.md) | 草稿 |
| 12 | PD 分离 + KV 传输 / offload 分层存储(同一带宽公式换 NVLink↔PCIe↔NVMe 档) | [`12-pd-disaggregation.md`](topics/12-pd-disaggregation.md) | 草稿 |

### 应用层与收口 (App layer & synthesis)

| # | 条目 | 文件 | 状态 |
|---|---|---|---|
| 13 | 约束解码:grammar / FSM / JSON-constrained 输出 | [`13-constrained-decoding.md`](topics/13-constrained-decoding.md) | 草稿 |
| 14 | 框架对比:vLLM 与 SGLang 的核心设计与定位差异 | [`14-framework-comparison.md`](topics/14-framework-comparison.md) | 草稿 |
| 15 | 量化估算算例:Llama-3 70B + H100 80GB 推导 KV/token、最大并发、ITL、TTFT、吞吐 | [`15-quantitative-estimation.md`](topics/15-quantitative-estimation.md) | 草稿 |

每写完一篇,这里与该篇顶部状态行同步更新。

## 推荐阅读顺序

编号即阅读顺序。三条主线:

1. **地基(01–03)**:`01` 是后面所有数字的来源(两阶段 + roofline + KV 字节),务必先读;`02` 把 TTFT/ITL/吞吐/goodput 定义清楚,后面所有「浪费 / 约束 / 判定」都引用它;`03` 说明朴素实现为什么不行,引出整个服务栈。
2. **单机服务栈(04–08)**:`04` continuous batching 回应 `03` 的尾部浪费 → `05` kernel 解释 prefill/decode 算力形态 → `06` PagedAttention 回应 KV 碎片 → `07` 前缀复用 → `08` 调度把 04–07 串成一个 iteration 循环。
3. **加速与扩展 + 收口(09–15)**:`09` 投机解码(时延/吞吐权衡)→ `10` 量化(成本模型的精度旋钮)→ `11` 多卡并行 → `12` PD 分离把单机栈搬上集群(KV 过链路)→ `13` 约束解码 → `14` vLLM vs SGLang 把机制映射到真实框架 → `15` 全链路算例,作为成本模型的「黄金样例」。

## 约定

- 命名:`topics/NN-slug.md`,两位序号。
- 公式:行内 `$...$`、独立 `$$...$$`;每符号给量纲;关键公式带代入算例。
- 数字纪律:`【精确值】` / `【典型量级】` / `TODO(核实)`,不编造。
- 交叉引用:相对链接 + 术语表锚点。

## 决策记录 (changelog)

- **v0.3**:15 篇初稿全部完成(状态=草稿);过一轮交叉引用 + 一致性检查(链接/锚点/符号/数字),修正 2 处错链 + 统一算力口径;glossary 71 词条。待逐篇审阅。
- **v0.2**:采纳全部提案。新增 `02 指标/SLO`、`05 kernel`、`10 量化`、`13 约束解码`;`PD 分离`从原「集群」篇拆出为 `12` 并合并 KV offload/传输;`GQA/MQA` 并入 `01`;编号按阅读顺序重排(原「集群并行」由 03 后移至 11–12)。
- **v0.1**:初版 10 篇骨架。
