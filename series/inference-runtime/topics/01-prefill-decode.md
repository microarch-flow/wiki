# 01 LLM 推理基础:Prefill / Decode 两阶段 / Inference Fundamentals

> 状态:草稿
>
> 一句话定位:把「自回归生成」拆成 prefill 与 decode 两阶段,推导出它们一个 compute-bound、一个 memory-bound 的根因,并给出 KV cache 字节公式(含 GQA)。本篇是后续所有数字的源头。

## 概念 (Concept)

**自回归生成([autoregressive](glossary.md#autoregressive))**:LLM 逐 token 生成,第 $t$ 个 token 的输入是前 $t-1$ 个 token(prompt + 已生成),输出该位置下一个 token 的分布。因此生成在时间上**串行**——这是后面一切时延问题的物理起点。

一次推理被工程上拆成两个形态迥异的阶段:

| 阶段 | 处理对象 | 形态 | 产出 |
|---|---|---|---|
| **[预填充](glossary.md#prefill) (prefill)** | 整段 prompt 的 $s_p$ 个 token | **一次** forward 并行处理全部位置 | 第 1 个输出 token + 填满 KV cache |
| **[解码](glossary.md#decode) (decode)** | 每步 1 个新 token | 自回归,逐步循环 | 每步 1 个 token,追加进 KV cache |

**为什么需要 [KV 缓存](glossary.md#kv-cache)**:注意力中,当前 token 的 query 要和**所有历史 token** 的 key/value 做内积。若不缓存,decode 每生成一个 token 都要重算前面所有 token 的 $K,V$,第 $t$ 步代价 $O(t)$,整段 $O(s^2)$。缓存历史 $K,V$ 后,decode 每步只需:为新 token 算 1 个 $Q,K,V$,把新 $K,V$ 追加进 cache,再用新 $Q$ 与全量 cache 做注意力。**KV cache 用显存换重算**——它的字节数与带宽,是 decode 阶段成本模型的核心变量。

## 机制 (Mechanism)

### 一个 decoder layer 做什么(用于后面计数)

每层(忽略 norm/残差等廉价项)主要是几个矩阵乘:

1. **QKV 投影**:$x[d] \to Q[h\cdot d_h],K[h_{kv}\cdot d_h],V[h_{kv}\cdot d_h]$。GQA 下 $K,V$ 只有 $h_{kv}$ 个头(见下)。
2. **注意力**:$\text{scores}=QK^\top$,softmax,再 $\cdot V$。这是唯一与序列长度 $s$ 相关、且**不含可复用权重**的部分。
3. **输出投影**:$[h\cdot d_h]\to[d]$。
4. **MLP / FFN**:通常 SwiGLU,三个矩阵(gate/up/down),中间维 $d_{ff}$(典型 $\approx \tfrac{8}{3}d$ 或 $4d$)。**FFN 通常占单层参数与 FLOP 的大头**。

### 形状差异 = compute/memory-bound 分野的根因

同样的权重,两个阶段喂进去的激活张量形状不同:

- **Prefill**:激活 $[b,\,s_p,\,d]$。每个权重矩阵参与的是 **GEMM(矩阵×矩阵)**,$M=b\cdot s_p$ 很大 → 每次从 HBM 读入的权重被复用 $M$ 次 → **算术强度高 → compute-bound**(算力是瓶颈)。
- **Decode**:激活 $[b,\,1,\,d]$(每请求只有 1 个新 token)。权重矩阵参与的是 **GEMV / 瘦 GEMM**,$M=b$(常为几~几十)→ 读入的权重几乎只用一次 → **算术强度低 → memory-bound**(HBM 带宽是瓶颈,算力闲置)。

> 一句话:**prefill 把权重摊给很多 token,decode 把权重摊给很少 token**。这就是为什么同一个模型、同一张卡,prefill 看 TFLOP/s、decode 看 TB/s。`05` 会进一步看这如何决定 attention kernel 形态(FlashAttention vs FlashDecoding)。

## 量化与公式 (Quantification)

符号(沿用 [`_conventions.md`](_conventions.md) §4):$b$ batch,$s$ 上下文长度 [token],$L$ 层数,$h$ query 头数,$h_{kv}$ KV 头数,$d_h$ head dim,$d=h\,d_h$ hidden,$P$ 参数量,$p$ 字节/元素,$BW$ HBM 带宽 [byte/s],$C$ 算力 [FLOP/s]。

### (1) KV cache 字节数 —— 最常用的一条

每 token、每层缓存 $K$ 和 $V$ 各 $h_{kv}\cdot d_h$ 个元素:

$$\text{KV}_{\text{tok}} = 2 \cdot L \cdot h_{kv} \cdot d_h \cdot p \quad[\text{byte/token}]$$

$$\text{KV}_{\text{total}} = b \cdot s \cdot \text{KV}_{\text{tok}} = 2\, b\, s\, L\, h_{kv}\, d_h\, p \quad[\text{byte}]$$

- 前导 `2` = $K$ 与 $V$ 两份。
- **[GQA](glossary.md#gqa) 因子**:多 query 头共享 KV 头,字节数相对 MHA($h_{kv}=h$)缩小 $h_{kv}/h$。[MQA](glossary.md#mqa) 是 $h_{kv}=1$ 的极端。这是现代大模型把 KV 压下来的头号手段——**不计 GQA 会把 KV/token 高估约 $h/h_{kv}$ 倍**。

**算例:Llama-3 70B,fp16。** 配置 $L=80,\ h=64,\ h_{kv}=8,\ d_h=128,\ d=8192$ 【精确值,官方 `config.json`;Llama-3 / 3.1 / 3.3 的 70B 这几个结构参数一致】,$p=2$:

$$\text{KV}_{\text{tok}} = 2\cdot 80\cdot 8\cdot 128\cdot 2 = 327{,}680\ \text{byte} = 320\ \text{KiB/token}$$

对比若是 MHA($h_{kv}=64$):$2560$ KiB/token —— GQA 把 KV 压了 $8\times$。
- 一条 8K 上下文请求:$8192\times320\text{ KiB}=2.5\ \text{GiB}$ 的 KV。
- 这条 2.5 GiB 直接决定单卡能并发多少请求(`15` 展开),也决定 decode 每步要从 HBM 搬多少字节(下面 (3))。

### (2) Decode 的算术强度与 roofline

[Roofline](glossary.md#roofline) 拐点(ridge point)$= C/BW$ [FLOP/byte];[算术强度](glossary.md#arithmetic-intensity) $AI=\frac{\text{FLOP}}{\text{bytes from HBM}}$,$AI<$ ridge → [memory-bound](glossary.md#memory-bound)。

一个 decode step(batch $b$,dense 模型):
- **FLOP** $\approx 2Pb$(每参数 1 次乘加 = 2 FLOP,每请求过一遍全部权重)。
- **HBM 读字节** $\approx \underbrace{P\,p}_{\text{权重(与 }b\text{ 无关)}} + \underbrace{b\,s\,\text{KV}_{\text{tok}}}_{\text{读全量 KV}}$。

$$AI_{\text{decode}} = \frac{2Pb}{P\,p + b\,s\,\text{KV}_{\text{tok}}}$$

两个极限很说明问题:
- **权重主导**(短上下文、KV 项可忽略):$AI \approx \dfrac{2b}{p}$。fp16 时 $AI\approx b$。→ **batch 越大越靠近 compute-bound**,这就是 decode 必须攒 batch 的根因。
- **KV 主导**(长上下文、$b$ 大):$AI \to \dfrac{2P}{s\,\text{KV}_{\text{tok}}}$,与 $b$ 无关 → 再加 batch 也压不动,**长上下文 decode 恒 memory-bound**。

**算例:H100 SXM80 的 ridge。** $C = 989.5$ TFLOP/s(BF16/FP16 Tensor Core,**稠密**;官方标称 1,979 TFLOPS 是带 2:4 结构稀疏的两倍值)、$BW = 3.35$ TB/s(HBM3)【精确值,NVIDIA H100 datasheet】:

$$\text{ridge} = \frac{989.5\times10^{12}}{3.35\times10^{12}} \approx 295\ \text{FLOP/byte}$$

fp16 权重主导时要 compute-bound 需 $b\gtrsim 295\cdot p/2 = 295$。实际并发远到不了(显存装不下那么多 KV,见 `15`),**故 decode 在真实部署中几乎总是 memory-bound**——这条结论是后面几乎所有优化(continuous batching、投机解码、量化)的动机。

### (3) 由带宽直接得 decode 时延/吞吐下界

memory-bound 下,decode 单步时间被 HBM 流量决定:

$$t_{\text{step}} \gtrsim \frac{P\,p + b\,s\,\text{KV}_{\text{tok}}}{BW},\qquad \text{ITL} = t_{\text{step}},\qquad \text{吞吐} = \frac{b}{t_{\text{step}}}=\frac{b\,BW}{P\,p+b\,s\,\text{KV}_{\text{tok}}}$$

系统吞吐随 $b$ 增长但有上界:$b\to\infty$ 时 $\to \dfrac{BW}{s\,\text{KV}_{\text{tok}}}$ —— **长上下文下吞吐被 KV 带宽封顶,与算力无关**。([ITL/TTFT](glossary.md#itl) 的完整推导与 prefill 侧(compute-bound,TTFT $\approx 2Pb\,s_p/C$)留给 `15`。)

> 现实性提示:Llama-3 70B fp16 权重 $=2P\,p\approx 140$ GB $>$ 80 GB,**单张 H100 装不下**,需 TP≥2 或量化(→ `10`、`11`)。本篇公式里的 $BW,C$ 届时换成「多卡聚合」或「量化后 $p$ 变小」即可复用。

## 与架构建模的接口 (Modeling Interface)

- **可扫设计参数(design knobs)**:精度 $p$(→ `10` 量化)、GQA 比 $h_{kv}/h$、模型结构 $L,d,d_{ff}$、运行时 $b,s$。其中 $p$ 与 $h_{kv}/h$ 是「一改全盘动」的旋钮。
- **可换档复用的公式**:(3) 里把 $BW$ 从 HBM 换成 NVLink/PCIe/NVMe 档,同一式即给出「KV 过链路」的传输时间——这是 `12` PD 分离与 KV offload 的统一接口。
- **喂给仿真器 / SLA 判定的量**:
  - $\text{KV}_{\text{tok}}(L,h_{kv},d_h,p)$ → 显存占用 → 最大并发(准入水位,`08`/`15`)。
  - 每 decode step 的 HBM 流量 $P p + b\,s\,\text{KV}_{\text{tok}}$ → ITL 下界 → 是否满足 ITL SLA(`02`)。
  - prefill FLOP $\approx 2Pb\,s_p$ → TTFT 下界 → 是否满足 TTFT SLA。
- **ridge point $=C/BW$** 是仿真器判定某 kernel 落在 roofline 哪一侧的开关:同一 kernel 在不同 $(C,BW)$ 配置下可能跨越 compute/memory-bound 边界,这正是架构探索要扫的。

## 延伸阅读 (References)

- 下一篇:[`02` 服务指标与 SLO](02-metrics-slo.md)(把这里的 ITL/TTFT/吞吐口径定死)。
- [`03` 朴素实现的瓶颈](03-naive-bottlenecks.md):KV 字节 → 显存碎片;decode memory-bound → 静态批尾部浪费。
- [`05` 注意力核](05-attention-kernels.md):形状差异如何决定 kernel(FlashAttention/FlashDecoding)。
- [`10` 量化](10-quantization.md):$p$ 作为旋钮;[`15` 算例](15-quantitative-estimation.md):本篇公式代入完整数字。
- 外部(已核实):
  - NVIDIA H100 Tensor Core GPU Datasheet —— BF16 稠密 989.5 TFLOPS(标称 1,979* 含 2:4 稀疏)、HBM3 3.35 TB/s(SXM80)。[NVIDIA H100 product page](https://www.nvidia.com/en-us/data-center/h100/) / [Lenovo H100 product guide](https://lenovopress.lenovo.com/lp1732-thinksystem-nvidia-h100-pcie-gen5-gpu)(规格表注明 1,979 TFLOPS「*With structural sparsity」)。
  - Meta Llama-3 70B 结构参数($L{=}80,h{=}64,h_{kv}{=}8,d_h{=}128,d{=}8192$):HF `config.json`,如 [NousResearch/Meta-Llama-3-70B-Instruct](https://huggingface.co/NousResearch/Meta-Llama-3-70B-Instruct/blob/main/config.json);[The Llama 3 Herd of Models](https://arxiv.org/pdf/2407.21783)。
  - FlashAttention(Dao et al., 2022)对注意力 IO 复杂度的分析。
