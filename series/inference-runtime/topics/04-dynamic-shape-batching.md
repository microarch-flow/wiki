# 04 动态 shape 与变长处理 / Dynamic Shape & Variable-Length Serving

> 状态:草稿
>
> 一句话定位:在线推理的请求长度天生异质,把「矩形张量 + padding」换成「ragged 布局 + iteration 级调度」,正面消除 [`03`](03-naive-bottlenecks.md) 的尾部浪费(continuous batching)与 prefill 干扰(chunked prefill)。

## 概念 (Concept)

训练用矩形张量 `[b, s, d]`:一个 batch 内所有样本等长(或 pad 到等长)、长度离线已知。**在线推理破坏了这两个前提**:

- prompt 长度 $s_p$ 各请求不同(几十到几万 token);
- 输出长度 $N_\text{out}$ 生成时才知道(碰到 `<eos>` 才停);
- 请求异步到达,batch 成分时刻在变。

把训练那套硬搬过来,要么 **padding 到 batch 内最长**(浪费算力/显存),要么**等齐长度再批**(推高 TTFT)。本篇的四件套——**不 padding / cu_seqlens·ragged 布局 / continuous batching / chunked prefill**——就是把"动态 shape"当一等公民处理的工程答案。它们分别对应:省掉 pad 浪费、让变长能进同一个 kernel、消除静态批尾部浪费、消除 prefill 干扰。

## 机制 (Mechanism)

### 1. 为什么不 padding

要把 $b$ 条长度 $\{s_i\}$ 的序列塞进矩形张量,得 pad 到 $\max_i s_i$。pad 出来的位置:

- **照样过 FFN/投影的 GEMM**(算力白烧),attention 还要额外 mask 掉它们;
- **照样占 KV 显存**。

浪费比例 $1-\frac{\sum_i s_i}{b\,\max_i s_i}$——和 [`03`](03-naive-bottlenecks.md) 的 $\eta_\text{batch}$ 同形。prompt 长度长尾时,prefill batch 里大半算力在算 pad。**结论:不要矩形,要 ragged。**

### 2. cu_seqlens 与 ragged(packed / varlen)布局

不 pad,而是把 $b$ 条序列的 token **首尾相接拍平成一维**,总长 $\sum_i s_i$,再用一个**累积长度前缀和数组**记边界:

$$\texttt{cu\_seqlens} = [\,0,\ s_1,\ s_1{+}s_2,\ \dots,\ \textstyle\sum_i s_i\,]\quad(\text{长度 }b{+}1)$$

- 可批的算子(QKV 投影、FFN、输出投影这些**大 GEMM**)对拍平后的 `[Σs_i, d]` 一把算,**完全不受变长影响**——它们本来就是逐 token 独立的。
- 唯一与序列边界相关的是 **attention**:它必须只在每条序列**自己的段内**做。[FlashAttention](../glossary.md#flash-attention) 的 **varlen 接口**吃 `cu_seqlens`,在 kernel 内对每段独立做注意力(等价于一个隐式的块对角 mask),既不算 pad、也不会跨序列串味。
- 这就是 Orca 说的 **selective batching(选择性批处理)**:**GEMM 批、attention 拆**。它是 continuous batching 能高效跑的底层前提——否则不同 KV 长度的序列没法共一个 attention 调用。

> 与你硬件侧的接口:ragged/jagged tensor 本质是「数据相关的循环边界」,正是 archax 这类工具在 Execution IR 上要建模的不规则访存——`cu_seqlens` 就是把不规则性显式化成一个可索引的 metadata 数组,kernel 据此切 tile。

### 3. Continuous batching(iteration 级调度)

朴素静态批跑到整批结束才换人([`03`](03-naive-bottlenecks.md) 瓶颈 2)。**continuous batching** 把调度粒度从「一整批」降到「一个 iteration(一次 forward)」:每做完一步,调度器就**踢掉已生成 `<eos>` 的序列、补进等待队列里的新请求**。batch 成分逐 iteration 变化,GPU 不再陪最长那条空转。

- 这正是 Orca 的 **iteration-level scheduling**;它把 [`03`](03-naive-bottlenecks.md) 的 $\eta_\text{batch}$ 从 $\overline{L}/\max L$ 推向 $\approx 1$,同时新请求等待从「整批时长」降到「一步时长」→ TTFT 大降。
- 落地依赖第 2 点的 ragged 布局 + PagedAttention([`06`](06-paged-kv-cache.md))的非连续 KV 寻址(新请求随时插入,KV 不能要求连续)。三者是一套。

### 4. Chunked prefill(分块预填充)

针对 [`03`](03-naive-bottlenecks.md) 瓶颈 3:一个长 prefill 顶住所有 decode。**chunked prefill** 把一条 prompt 的 prefill 切成固定 token 预算 $T_\text{chunk}$ 的若干块,**每个 iteration 只处理一块**,并把这块和**正在进行的 decode token 拼进同一次 forward**(decode-maximal batching / SplitFuse)。

- 每个 iteration 的 forward 总 token 数被钉在 $\approx T_\text{chunk}$ → 每步耗时**可预测、有上界** → decode 的 ITL 不再被整段 prefill 拉爆。Sarathi-Serve 称之为 **stall-free scheduling(无停顿调度)**:新请求的 prefill chunk 加入运行中的 batch,**不暂停**任何在跑的 decode。
- 它把 prefill 和 decode 统一成「每 iteration 处理一个固定 token 预算」的单一抽象——**$T_\text{chunk}$ 成了平衡 TTFT-stall 与 prefill 吞吐的唯一旋钮**。

## 量化与公式 (Quantification)

新符号:$T_\text{chunk}$ 每 iteration 的 prefill token 预算 [token];$b_d$ 同 iteration 内的 decode 请求数;其余沿用 [`01`](01-prefill-decode.md)/[`03`](03-naive-bottlenecks.md)。

### (1) ragged vs padding 的计算量

- **可批 GEMM 部分**:padding 做 $b\,\max_i s_i$ 个 token 的功,ragged 只做 $\sum_i s_i$ → 省掉因子 $\dfrac{\sum_i s_i}{b\max_i s_i}=\eta_\text{batch}$(长尾下常 0.2–0.5)。
- **attention 部分**:每段 FLOP $\propto s_i^2$,ragged 总量 $\propto\sum_i s_i^2$;若误用一把大 attention 则是 $(\sum_i s_i)^2$,**ragged 把跨序列的 $\sum_{i\ne j}s_is_j$ 项全省掉**,长 batch 下差一个数量级。

### (2) chunked prefill 的 stall 上界与代价

- **stall 封顶**:一条 decode 撞上 prefill,最坏只等**一个 chunk** 的 forward,而非整段:
  $$\text{ITL}_\text{stall} \approx \frac{2P\,(T_\text{chunk}+b_d)}{C}\quad\text{(compute-bound)}\ \ \ll\ \ \frac{2P\,s_p}{C}=T_\text{prefill}$$
  **算例(2×H100 跑 70B,接 [`03`](03-naive-bottlenecks.md) 算例)**:整段 $s_p{=}4096$ 的 stall 是 ~570 ms;取 $T_\text{chunk}{=}512$ 切成 8 块,单次 stall 降到 $\approx 2\times70\text{e}9\times512/1\text{e}15\approx 72$ ms(忽略 $b_d$)。**ITL 尾从 ~570 ms 压到 ~70 ms,代价是这条 prompt 的 TTFT 略增(分 8 步走)。** 【估算,MFU 取 0.5;`15` 用实测复算】
- **代价 / 不能无限小**:chunk 越小,(a) prefill 的 GEMM 的 $M$ 维越小、算术强度下降、[MFU](../glossary.md#mfu) 掉;(b) 后续 chunk 做 attention 要重读前缀 KV,带来 $O(\sum_k k\cdot T_\text{chunk})$ 的额外 KV 读。故存在最优 $T_\text{chunk}^\*$ 平衡「decode stall ↓」与「prefill 吞吐 ↓」——这是要扫的设计点。

### (3) 实测收益(论文报告值,作量级参照)

| 机制 | 报告收益 | 来源 |
|---|---|---|
| iteration-level scheduling(continuous batching) | GPT-3 175B 上,**同延迟吞吐 36.9×** vs FasterTransformer | Orca, OSDI '22 |
| chunked prefill + SplitFuse | 对 vLLM **有效吞吐 ≤2.3×、平均延迟 ~2×↓、尾延迟 ≤3.7×↓** | DeepSpeed-FastGen |

【论文报告值,口径随各文 setup 而异;引作量级,勿当成你 workload 的预期】

## 与架构建模的接口 (Modeling Interface)

- **成本模型的输入从「最坏情况矩形」换成「长度分布」**:compute 项用 $\sum_i s_i$、attention 项用 $\sum_i s_i^2$,直接吃 workload trace 的 $\{s_p^{(i)},N_\text{out}^{(i)}\}$,不要再用 $b\cdot\max s$。
- **可扫设计参数**:
  - $T_\text{chunk}$ —— 把 TTFT-stall(ITL p99)与 prefill MFU 连成一条曲线的**单旋钮**,是仿真器里最值钱的一个 knob;扫它即得 [`02`](02-metrics-slo.md) 的 latency–throughput 前沿。
  - iteration 调度的 CPU 开销:每步要做一次调度决策,**该开销必须 ≪ 一个 iteration 的 GPU 时间**,否则 GPU 出现气泡;decode 步本就短(~毫秒),这条约束对调度器实现是硬指标(→ `08`)。
- **仿真器的 iteration 抽象**:chunked prefill 把每个 iteration 规约成「处理固定 token 预算 $T_\text{chunk}+b_d$」→ 每 iteration 时长**可解析预测**(compute-bound 段 $\approx 2P(T_\text{chunk}+b_d)/C$),非常适合做事件仿真器的基本时间片——比"整段 prefill 一个大事件"好建模得多。
- **ragged = 数据相关控制流**:`cu_seqlens` 是把不规则访存显式化的 metadata,Execution IR 层可据此建模 tile 切分与不规则 HBM 访问;这也是 attention kernel(→ `05`)与 GEMM 在仿真里要分开计时的原因。

## 延伸阅读 (References)

- 上游:[`03` 朴素瓶颈](03-naive-bottlenecks.md)(本篇是其瓶颈 2、3 的解法)、[`01`](01-prefill-decode.md)(两阶段)、[`02`](02-metrics-slo.md)(TTFT/ITL)。
- 下游:[`05` 注意力核](05-attention-kernels.md)(varlen attention kernel 怎么实现)、[`06` PagedAttention](06-paged-kv-cache.md)(continuous batching 的 KV 寻址前提)、[`08` 调度](08-scheduling.md)(iteration 调度循环与 token 预算)。
- 外部(已核实):
  - Orca: *A Distributed Serving System for Transformer-Based Generative Models*, Yu et al., OSDI '22 —— iteration-level scheduling + selective batching,36.9× vs FasterTransformer。[USENIX PDF](https://www.usenix.org/system/files/osdi22-yu.pdf)
  - Sarathi-Serve: *Taming the Throughput-Latency Tradeoff in LLM Inference*, Agrawal et al., 2024 —— chunked-prefills + stall-free scheduling。[arXiv 2403.02310](https://arxiv.org/pdf/2403.02310)
  - DeepSpeed-FastGen —— Dynamic SplitFuse,≤2.3× 有效吞吐 / ≤3.7× 尾延迟 vs vLLM。[DeepSpeed blog](https://github.com/microsoft/DeepSpeed/blob/master/blogs/deepspeed-fastgen/README.md)
  - FlashAttention varlen / `cu_seqlens` API:见 `05` 引用。
