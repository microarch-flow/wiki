# 05 注意力核与解码 kernel:Prefill vs Decode / Attention Kernels

> 状态:草稿
>
> 一句话定位:同一套 attention 数学,因 query 长度 $s_q$ 在两阶段相差悬殊(prefill 的 $s_p$ vs decode 的 1),落成两种**完全不同形态的 kernel**——prefill 是 compute-bound 的 GEMM-tiling(FlashAttention),decode 是 memory-bound 的 GEMV、但要靠 split-KV 抢回占用率(FlashDecoding),再叠分页 KV 的 gather。本篇解释 [`01`](01-prefill-decode.md) 的「理想带宽下界」与实测 TPOT 之间那个 [MBU](glossary.md#mbu) 效率因子从哪来。

## 概念 (Concept)

attention 有两个独立的"长度"输入:**query 长度 $s_q$** 与 **KV 长度 $s_{kv}$**。两阶段取值天差地别:

| | $s_q$ | $s_{kv}$ | $S=QK^\top$ 形态 | 算术强度 | 瓶颈 |
|---|---|---|---|---|---|
| **prefill** | $s_p$(整段 prompt) | $s_p$ | $[s_p,s_p]$ 矩阵×矩阵 | 高 | compute |
| **decode** | $1$(每请求每步 1 个新 token) | $s$(全历史) | $[1,s]$ 向量×矩阵(GEMV) | 低 | memory |

这个 **$s_q$ 的 "$s_p$ vs 1"** 就是 [`01`](01-prefill-decode.md) 的 compute/memory-bound 分野在 kernel 层的根:GEMM 把权重/KV 摊给很多 query 位置 → 高复用;GEMV 只有一个 query 位置 → 读一遍 KV 几乎不复用。

两阶段共享一个内核难题:**(a)** 中间矩阵 $S=QK^\top$ 是 $O(s^2)$,不能落 HBM;**(b)** softmax 要按整行归一。[FlashAttention](glossary.md#flash-attention) 用 **tiling + online softmax** 一并解决——但**并行策略**两阶段必须不同,这是本篇的主线。

## 机制 (Mechanism)

### FlashAttention:不落 $S$ 矩阵的 tiling + online softmax

标准实现:算 $S=QK^\top$ 写 HBM、softmax 读写 HBM、再 $\cdot V$ —— $O(s^2)$ 次 HBM 往返 + $O(s^2)$ 显存。FlashAttention 把 $Q,K,V$ 切块放进 SRAM,块内算 partial,用 **online softmax**(维护 running max $m$、running sum $\ell$,合并时按指数差 rescale)增量累积输出,**全程不 materialize $S$**:HBM 访问从 $\Theta(s^2)$ 降到 $\Theta(s^2 d/M)$($M$=SRAM 容量),显存从 $\Theta(s^2)$ 降到 $\Theta(s)$。这是长 context 能跑起来的前提。

- **FA-2**:改并行划分、沿 seq 维并行、削减非 matmul FLOP,~2× FA-1。
- **FA-3**(Hopper):warp-specialization(用 TMA + Tensor Core 的异步做 producer-consumer)、matmul 与 softmax **ping-pong 交叠**、FP8 block-quant + incoherent processing → FP16 **740 TFLOPS ≈ H100 的 75%**(FA-2 仅 35%),FP8 ~1.2 PFLOPS。【论文报告值,FlashAttention-3】
- **这是 prefill 的主力**:$s_q=s_p$ 大,query 维天然多并行,GEMM 算术强度高 → FA tiling 把 Tensor Core 喂饱,落在 roofline 的 compute 侧。

### Decode 为什么不能照搬 FlashAttention:占用率塌方

decode 的 $s_q=1$,attention 的**天然并行维只有 $b\times h$ 个独立工作单元**(每个 query head 独立 attend,GQA 下仍是 $h$ 个 query head),而每个单元要**串行扫 $s$ 个 KV 位置**。低 batch + 长 context 时两头都坏:$b\cdot h$ 可能 $<$ SM 数 → 大量 SM 闲置;单元内扫 $s$ 很长 → 关键路径被一个长串行扫描主导。这正是 [`01`](01-prefill-decode.md) 「decode memory-bound」在 kernel 层的样子——**读完整 KV 是硬性的,但朴素 kernel 连"把读 KV 的活摊到所有 SM"都做不到**。

### FlashDecoding:加第三个并行维(split-KV)

把每条序列的长 KV 沿序列切成 $n_\text{split}$ 段,**每段在不同 SM 上独立算 partial attention**(各自的 local max / sum / 部分输出),最后一步 **reduction** 用 online-softmax 把 $n_\text{split}$ 个 partial rescale 合并:

- 工作单元 $b\cdot h \to b\cdot h\cdot n_\text{split}$(填满 SM),每单元扫 $s/n_\text{split}$(缩短关键路径),代价是多一步跨 split 的 reduction。
- 收益(报告值):长序列下 **attention 本身最高 ~50× 于 FA,端到端最高 ~8×**;序列长到 32k attention 时间仍近似常数(GPU 被喂满)。FlashDecoding++ 进一步优化 reduction(统一 max、异步)。
- **关键张力**:$b$ 越大,$b\cdot h$ 本身越接近占满 SM,split 的边际收益越小 → split-KV 主要救**低 batch / 长 context**;这与投机解码([`09`](09-speculative-decoding.md))、大 batch 吞吐模式互相拉扯。

### Paged attention kernel:在 gather 之上做 FlashDecoding

KV 一旦分页([`06`](06-paged-kv-cache.md)),物理 block 散落,decode kernel 必须**按 [block table](glossary.md#block-table) 间接寻址、gather 散块进 SRAM 再算**。与 vanilla FA 的差别:多了指针追逐,load 以 block 为粒度。**block 大小 $B_\text{blk}$ 是旋钮**:大 block → load 更连续 / DMA 友好、指针查找少,但内部碎片大([`06`](06-paged-kv-cache.md));小 block 反之。现代 decode kernel = **paged + split-KV 合体**(vLLM paged-attention v2、FlashInfer 库),`04` 的 varlen/`cu_seqlens` 也由同类 kernel 吃进去。

## 量化与公式 (Quantification)

新符号:$M$ SRAM/shared mem 容量 [byte];$n_\text{SM}$ SM 数;$n_\text{split}$ KV 切分数;$B_\text{blk}$ 分页块大小 [token];$k$ 占用率冗余倍率。

### (1) prefill:为什么必须不落 $S$

标准实现要在 HBM 物化 $S$。单 head、$s=8192$、fp16:$8192^2\times2\approx 134$ MB,再 $\times h\times b\times L$ 是天文数字且是 $O(s^2)$ 增长——**这就是 FlashAttention 存在的全部理由**。FA 把它降到 SRAM 内的 tile,HBM 访问 $\Theta(s^2 d/M)$,显存 $\Theta(s)$。

### (2) decode:占用率条件 → split 数

要占满 SM(留 $k\!\sim\!1\text{–}2$ 倍冗余隐藏延迟):

$$b\cdot h\cdot n_\text{split} \gtrsim k\, n_\text{SM}\quad\Rightarrow\quad n_\text{split} \gtrsim \frac{k\,n_\text{SM}}{b\,h},\qquad n_\text{split}\le \frac{s}{B_\text{blk}}\ \text{(不能切得比 block 还细)}$$

**算例(H100 SXM,$n_\text{SM}\approx132$;Llama-3 70B,$h=64$)**:
- $b=1$:$b h=64<132$ → 半数 SM 闲 → 取 $n_\text{split}\approx 4$ 凑到 256 单元填满。
- $b=8$:$bh=512>132$ → 通常无需 split(除非 $s$ 极长致关键路径仍长)。
- 结论:**split-KV 的价值随 batch 上升而衰减**,这条直接进 `09` 与 `08` 的权衡。【估算,占用率为量级判断,实际还看 register/shmem 占用】

### (3) 把 `01` 的理想下界接到实测 TPOT

[`01`](01-prefill-decode.md) (3) 给 decode 每步 HBM 下界 $\frac{Pp+b\,s\,\text{KV}_\text{tok}}{BW}$,是 **MBU=1 的理想**。实测:

$$\text{TPOT}_\text{实测} = \frac{Pp + b\,s\,\text{KV}_\text{tok}}{BW\cdot \text{MBU}},\qquad \text{MBU}=f(\text{占用率},\ \text{gather 连续性},\ \text{异步交叠})$$

kernel 决定 MBU:split-KV 占用不足 → MBU 掉;paged gather 不连续 → 有效带宽掉;FA-3 类异步 → MBU 升。**所以本篇是 `01` 理想下界与 realized 之间那座桥。** 示意:若占用率使 MBU$=0.6$,`01` 算的某 21 ms 理想步 → 实测 ~35 ms。

## 与架构建模的接口 (Modeling Interface)

- **attention kernel 是成本模型里"不规则 + $s$ 相关 + 访存受限"的那块,与规则 GEMM 分开计时**:
  - prefill attention:建模为 compute-bound,FLOP $\propto b\sum_i s_i^2$(per head,接 [`04`](04-dynamic-shape-batching.md) ragged),上限是 Tensor Core 峰值 × FA 利用率(FA-3 ~75%)。
  - decode attention:建模为 memory-bound,HBM 流量 = 读 KV $= b\,s\,\text{KV}_\text{tok}$,上限是 $BW\times\text{MBU}$。
- **可扫设计参数(直接对应 archax 要扫的硬件量)**:
  | 旋钮 | 影响 | 落点 |
  |---|---|---|
  | SRAM/shmem 容量 $M$ | FA tile 能否放下 → prefill attention 利用率 | (1) |
  | SM 数 $n_\text{SM}$ | decode 占用率 → 需要的 $n_\text{split}$ → MBU | (2) |
  | 分页块 $B_\text{blk}$ | gather 连续性(有效带宽)↔ 内部碎片 | (3)/`06` |
- **一条关键体系结构判定**:prefill attention 经 FA **可被推到 compute 侧**(去掉了 $O(s^2)$ HBM);decode attention **不可约地 memory-bound**(必须把 KV 读一遍),split-KV 只救回 *latency/占用率*,**救不回带宽下界**。→ 这决定了「加片上算力」对 prefill 有效、对 decode 几乎无效,而「加 HBM 带宽 / 压 $\text{KV}_\text{tok}$(GQA、量化)」才是 decode 的杠杆——是「算力 vs 带宽」配比探索的核心输入。

## 延伸阅读 (References)

- 上游:[`01`](01-prefill-decode.md)(compute/memory-bound 的源头)、[`04`](04-dynamic-shape-batching.md)(varlen/`cu_seqlens` attention)。
- 下游:[`06` PagedAttention](06-paged-kv-cache.md)(分页、block table、$B_\text{blk}$ 碎片);[`09` 投机解码](09-speculative-decoding.md)(把 decode 的 $s_q$ 从 1 抬到 $k$ → 改变 kernel 占用与算术强度)。
- 外部(已核实):
  - FlashAttention(Dao et al., 2022)/ FA-2(2023)/ **FA-3**(2024,arXiv 2407.08608,FP16 740 TFLOPS=75% H100、FP8 1.2 PFLOPS)。[tridao.me/blog/flash3](https://tridao.me/blog/2024/flash3/)
  - **Flash-Decoding**(Dao et al., 2023,split-KV,长序列 attention ~50×、端到端 ~8×)。[Stanford CRFM](https://crfm.stanford.edu/2023/10/12/flashdecoding.html) / [PyTorch blog](https://pytorch.org/blog/flash-decoding/)
  - FlashDecoding++(MLSys '24)、FlashInfer(LLM serving 的 paged/ragged attention kernel 库,vLLM/SGLang 在用)。
