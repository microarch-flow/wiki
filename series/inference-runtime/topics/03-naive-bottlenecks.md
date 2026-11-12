# 03 朴素实现的瓶颈 / Bottlenecks of a Naive Engine

> 状态:草稿
>
> 一句话定位:把一个"能跑但没优化"的推理引擎拆出三处系统性浪费——**KV 显存碎片、静态批的尾部浪费、prefill/decode 互相干扰**。每处都落成一个 < 1 的效率乘子或一个延迟惩罚项,正好对应后面 `04`–`08`、`12` 的解法。

## 概念 (Concept)

一个"朴素引擎"= 把训练那套搬来做推理:**每请求预留一块定长 KV 缓冲、整批一起跑到全部结束、prefill 和 decode 不加区分塞进同一个 batch**。它能出正确结果,但把 [`02`](02-metrics-slo.md) 的 [goodput](../glossary.md#goodput) 漏掉一大半。三处浪费的根源都在 [`01`](01-prefill-decode.md):

| 浪费 | 物理根源(来自 `01`) | 表现 | 解法(后续篇) |
|---|---|---|---|
| KV 显存碎片 | KV 字节随 $s$ 增长、**输出长度事先未知** | 显存装不下本可容纳的并发 | [`06` PagedAttention](06-paged-kv-cache.md) |
| 静态批尾部浪费 | decode [memory-bound](../glossary.md#memory-bound)、**长度异质** | 短请求陪长请求空转 | [`04` continuous batching](04-dynamic-shape-batching.md) |
| prefill/decode 干扰 | 一个 [compute-bound](../glossary.md#compute-bound)、一个 memory-bound | prefill 一来 decode 卡顿,ITL 尾爆 | [`04` chunked prefill](04-dynamic-shape-batching.md) / [`12` PD 分离](12-pd-disaggregation.md) |

下面逐个量化。

## 机制 (Mechanism)

### 瓶颈 1:KV 显存碎片

朴素做法:请求进来时,按**最大可能长度** $s_\max$(模型上下文上限或配置的 `max_model_len`)预留一整块**连续** KV 缓冲。原因是输出长度 $N_\text{out}$ 事先不知道,为避免中途搬迁,只能按最坏情况一次性占好。后果三种碎片叠加:

- **内部碎片(internal fragmentation)**:预留 $s_\max$ 但实际只用到 $s_\text{actual}=s_p+N_\text{out}$,中间一大段预留而未用。
- **外部碎片(external fragmentation)**:变长的连续块反复分配/释放,在显存里留下大小不一、装不下新请求的"洞"——即使空闲总量够。
- **过度预留(over-reservation)**:按 $s_\max$ 占坑,直接把可并发数砍到远低于显存本可支撑的水平。

> 这正是 [PagedAttention](../glossary.md#paged-attention)(`06`)要解决的:像 OS 虚存分页一样,把 KV 切成定长 block 按需分配,**只在最后一个未满 block 里残留 ≤ block 大小的内部碎片,外部碎片归零**。

### 瓶颈 2:静态批处理的尾部浪费

朴素批处理:凑齐 $b$ 个请求组成一个 batch,**一起跑到 batch 内全部完成**才释放、才接新请求。但输出长度异质——短请求早早生成完 `<eos>`,它的 slot 却被占着(padding 或空算)直到 batch 里**最长**那条结束。两层损失:

1. **算力/带宽空转**:已完成的 slot 仍参与每步计算或占着 KV。
2. **队头阻塞(head-of-line blocking)**:新请求要等整批排空才能进 → 排队时延 ↑ → TTFT ↑。

> 解法是 [continuous batching](../glossary.md#continuous-batching)(`04`):调度粒度从"一整批"降到"一个 iteration",完成即出、空位即补,把尾部浪费抹平。

### 瓶颈 3:prefill / decode 互相干扰

朴素引擎把 prefill 和 decode 的 token 混进同一个 forward batch。但两者资源画像相反([`01`](01-prefill-decode.md)):prefill 是一次**长 compute 突发**(并行处理 $s_p$ 个 token),decode 要的是**高频小步**、对延迟敏感。混在一起两败俱伤:

- 一个大 prefill 进来,**正在进行的所有 decode 被它顶住** → 该步 ITL 突然拉长一个数量级 → [ITL](../glossary.md#itl) 的 p99(用户感知的"结巴")炸掉。
- 反过来,decode token 挤占 batch,prefill 也吃不满算力。

> 解法两条:[chunked prefill](../glossary.md#chunked-prefill)(`04`)把长 prefill 切片、与 decode 交错,封顶单次卡顿;[PD 分离](../glossary.md#pd-disaggregation)(`12`)干脆把两阶段放到不同硬件池,从物理上解耦。

## 量化与公式 (Quantification)

新符号:$s_\max$ 预留长度上限 [token];$s_\text{actual}$ 实际用到长度 [token];$\eta_\text{mem},\eta_\text{batch}\in(0,1]$ 两个效率乘子。其余沿用 [`01`](01-prefill-decode.md)/[`02`](02-metrics-slo.md)。

### (1) 碎片 → 显存利用率乘子 $\eta_\text{mem}$

朴素按 $s_\max$ 预留,有效 KV 利用率:

$$\eta_\text{mem} = \frac{\mathbb{E}[s_\text{actual}]}{s_\max},\qquad \text{并发上限} = \eta_\text{mem}\cdot\frac{M_\text{KV}}{s_\max\,\text{KV}_\text{tok}}\Big/\!\!\ldots = \frac{M_\text{KV}}{\mathbb{E}[s_\text{actual}]\,\text{KV}_\text{tok}}\cdot\eta_\text{mem}$$

更直接地:**朴素并发** $=\dfrac{M_\text{KV}}{s_\max\,\text{KV}_\text{tok}}$,**理想并发** $=\dfrac{M_\text{KV}}{\mathbb{E}[s_\text{actual}]\,\text{KV}_\text{tok}}$,比值就是 $\eta_\text{mem}$($M_\text{KV}$ = 留给 KV 的显存)。

**算例**:$s_\max=8192$、平均实际 $\mathbb{E}[s_\text{actual}]=1500$ → $\eta_\text{mem}\approx 18\%$,即朴素预留方式把可并发数砍到理想的不到五分之一。叠加外部碎片更低。论文报告既有系统 KV 显存浪费可达 **60–80%**【典型量级,PagedAttention/vLLM 论文报告值,TODO(核实):取 Kwon et al. SOSP'23 原文确认该区间与定义】。

### (2) 尾部浪费 → batch 效率乘子 $\eta_\text{batch}$

一个静态批,长度 $\{L_1,\dots,L_b\}$,要跑 $\max_i L_i$ 步才整批结束。有用的 token·step 是 $\sum_i L_i$,总占用是 $b\cdot\max_i L_i$:

$$\eta_\text{batch} = \frac{\sum_i L_i}{b\cdot\max_i L_i} = \frac{\overline{L}}{\max_i L_i}$$

**算例**:$b=8$,长度分布使 $\overline{L}=200$、$\max=1000$(长尾常见)→ $\eta_\text{batch}=20\%$,即 **80% 的 decode slot·step 在陪跑**。分布越长尾,$\overline{L}/\max$ 越小,浪费越狠。【示意,数字示长尾效应;真实分布取你的 workload trace】

### (3) prefill 干扰 → ITL 尾部惩罚

一个 $s_p$ 的 prefill 占用算力时间 $T_\text{prefill}\approx 2P s_p/C$;它执行期间并发 decode 全部停摆,本步 ITL 被抬到 $\approx T_\text{prefill}$。

**算例(2×H100 跑 70B)**:$s_p=4096$,FLOP $=2\times70\text{e}9\times4096\approx 5.7\times10^{14}$;2×H100 稠密 BF16 聚合 $\approx 1.98\times10^{15}$ FLOP/s,按 [MFU](../glossary.md#mfu) 0.5 取 $\approx 1\times10^{15}$ 有效 → $T_\text{prefill}\approx 0.57$ s。一条本想要 25 ms ITL 的 decode,撞上这次 prefill 就是 **~570 ms 的一次卡顿,p99 ITL 直接 ×20+**。【估算,MFU 取 0.5;`15` 用你的实测 MFU 复算】

### 三乘子合一:为什么朴素 goodput 只剩零头

朴素有效 goodput $\approx$ 理想 $\times\,\eta_\text{mem}\times\eta_\text{batch}\times(\text{SLO 通过率})$。上面算例随手就是 $0.18\times0.20\approx 3.6\%$ 的"双杀",再叠 prefill 干扰把 SLO 通过率打下去——**这就是为什么"能跑"和"能商用"之间隔着整个 `04`–`12`**。

## 与架构建模的接口 (Modeling Interface)

- **把三处浪费建成成本模型里的显式乘子/惩罚项**,而非黑盒:
  | 浪费 | 建模量 | 被哪个旋钮消除 |
  |---|---|---|
  | KV 碎片 | $\eta_\text{mem}$ 乘到 KV 容量 → 并发上限 | block 大小、分页(`06`) |
  | 尾部 | $\eta_\text{batch}$ 乘到 decode 吞吐 | 调度粒度(`04`/`08`) |
  | 干扰 | ITL 尾部 $+T_\text{prefill}$ 惩罚 | chunk 大小(`04`)、PD 切分(`12`) |
- **可扫设计参数**:block 大小(碎片 vs 寻址开销的折中)、chunk 大小(干扰 vs prefill 吞吐)、调度水位——这三个旋钮分别把上面三个乘子从朴素值推向 1,是架构探索的主战场。
- **喂给仿真器**:$\eta_\text{mem},\eta_\text{batch}$ 让仿真器从"理论 roofline 吞吐"过渡到"可实现 goodput";prefill 干扰项决定要不要在体系结构上隔离两阶段(共享 die vs 分池),正是 `12` 的取舍依据。
- **基线意义**:本篇的朴素值是架构探索的**对照组**——后面每个机制的收益,都应表达为"把某个 $\eta$ 提高了多少"或"砍掉了多少 ITL 尾",这样收益可叠加、可归因。

## 延伸阅读 (References)

- 上游:[`01` 推理基础](01-prefill-decode.md)(KV 字节、memory-bound)、[`02` 指标](02-metrics-slo.md)(goodput、ITL p99)。
- 解法下游:[`04` 变长与 continuous batching](04-dynamic-shape-batching.md)、[`06` PagedAttention](06-paged-kv-cache.md)、[`08` 调度](08-scheduling.md)、[`12` PD 分离](12-pd-disaggregation.md)。
- 外部(待核实):PagedAttention / vLLM(Kwon et al., *Efficient Memory Management for LLM Serving with PagedAttention*, SOSP '23)——碎片浪费 60–80%、连续批处理收益的原始数据;Orca(Yu et al., OSDI '22)——iteration-level scheduling(连续批处理)的提出。`TODO(核实)`:核对 vLLM 论文中"浪费 60–80%"的精确口径与 Orca 的吞吐提升倍数,留到写 `06`/`04` 时一并查证。
