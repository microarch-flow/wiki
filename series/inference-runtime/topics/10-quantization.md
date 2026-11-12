# 10 量化:权重 / 激活 / KV / Quantization

> 状态:草稿
>
> 一句话定位:精度档 $p$ 是这套 wiki 里**耦合最广**的旋钮。它不是一个 $p$,而是**三个正交子旋钮**——$p_w$(权重)、$p_a$(激活)、$p_{kv}$(KV),各打成本模型里**不同的一项**。本篇拆开它们、回写 [`01`](01-prefill-decode.md)/[`06`](06-paged-kv-cache.md)/[`08`](08-scheduling.md)/[`09`](09-speculative-decoding.md)。**唯一有质量代价的加速手段**(区别于无损的 [`09`](09-speculative-decoding.md))。

## 概念 (Concept)

量化 = 用更少 bit 表示数。但**"量化什么"决定打中哪条瓶颈**——这是全篇的组织主线:

| 子旋钮 | 压的字节 | 受益阶段 | 物理原因 |
|---|---|---|---|
| **$p_w$**(权重) | $P\,p_w$ | 低 batch decode、能否装进 $N$ 卡 | decode weight-bound([`01`](01-prefill-decode.md)) |
| **$p_a$**(激活,配 $p_w$) | 激活字节 + 启用低精 tensor core | compute-bound prefill | 抬高有效算力 $C$ |
| **$p_{kv}$**(KV) | $\text{KV}_\text{tok}\propto p_{kv}$ | 并发、长上下文 decode | KV-bound([`01`](01-prefill-decode.md)) |

**与 [`09`](09-speculative-decoding.md) 的根本区别:量化有损(lossy)**,$p$ 是「性能 ↔ 质量」曲线上的点,不是纯加速。所以量化的设计空间探索要带一个「精度退化 ≤ $\varepsilon$」的约束(类似 SLA)。

## 机制 (Mechanism)

### 格式与字节

FP16/BF16 = 2 B,FP8(E4M3 / E5M2)= 1 B,INT8 = 1 B,INT4 = 0.5 B。FP8 两型:**E4M3**(范围小、精度高,前向用)、**E5M2**(范围大);Hopper Transformer Engine 原生支持。

### 权重量化(weight-only,W4A16):AWQ / GPTQ

只压权重到 INT4、激活仍 FP16;计算时**在线反量化(dequant)** 再走 FP16 tensor core。

- **为什么 weight-only 更容易**:激活有 **outlier channel**(少数维度幅值极大)难量化,而权重分布乖。
- **GPTQ**:逐层、用 Hessian/OBQ 二阶信息做**误差补偿 rounding**(W4/W3)。
- **AWQ**:用激活幅度找出 ~1% **salient 权重通道**、per-channel scaling 保护它们(W4,无混精存储、硬件友好)。
- **影响**:$P\,p_w$ 降约 $4\times$(16→4 bit)→ **低 batch decode(weight-bound)直接快、大模型能装进更少卡**;但**计算仍 FP16** → prefill / 大 batch **不提速**(还多 dequant 开销)。**weight-only 是「低 batch decode + 装得下」的杠杆,不是算力杠杆。**

### 权重+激活量化(W8A8):FP8 / SmoothQuant

权重和激活都低精 → 用 INT8/FP8 tensor core → **计算提速**。

- 难点仍是激活 outlier。**SmoothQuant**:把激活 outlier 按 per-channel scale **迁移进权重**,使两边都好量 → W8A8(INT8)。
- **FP8**(Hopper):原生 **2× BF16 算力**([`01`](01-prefill-decode.md):FP8 稠密 1979 vs BF16 989.5 TFLOPS)。W8A8-FP8 → **prefill ~2×**,且字节减半。
- **影响**:有效算力 $C\uparrow$(~2× FP8)→ compute-bound prefill 提速;字节减半也帮 decode。

### KV 量化($p_{kv}$):FP8 / INT8 / INT4 KV

直接压 KV cache:$\text{KV}_\text{tok}\propto p_{kv}$。FP8 KV → 减半 → **并发翻倍 + 长上下文 decode 带宽减半**。方法:per-token / per-channel / group-wise scaling;**FP8 KV 常近无损**,INT4 KV 需 group-wise 小心。**这是长上下文 decode(KV 主导,[`01`](01-prefill-decode.md))的杠杆。**

## 量化与公式 (Quantification)

### (1) 精度档表(Llama-3 70B,$P=70$e9,$\text{KV}_\text{tok}^{\text{fp16}}=320$ KiB)

权重(随 $p_w$):

| $p_w$ | bit | 权重 $P\,p_w$ | 装卡(H100 80GB) |
|---|---|---|---|
| FP16 | 16 | 140 GB | 需 2× |
| FP8 | 8 | 70 GB | 勉强 1×(KV 余量小) |
| INT4 | 4 | 35 GB | 1× 宽裕 |

KV(随 $p_{kv}$):

| $p_{kv}$ | $\text{KV}_\text{tok}$ | 8k 上下文 KV/req |
|---|---|---|
| FP16 | 320 KiB | 2.5 GiB |
| FP8 | 160 KiB | 1.25 GiB |
| INT4 | 80 KiB | 0.625 GiB |

### (2) 三个旋钮打三个项(回写 [`01`](01-prefill-decode.md))

decode 每步 HBM $= P\,p_w + b\,s\,\text{KV}_\text{tok}(p_{kv})$;prefill 时间 $\propto 1/C(p_a)$。

- **$p_w\downarrow$**:低 batch decode(权重主导)$\text{TPOT}\propto p_w$ → INT4 权重读约 $4\times$ less。
- **$p_{kv}\downarrow$**:长上下文(KV 主导)$\text{TPOT}\propto p_{kv}$;并发 $\propto 1/p_{kv}$([`06`](06-paged-kv-cache.md))。
- **$p_a\downarrow$(FP8)**:$C\uparrow 2\times$ → prefill TTFT ~减半([`01`](01-prefill-decode.md) prefill compute-bound)。

### (3) 回写各篇(这就是"牵一发")

| 篇 | 受影响的量 | 量化怎么改 |
|---|---|---|
| [`01`](01-prefill-decode.md) | $\text{KV}_\text{tok}=2Lh_{kv}d_h\,p_{kv}$ | $p_{kv}$ 直接进源公式 |
| [`06`](06-paged-kv-cache.md) | $\text{max\_conc}=\frac{M_\text{KV}\eta_\text{mem}}{\mathbb{E}[s]\text{KV}_\text{tok}}$ | $\text{KV}_\text{tok}\downarrow$ → 并发↑;$P p_w\downarrow$ 腾出更多 $M_\text{KV}$ |
| [`08`](08-scheduling.md) | 交叉点 $BW^\*=\frac{\text{KV}_\text{tok}\,C}{P}$ | **KV 量化** $\text{KV}_\text{tok}\downarrow\Rightarrow BW^\*\downarrow\Rightarrow$ **swap 更有利**;**FP8 权重** $C\uparrow\Rightarrow T_\text{recompute}\downarrow\Rightarrow$ **recompute 更有利**(两者反向) |
| [`09`](09-speculative-decoding.md) | $b^\*=\frac{\text{ridge}\cdot p}{2\gamma}$ | FP8 改 ridge($C\uparrow$)与 $p$ → 移动 $b^\*$ |

### (4) 质量代价(有损,必须实测)

经验方向:**W8A8 / FP8 通常近无损;W4(AWQ/GPTQ)小退化;INT4 KV / 更低需谨慎、退化明显**。`TODO(核实)`:**不编具体精度数字**——按你的目标模型/任务实测 perplexity / 下游 accuracy,作为 $p$ 这个"质量旋钮"的另一侧。这是量化区别于纯性能旋钮的关键:它的探索必须带一条实测的质量约束。

## 与架构建模的接口 (Modeling Interface)

- **把 $p$ 拆成 $(p_w, p_a, p_{kv})$ 三个正交旋钮、各打不同项,不要用单一 $p$**——这是建模量化最干净的分解(见 (2) 表)。
- **联动要在仿真器里串起来**:改 $p_{kv}$ 自动重算 [`01`](01-prefill-decode.md)/[`06`](06-paged-kv-cache.md)/[`08`](08-scheduling.md)/[`09`](09-speculative-decoding.md) 的下游量。量化是这套 wiki 里耦合最广的旋钮,**最适合用来验证你的成本模型有没有把这些公式正确联动**。
- **"算力 vs 带宽"再平衡**:FP8 同时 $C\uparrow(2\times)$ 与字节 $\downarrow(½)$,**把 roofline 两根轴一起推**;weight-only INT4 **只推带宽轴、不推算力轴** → 对 prefill 无益。**选哪种量化 = 看 workload 落 compute 还是 memory 侧**(回 [`01`](01-prefill-decode.md) 的判定)。
- **质量是约束,不是目标**:量化探索的目标函数应是「在精度退化 $\le\varepsilon$ 下最小化字节 / 最大化 goodput」,$\varepsilon$ 约束需实测喂入——和 [`02`](02-metrics-slo.md) 的 SLA 判定同构,但多一条质量维度。

## 延伸阅读 (References)

- 上游:[`01`](01-prefill-decode.md)(字节/算力源公式)、[`05`](05-attention-kernels.md)(FP8 attention kernel)、[`06`](06-paged-kv-cache.md)(并发)、[`08`](08-scheduling.md)(交叉点)、[`09`](09-speculative-decoding.md)($b^\*$)。
- 下游:[`15` 算例](15-quantitative-estimation.md)(代入档位算 KV / 并发 / TTFT)。
- 外部(已核实):
  - **GPTQ**:*Accurate Post-Training Quantization for Generative Pre-trained Transformers*, Frantar et al.,ICLR '23。[arXiv 2210.17323](https://arxiv.org/abs/2210.17323)
  - **AWQ**:*Activation-aware Weight Quantization*, Lin et al.,MLSys '24 Best Paper(保护 ~1% salient 通道)。[arXiv 2306.00978](https://arxiv.org/abs/2306.00978)
  - **SmoothQuant**:*Accurate and Efficient Post-Training Quantization for LLMs*, Xiao et al.,ICML '23(W8A8,迁移激活 outlier)。[arXiv 2211.10438](https://arxiv.org/abs/2211.10438)
  - FP8 格式:NVIDIA Hopper Transformer Engine(E4M3 / E5M2);KV 量化:KVQuant 等(`TODO`:补一篇 KV 量化代表作)。
