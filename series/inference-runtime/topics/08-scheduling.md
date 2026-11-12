# 08 调度:iteration 循环、准入与抢占 / Scheduling

> 状态:草稿
>
> 一句话定位:把 [`04`](04-dynamic-shape-batching.md)–[`07`](07-radix-prefix-reuse.md) 的机制串成一个**每 iteration 跑一次的控制回路**。调度器做两个决策——**准入**(从等待队列放多少进来)与**抢占**(显存不够时踢谁、怎么踢),它们共同把系统**钉在 [`02`](02-metrics-slo.md) goodput 曲线上的某个工作点**。

## 概念 (Concept)

推理引擎本质是个**控制回路**,状态有三块:**等待队列**(waiting,尚未分配 KV)、**运行集**(running,已占 KV)、**资源账本**(free KV blocks + radix tree)。每个 iteration 跑一遍:

```
loop 每个 iteration:
  1. 选本步运行集(优先续跑 running 的 decode)
  2. 准入:在 token 预算 + KV 空间 + 延迟预算内,从 waiting 拉新请求进 running
  3. 抢占:若 KV 不够续命,把部分 running 踢回 waiting/swapped,释放 block
  4. 组 batch(decode + prefill chunk 混编,见 04)
  5. 跑一次 forward(executor)
  6. 收尾:追加 token、检测 <eos>、释放完成请求、更新 radix tree(07)
```

它和 OS 进程调度器同构:**准入 ≈ 多道程序度(admission control),抢占 ≈ 换页/换出(swap),抖动 ≈ thrashing**。你熟的那套直觉直接可搬。

## 机制 (Mechanism)

### iteration 调度循环

调度粒度是**一个 iteration**(=一次 forward,[`04`](04-dynamic-shape-batching.md) continuous batching)。两个预算钳住每步:

- **token 预算** `max_num_batched_tokens`:本步 prefill chunk + decode token 总数上限(=[`04`](04-dynamic-shape-batching.md) 的 $T_\text{chunk}+b_d$),决定每步耗时上界。
- **序列预算** `max_num_seqs`:并发序列数上限。

常见策略:**先保 running 的 decode**(已投入的成本不能丢),再用剩余预算准入新 prefill。decode 优先保证了在跑请求的 ITL 稳定。

### 准入水位(admission watermark)

不能准入到把 KV 池占满——decode 还要**继续增长** KV,占满就会 iteration 中途 OOM。于是保留一个**水位**:可用 block $=(1-w)\cdot$ 池(vLLM 默认留极小一档,如 $w\sim0.01$,作防死锁缓冲)。准入由三条上界的**最小值**决定:

| 约束 | 上界 | 来源 |
|---|---|---|
| 显存 | $\sum_i s_i\,\text{KV}_\text{tok} \le M_\text{KV}\,\eta_\text{mem}(1-w)$ | [`06`](06-paged-kv-cache.md) |
| 延迟 | $b \le \dfrac{BW\cdot\text{MBU}\cdot\text{SLO}_\text{TPOT}-Pp}{s\,\text{KV}_\text{tok}}$ | [`02`](02-metrics-slo.md)+[`05`](05-attention-kernels.md) |
| token 预算 | $T_\text{chunk}+b_d \le$ `max_num_batched_tokens` | [`04`](04-dynamic-shape-batching.md) |

**这就是工作点选择**:准入太松 → 显存压力 → 抢占抖动 + TPOT 膨胀 → 违 SLO,goodput 掉头([`02`](02-metrics-slo.md));准入太紧 → 利用不足 → 吞吐低。水位 + `max_num_seqs` 是把系统推到 goodput 峰值的旋钮。

### 抢占:recompute vs swap

运行中的序列 KV 在增长,池可能耗尽 → 必须**抢占**部分 running 释放 block。被抢的请求,恢复时有两条路:

- **重算(recompute)**:直接丢弃其 KV;恢复时把它已有的 token(prompt + 已生成)当新 prompt **重跑 prefill**。代价:重做 prefill 算力 $O(s)$,**无数据搬运**;且可命中前缀缓存([`07`](07-radix-prefix-reuse.md))进一步变便宜。
- **换出(swap)**:把其 KV 从 HBM 拷到 CPU 内存(走 PCIe);恢复时再拷回。代价:**$2\times$ KV 字节过链路**(出+回),**无重算**。

这是一个**算力 vs 带宽**的经典取舍——正是体系结构要建模的东西。`TODO(确认)`:vLLM 两种都支持、常以 recompute 为默认(版本相关),你若要精确对齐某版本默认值,写 `14` 时核。

## 量化与公式 (Quantification)

新符号:$w$ 水位预留比;$BW_\text{link}$ offload 链路带宽 [byte/s];其余沿用前篇。

### (1) recompute vs swap 的交叉点(与序列长度无关!)

单次抢占恢复的代价(每被抢序列、长度 $s$):

$$T_\text{recompute} \approx \frac{2P\,s}{C}\ (\text{prefill,compute-bound}),\qquad T_\text{swap} \approx \frac{2\,s\,\text{KV}_\text{tok}}{BW_\text{link}}\ (\text{出+回})$$

两者**都 $\propto s$**,所以比值与 $s$ 无关 → **recompute/swap 的选择是个 per-模型/per-硬件常数,不是 per-请求决策**。swap 更便宜 ⟺

$$\boxed{\,BW_\text{link} > BW^\*_\text{link} = \frac{\text{KV}_\text{tok}\cdot C}{P}\,}$$

**算例(Llama-3 70B,2×H100,$C=1.979\times10^{15}$ FLOP/s,$\text{KV}_\text{tok}=320$ KiB,$P=70$e9)**:

$$BW^\*_\text{link} = \frac{327680 \times 1.979\times10^{15}}{70\times10^{9}} \approx 9.3\ \text{GB/s}$$

对照链路档(均【典型量级】):

| 链路 | 典型带宽 | vs $BW^\*\!\approx\!9.3$ GB/s | 倾向 |
|---|---|---|---|
| NVLink (H100) | ~450 GB/s/向 | ≫ | **swap** |
| PCIe Gen5 ×16 | ~64 GB/s | ≫ | **swap** |
| NVMe SSD | ~7–14 GB/s | ≈/< | **临界 / recompute** |

→ 70B 在 PCIe/NVLink 上**一阶看 swap 更省**;掉到 NVMe 档才轮到 recompute。具体数:$s{=}2000$ 时 $T_\text{recompute}\approx141$ ms、$T_\text{swap(PCIe5)}\approx20$ ms。【估算】

> **二阶修正(为什么实践常选 recompute)**:decode 是 memory-bound([`01`](01-prefill-decode.md)),GPU 的**算力本就闲着** → recompute 用的是"免费"资源;而 swap 占的 PCIe 可能与权重加载 / KV offload 争抢。再叠 [`07`](07-radix-prefix-reuse.md) 前缀命中,recompute 实际成本常低于一阶式。**结论:交叉点给方向,最终选择要把"被占资源是否空闲/争用"叠进去**——这恰是仿真器该回答的。

### (2) 抖动(thrashing)边界

准入使「续命所需 block 增长率」> 「释放率」时,系统陷入 preempt↔resume churn,有用产出塌方(同 OS thrashing)。水位 $w$ 与准入上界 (准入小节) 就是防抖动的闸。`TODO`:可用一个简单排队模型给抖动临界到达率,留到 `15` 接 workload。

## 与架构建模的接口 (Modeling Interface)

- **调度器 = 选 goodput 工作点的策略模块**:仿真器里它是 policy,队列是 state,iteration 是 event。**realized goodput 由这个策略决定**,不是由峰值硬件决定——这是 archax 必须显式建模调度而非只算 roofline 的根本原因。
- **准入水位**:把吞吐(高准入)与 SLO 达成(留 headroom)连成一条曲线的旋钮;扫它 + [`02`](02-metrics-slo.md) 的 SLO 约束即得工作点。
- **抢占交叉点 $BW^\*_\text{link}=\text{KV}_\text{tok}\,C/P$**:**直接就是"选哪一档 offload 链路"的判据**,换 HBM/NVLink/PCIe/NVMe 档复用同一式(你要的换档接口)。注意它**与 $s$ 无关、只随模型 $(P,\text{KV}_\text{tok})$ 与卡 $(C)$ 变**——量化([`10`](10-quantization.md))从两侧反向推它:**KV 量化** $\text{KV}_\text{tok}\downarrow\Rightarrow BW^\*\downarrow\Rightarrow$ 任何链路更易超过阈值 → **swap 更有利**(要搬的 KV 更少);**FP8 权重量化** $C\uparrow\Rightarrow T_\text{recompute}\downarrow\Rightarrow$ **recompute 更有利**。
- **调度开销是硬约束**:每 iteration 的调度决策(CPU)必须 $\ll$ 一个 GPU step($\sim$ms)。仿真器把它建成**每 iteration 固定成本**;超过 step 时间 → GPU 出气泡。这对 decode(步极短)尤其紧,是"异步调度 / 调度与执行重叠"这类优化的动机。
- **与 PD 分离的关系**:本篇是**单池**调度;[`12`](12-pd-disaggregation.md) 把 prefill/decode 拆成两个池后,准入/抢占要跨池协同(prefill 完成后 KV 怎么交给 decode 池),交叉点公式里的 $BW_\text{link}$ 就变成**池间链路**带宽。

## 延伸阅读 (References)

- 上游:[`02` 指标](02-metrics-slo.md)(准入的延迟上界、goodput)、[`04`](04-dynamic-shape-batching.md)(token 预算、iteration 粒度)、[`05`](05-attention-kernels.md)(MBU)、[`06`](06-paged-kv-cache.md)(block 池、$\eta_\text{mem}$)、[`07`](07-radix-prefix-reuse.md)(cache-aware 调度、recompute 命中)。
- 下游:[`10` 量化](10-quantization.md)(压 $\text{KV}_\text{tok}$ 移动交叉点)、[`12` PD 分离](12-pd-disaggregation.md)(跨池调度)、[`15` 算例](15-quantitative-estimation.md)(代入 workload)。
- 外部:vLLM scheduler(`max_num_batched_tokens` / `max_num_seqs` / 水位、recompute vs swap 抢占)与 Sarathi-Serve(stall-free 调度,[`04`](04-dynamic-shape-batching.md) 已引)的调度策略;Orca iteration-level scheduling([`04`](04-dynamic-shape-batching.md) 已引)。`TODO(核实)`:对某一具体 vLLM 版本核准入默认值与默认抢占模式,留到 `14`。
