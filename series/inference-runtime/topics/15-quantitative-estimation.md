# 15 量化估算算例:Llama-3 70B on H100 / Worked Example

> 状态:草稿
>
> 一句话定位:把 [`01`](01-prefill-decode.md)–[`14`](14-framework-comparison.md) 的公式全部代入**具体型号**,端到端推 KV/token → 最大并发 → TPOT/ITL → TTFT → 吞吐 → goodput 工作点,作为成本模型的**黄金样例**。每个数字都标出处篇与性质(精确 / 假设)。**把这页当模板:换型号只改常数,公式不动。**

## 0. 配置与常数(Setup)

**模型 Llama-3 70B**【精确,[`01`](01-prefill-decode.md)】:$L=80,\ h=64,\ h_{kv}=8,\ d_h=128,\ d=8192,\ P=70\text{e}9$。
**硬件 H100 SXM80**【精确,[`01`](01-prefill-decode.md)】:单卡 $C_\text{bf16}=989.5$ TFLOP/s(稠密)、$C_\text{fp8}=1979$ TFLOP/s、$BW=3.35$ TB/s、HBM $=80$ GB、132 SM、NVLink ~450 GB/s。

**两个配置对照**(展示量化的杠杆,[`10`](10-quantization.md)/[`11`](11-cluster-parallelism.md)):

| | 配置 A(基线) | 配置 B(量化) |
|---|---|---|
| 精度 | FP16($p_w{=}p_{kv}{=}2$) | FP8($p_w{=}p_{kv}{=}1$) |
| 并行 | TP=4,**4×H100** | TP=2,**2×H100** |
| 聚合 $C$ | $4{\times}989.5=3958$ TFLOP/s | $2{\times}1979=3958$ TFLOP/s |
| 聚合 $BW$ | $4{\times}3.35=13.4$ TB/s | $2{\times}3.35=6.7$ TB/s |
| 聚合 HBM | 320 GB | 160 GB |

**效率因子(假设值,需你实测替换)**【假设】:$\eta_\text{mem}=0.96$([`06`](06-paged-kv-cache.md))、显存利用率 util$=0.9$、decode MBU$=0.7$([`05`](05-attention-kernels.md))、prefill MFU$=0.5$。**结构性数字精确,这四个是软输入——成本模型的不确定性主要在这里。**

> 以下主线用**配置 A**,§6 切到配置 B 看量化收益。TP 通信项([`11`](11-cluster-parallelism.md))此处略去(TP=4、NVLink 下每步 $\lesssim$ 0.2 ms),精算时叠加。

## 1. KV/token([`01`](01-prefill-decode.md))

$$\text{KV}_\text{tok}=2\,L\,h_{kv}\,d_h\,p_{kv}=2\cdot80\cdot8\cdot128\cdot2=327{,}680\text{ B}=\boxed{320\text{ KiB/token}}\ \text{【精确】}$$

一条 $s=4096$ 的请求:$4096\times320\text{ KiB}=1.342$ GB 的 KV。

## 2. 显存 → 最大并发([`06`](06-paged-kv-cache.md)/[`08`](08-scheduling.md))

- 权重 $=P\,p_w=70\text{e}9\times2=140$ GB(TP=4,每卡 35 GB)。
- 可用 $=\text{util}\times\text{HBM}=0.9\times320=288$ GB;留 ~8 GB 激活/上下文开销 → **KV 池 $M_\text{KV}\approx288-140-8=140$ GB**。
- 取平均上下文 $\mathbb{E}[s]=4096$:

$$\text{max\_conc}=\frac{M_\text{KV}\cdot\eta_\text{mem}}{\mathbb{E}[s]\cdot\text{KV}_\text{tok}}=\frac{140\times0.96}{1.342}\approx\boxed{100\ \text{并发请求}}$$

## 3. TPOT / ITL vs batch([`01`](01-prefill-decode.md)/[`05`](05-attention-kernels.md))

decode 每步聚合 HBM $=P\,p_w+b\,s\,\text{KV}_\text{tok}$,实测除以 MBU:

$$\text{TPOT}(b)=\frac{P\,p_w+b\,s\,\text{KV}_\text{tok}}{BW_\text{agg}\cdot\text{MBU}}=\frac{(140+1.342\,b)\text{e9}}{13.4\text{e}12\times0.7}$$

| $b$ | 权重项 | KV 项 | TPOT |
|---|---|---|---|
| 1 | 140 GB | 1.3 GB | **14.9 ms** |
| 32 | 140 | 42.9 | **19.5 ms** |
| 100(满并发) | 140 | 134.2 | **29.2 ms** |

注意 $b{=}1$ 时权重项独占($\frac{140\text{e}9}{9.38\text{e}12}=14.9$ ms),印证 [`01`](01-prefill-decode.md):**低 batch decode 被权重带宽锁死**,加 batch 几乎免费(到 $b{=}100$ 才把 TPOT 抬到 ~2×)。

## 4. TTFT([`01`](01-prefill-decode.md)/[`02`](02-metrics-slo.md))

prefill compute-bound,$s_p=3500$:

$$T_\text{prefill}=\frac{2\,P\,s_p}{C_\text{agg}\cdot\text{MFU}}=\frac{2\times70\text{e}9\times3500}{3958\text{e}12\times0.5}=\frac{4.9\text{e}14}{1.979\text{e}15}\approx\boxed{248\text{ ms}}$$

$\text{TTFT}=T_\text{queue}+T_\text{prefill}$;空载 ~248 ms。前缀命中([`07`](07-radix-prefix-reuse.md))则按未命中 suffix 重算,可降一个量级。

## 5. 吞吐与 goodput 工作点([`02`](02-metrics-slo.md)/[`08`](08-scheduling.md))

满并发 $b=100$、TPOT$=29.2$ ms:

$$\text{系统吞吐}=\frac{b}{\text{TPOT}}=\frac{100}{0.0292}\approx 3425\ \text{tok/s},\quad \frac{}{\text{GPU}}\approx856,\quad \frac{}{\text{user}}=\frac{1}{0.0292}\approx 34\ \text{tok/s}$$

**哪个约束在绑?** 设 SLO:TTFT$_\text{p99}\le2$ s、TPOT$_\text{p99}\le40$ ms。
- 延迟侧上界([`02`](02-metrics-slo.md)):$b\le\frac{BW\cdot\text{MBU}\cdot\text{SLO}_\text{TPOT}-P p_w}{s\,\text{KV}_\text{tok}}=\frac{(13.4\text{e}12\cdot0.7\cdot0.04-140\text{e}9)}{1.342\text{e}9}\approx 175$。
- 显存侧上界(§2):$b\le 100$。
- **取 min → 显存绑(100 < 175)**:此上下文长度下**瓶颈是显存不是延迟**,工作点 $b\approx100$、TPOT 29 ms(< 40 ms SLO ✓)、TTFT 248 ms(✓)。→ 想提吞吐应先扩 KV 池(量化 / 更多卡),而非松延迟。

## 6. 旋钮敏感度(Sweeps)

### (a) 上下文翻 4 倍 → 显存绑、吞吐崩(KV 主导,[`01`](01-prefill-decode.md))

$s=16384$:KV/req $=16384\times320\text{ KiB}=5.37$ GB → max_conc $=\frac{140\times0.96}{5.37}\approx\boxed{25}$。吞吐 $\approx25/0.029\approx856$ tok/s,**仅 4k 场景的 1/4**。长上下文把并发(进而吞吐)按 $1/s$ 砍——这是 KV-bound 区([`01`](01-prefill-decode.md))的代价。

### (b) FP8 量化 → 砍一半 GPU(配置 B,[`10`](10-quantization.md))

| 量 | A:FP16 / 4×H100 | B:FP8 / 2×H100 |
|---|---|---|
| 权重 | 140 GB | 70 GB |
| $\text{KV}_\text{tok}$ | 320 KiB | 160 KiB |
| $M_\text{KV}$ | 140 GB | $144-70-4\approx70$ GB |
| max_conc @4k | 100 | $\frac{70\times0.96}{0.671}\approx100$ |
| TPOT @满并发 | 29.2 ms | $\frac{(70+67.1)\text{e}9}{6.7\text{e}12\cdot0.7}=29.2$ ms |
| TTFT | 248 ms | 248 ms($C_\text{fp8}$ 补回算力) |
| **吞吐 / GPU** | **856** | **1712** |

**同样的并发 / TPOT / TTFT,GPU 数减半 → 吞吐/GPU 翻倍、每 query 成本减半。** 这就是 [`10`](10-quantization.md) 「$p$ 牵一发」在终点的兑现(代价:FP8 的质量退化需实测,[`10`](10-quantization.md) §4)。

## 汇总表(配置 A,Llama-3 70B / 4×H100 / FP16 / s≈4k)

| 量 | 值 | 出处 | 性质 |
|---|---|---|---|
| KV/token | 320 KiB | [`01`](01-prefill-decode.md) | 精确 |
| 权重 | 140 GB | [`01`](01-prefill-decode.md) | 精确 |
| 最大并发 @4k | ~100 | [`06`](06-paged-kv-cache.md) | 含假设 $\eta_\text{mem}$ |
| TPOT @b=100 | ~29 ms | [`01`](01-prefill-decode.md)/[`05`](05-attention-kernels.md) | 含假设 MBU |
| TTFT @3.5k prompt | ~248 ms | [`01`](01-prefill-decode.md) | 含假设 MFU |
| 系统吞吐 | ~3400 tok/s | [`02`](02-metrics-slo.md) | — |
| 绑定约束 @4k | 显存 | [`08`](08-scheduling.md) | — |

## 与架构建模的接口 (Modeling Interface)

- **这整页就是成本模型的骨架**:输入 = {模型常数 $(L,h_{kv},d_h,P)$、硬件 $(C,BW,\text{HBM})$、精度 $(p_w,p_{kv},p_a)$、并行 $(N_{tp},\dots)$、效率 $(\eta_\text{mem},\text{MBU},\text{MFU})$、workload $(\mathbb{E}[s],s_p,N_\text{out},h)$、SLO}; 输出 = {并发, TPOT, TTFT, 吞吐, goodput, 绑定约束}。
- **依赖链(改一个常数,沿链重算)**:$p_{kv}\to\text{KV}_\text{tok}\to\{$并发, TPOT, KV 传输$\}$;$p_w\to$ 权重 $\to\{$并发, TPOT, 装卡$\}$;$p_a\to C\to$ TTFT;$N_{tp}\to\{C,BW,\text{HBM}\}_\text{agg}+$ 通信。**这正是 [`10`](10-quantization.md) 说的"用量化验证联动正确性"的落点。**
- **三个软因子是不确定性主源**:$\eta_\text{mem}$(分页实现)、MBU(kernel/占用,[`05`](05-attention-kernels.md))、MFU(prefill kernel)。建议你的工具把它们建成**可标定参数**,用一两个实测点反推,而非拍死——结构公式是硬的,这三个是要 fit 的。
- **绑定约束随 workload 切换**:短上下文 → 显存绑(扩 KV 池有效);长上下文 → 仍显存绑但更紧;高 QPS 短输出 → 可能延迟/排队绑。**架构探索的核心产物是"在 $(\mathbb{E}[s],\text{QPS},\text{SLO})$ 空间里,哪个资源先绑"的相图**——本页给的是其中一个点,扫成面就是你要的 design space。
- **goodput 是目标函数**([`02`](02-metrics-slo.md)/[`12`](12-pd-disaggregation.md)):把本页的吞吐用 SLO 通过率筛一遍,在 $(b,\text{量化档},N_{tp},\text{PD 配比})$ 上最大化 per-GPU goodput,就是选型/架构决策。

## 延伸阅读 (References)

- 本页代入了:[`01`](01-prefill-decode.md)(KV/算力/带宽)、[`02`](02-metrics-slo.md)(SLO/吞吐口径)、[`05`](05-attention-kernels.md)(MBU)、[`06`](06-paged-kv-cache.md)($\eta_\text{mem}$/并发)、[`08`](08-scheduling.md)(绑定约束)、[`10`](10-quantization.md)(量化档)、[`11`](11-cluster-parallelism.md)(TP 聚合/通信)、[`12`](12-pd-disaggregation.md)(goodput)。
- `TODO(核实)`:三个软因子($\eta_\text{mem}$/MBU/MFU)与 FP8 质量退化按你的目标栈实测;TP 通信项若精算需补 [`11`](11-cluster-parallelism.md) 的 latency 项;投机解码([`09`](09-speculative-decoding.md))的 $\alpha$ 若有实测可加一档"投机后 TPOT"。
