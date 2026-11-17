# Prefill 与 Decode：计算、状态与资源需求

<div class="inference-legacy-anchors" aria-hidden="true"><span id="01-llm-推理基础prefill-decode-两阶段-inference-fundamentals"></span></div>

上级：[本专题导读](README.md)

Prefill 与 Decode 的区别，首先是本轮需要计算多少个位置、这些位置依赖哪些历史状态。性能差别由计算形状和状态访问共同产生，不能只用阶段名称判断瓶颈。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="概念-concept"></span></div>

## 从自回归依赖到两个阶段

设输入已有 $s_p$ 个 token。因果模型中，位置 $j$ 可以读取不晚于自身的输入位置。输入 token 已知，因此 Prefill 可以并行计算多个位置；因果掩码保证不会读取未来位置。

Prefill 最后一个位置产生的 logits 通常用于采样第一个输出 token。此后，普通 Decode 每次把上一步选出的 token 输入模型，产生下一个 token 的分布。单条序列的生成存在依赖；不同请求仍可批量执行。

不使用 KV 缓存而每轮重跑整个前缀时，历史位置的投影、MLP 和注意力会被重复计算。保存 KV 后，新位置只需计算自己的投影和 MLP，并读取历史 K/V。对全注意力而言，单次新位置的注意力工作量仍随上下文长度增长；缓存没有消除这部分计算。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="机制-mechanism"></span><span id="一个-decoder-layer-做什么用于后面计数"></span><span id="形状差异-computememory-bound-分野的根因"></span></div>

## 一层模型在处理什么

以常见的稠密 Decoder 层为例，输入经归一化、Q/K/V 投影、注意力、输出投影和 MLP，并通过残差连接更新隐藏状态。具体顺序取决于模型结构。

Prefill 的线性层处理多行输入，通常更容易复用权重。低并发 Decode 的行数较少，权重摊薄较弱。Attention 又受查询长度、历史 KV 长度、头数和内核并行度影响。

这解释了“Prefill 常偏计算、低批量 Decode 常偏带宽”的经验。但短输入、小算子、启动开销、长上下文、大批量或通信，都可能改变主要限制。判断方法见[资源下界与实际瓶颈](../../storage/01-memory-hierarchy/03-performance/memory-bound-vs-compute-bound.md)。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="量化与公式-quantification"></span><span id="1-kv-cache-字节数-最常用的一条"></span></div>

## KV 容量公式及其边界

对各层均采用相同全注意力布局、K 与 V 维度相同的模型，定义：

| 符号 | 含义 |
|---|---|
| $L$ | 注意力层数 |
| $h_q,h_{kv}$ | 查询头数、KV 头数 |
| $d_h$ | 每头维度 |
| $p_{kv}$ | 每个 KV 元素的存储字节数 |
| $k_{kv}$ | 每个 token 在所有层的 KV 有效载荷，byte/token |

$$k_{kv}=2Lh_{kv}d_hp_{kv}$$

因子 2 对应 K 和 V。GQA 让多个查询头共享 KV 头；不能把 $h_q$ 代入 KV 容量。

例如 $L=80,h_{kv}=8,d_h=128,p_{kv}=2$，得到 $k_{kv}=327680$ byte/token，即 320 KiB/token。8,192 个已缓存位置占 2.5 GiB 有效载荷。分页尾部、缩放参数、复制和块表另算。

MLA、滑动窗口和混合注意力／循环状态模型不直接套用这个式子。应逐层、逐状态池计数，见[完整内存预算](../04-state-and-memory/runtime-state.md)。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="2-decode-的算术强度与-roofline"></span></div>

## 从工作量估算到时间边界

假设一次普通 Decode 有 $B_{\rm req}$ 条序列，每条产生一个 token。设序列 $i$ 的可见 KV 长度为 $s_i$，模型参数量为 $P$，权重字节数为 $p_w$。

在线性层近似下，工作量约为 $2PB_{\rm req}$ FLOP。全注意力的 QK 与 AV 还需要约：

$$F_{\rm attn}\approx4Lh_qd_h\sum_i s_i$$

它忽略 softmax、归一化等操作，却不能在分析长上下文时直接删除。FMA 按 2 FLOP 计。

若假设本轮权重从 HBM 读取一次、每条序列的 KV 有效载荷读取一次，可构造逻辑流量估算：

$$D_{\rm logical}\approx Pp_w+k_{kv}\sum_i s_i$$

这个估算没有包含 KV 写入、中间张量、缓存命中和实际内核的重复读取。它不是硬件计数器测得的 HBM 字节数。算术强度 $F/D$ 必须使用一致的工作量和观察边界。

对指定资源，若工作量与流量均已确定，可计算理想时间下界：

$$T_{\rm resource}\ge\max(F/C_{\rm peak},D/BW_{\rm peak})$$

实际时间还受启动、依赖、通信和资源利用率影响。多个串行算子的时间不能仅用全模型总 FLOP 和总字节的一次 max 完整描述。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="3-由带宽直接得-decode-时延吞吐下界"></span><span id="与架构建模的接口-modeling-interface"></span></div>

## 何时可以把迭代时间写成 token 间隔

只有所有请求每轮都被选择、每轮各产出一个 token、输出及时返回且没有其他等待时，单请求 ITL 才接近迭代时间，系统输出速率才接近 $B_{\rm req}/T_{\rm step}$。

调度跳过请求、推测解码批量提交 token、流式缓冲和 PD 交接都会改变对应关系。多卡带宽也只有在负载均衡、切分匹配且必要通信已处理时才能聚合。NVLink 或 SSD 传输的是特定载荷，不能把整个 HBM 流量式中的带宽名称替换后继续使用。

<div class="inference-legacy-anchors" aria-hidden="true"><span id="延伸阅读-references"></span></div>

## 来源与后续

- [模型结构背景](../../workload/01-foundation-model-components/attention-and-transformer.md)解释 Attention 的数学语义。
- [GQA 原论文](https://arxiv.org/abs/2305.13245)说明查询头与 KV 头的分组。
- [Transformer 推理扩展研究](https://arxiv.org/abs/2211.05102)讨论批量、并行与资源约束。
- 继续阅读[服务指标](02-metrics-slo.md)；具体数字的使用方式见[条件算例](../09-measurement-and-cases/15-quantitative-estimation.md)。
