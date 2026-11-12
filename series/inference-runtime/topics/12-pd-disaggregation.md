# 12 PD 分离 + KV 传输 / 分层存储 / Prefill-Decode Disaggregation

> 状态:草稿
>
> 一句话定位:把 prefill 和 decode 拆成**两个独立池**,各用各的并行配置、各自扩缩、甚至各用各的硬件;消除 [`03`](03-naive-bottlenecks.md) 的干扰、解开 [`11`](11-cluster-parallelism.md) 的「两阶段非对称」折中。代价是 **KV 过链路**——这是你「换一档链路带宽就复用同一公式」接口的**总用武之地**。本篇坐实 [`02`](02-metrics-slo.md) 的 goodput 定义。

## 概念 (Concept)

两条线索汇到这里:[`11`](11-cluster-parallelism.md) 说 prefill 要算力/大 TP、decode 要带宽/省通信,**单池只能折中**;[`03`](03-naive-bottlenecks.md) 说同池里 prefill 突发会顶停 decode(干扰)。**PD 分离**(DistServe)一刀解决:物理拆成 **prefill 池**(算 KV)和 **decode 池**(生成),prefill 算完把 KV **过链路**交给 decode 池。

三个收益 + 一个新成本:

- ✅ 两池**各自独立**配并行/batch/硬件型号、独立扩缩;
- ✅ **无干扰** → ITL 稳([`03`](03-naive-bottlenecks.md) 瓶颈 3 消失);
- ✅ 各池**按自己的瓶颈**优化(TTFT vs TPOT 解耦);
- ❌ 新成本:**KV 从 prefill 节点传到 decode 节点**。

## 机制 (Mechanism)

### 两池分工(SLO 解耦)

- **prefill 池**:收请求 → 算全 prompt 的 KV → 优化 **TTFT**(compute-bound),可用更高 TP、更大 token batch + chunked prefill([`04`](04-dynamic-shape-batching.md))。
- **decode 池**:收 KV → 跑自回归 decode loop → 优化 **TPOT**(bandwidth-bound),可用不同 TP、大 batch 拉吞吐。
- [`02`](02-metrics-slo.md) 的两个 SLO **分别落到两池**:TTFT 约束归 prefill 池、TPOT 约束归 decode 池——各自独立达标,不再互相拖累。

### KV 传输

prefill 完成后,把该请求的 KV($L$ 层 × $s_p$ token × $\text{KV}_\text{tok}$)传给指定 decode worker。两个关键优化:

- **layer-wise 流式**:算完一层就传该层 KV,与后续层计算**重叠** → 隐藏大部分传输延迟(Mooncake「continuously stream output KVCache」)。
- **前缀复用免传**:若 decode 池已缓存该前缀 KV([`07`](07-radix-prefix-reuse.md)),则不必传(Mooncake 先「transfer as much reusable KVCache as possible」)。

### KV offload / 分层存储

KV 不只活在 HBM,而是一条层级:**HBM(热,活跃 decode)→ CPU DRAM → SSD/NVMe(冷,暂停的请求 / 缓存的前缀)**。Mooncake 的 **KVCache-centric** 设计把集群里闲置的 CPU/DRAM/SSD/RDMA **池成一个 disaggregated KV 池**,prefill/decode 共享;全局调度器 **Conductor** 按 KV 分布 + 负载派发请求,必要时复制/swap block。**链路档(HBM ↔ NVLink ↔ PCIe/RDMA ↔ NVMe)决定什么值得放哪一层**——正是你要的换档接口。

## 量化与公式 (Quantification)

新符号:$BW_\text{link}$ 池间链路带宽 [byte/s];$h$ 前缀命中率([`07`](07-radix-prefix-reuse.md))。

### (1) KV 传输成本(复用 [`01`](01-prefill-decode.md)/[`08`](08-scheduling.md) 的带宽式)

$$T_\text{xfer} = \frac{s_p\cdot\text{KV}_\text{tok}}{BW_\text{link}}\quad(\text{单向,prefill}\to\text{decode})$$

**算例(70B,$s_p=2000$,$\text{KV}_\text{tok}=320$ KiB → KV $\approx 625$ MB)**:

| 链路 | $BW_\text{link}$ | $T_\text{xfer}$ |
|---|---|---|
| NVLink | ~450 GB/s | ~1.4 ms |
| PCIe Gen5 | ~64 GB/s | ~9.8 ms |
| RDMA/IB(400 Gb) | ~50 GB/s | ~13 ms |
| FP8 KV(÷2) | — | 各 ÷2 |

【估算,理想带宽】约束两条:(a) $T_\text{xfer}$ 摊到 $N_\text{out}$ 个 decode 步**几乎可忽略**($N_\text{out}\cdot\text{TPOT}\gg T_\text{xfer}$);(b) layer-wise 流式后大部分被 prefill 计算掩盖,**不进 TTFT 关键路径**。注意这就是 [`01`](01-prefill-decode.md) (3) / [`08`](08-scheduling.md) 交叉点 / [`10`](10-quantization.md) KV 量化用的**同一个 $s\cdot\text{KV}_\text{tok}/BW_\text{link}$**,只是 $BW_\text{link}$ 换成池间档位。

### (2) 何时值得分离

$$\text{净收益} = \underbrace{\text{省掉的干扰(ITL 尾)}}_{\text{03}} + \underbrace{\text{两池各自优化的 goodput 增益}}_{\text{11}} - \underbrace{(T_\text{xfer}\text{ 摊薄} + \text{调度复杂度} + \text{资源碎片})}_{\text{成本}}$$

低负载 / 短输出:传输摊不开、收益小;**高负载 / 长输出 + 严 SLO:分离大赢**(DistServe 报告 **7.4× 请求** 或 **12.6× 更紧 SLO**,>90% 请求满足延迟约束)。【论文报告值】

### (3) goodput(坐实 [`02`](02-metrics-slo.md))

DistServe 的精确定义:**per-GPU goodput = 在满足 SLO 达成率(如 90%)前提下,每张 GPU 能服务的最大请求率**;**越高 ⇔ 每 query 成本越低**。分离让 TTFT / TPOT 两约束在两池**独立逼近各自上限**,这就是 [`02`](02-metrics-slo.md) 说的「goodput 才是架构探索的目标函数」在系统层的兑现。

### (4) 分层 KV 的取舍

每层是一个(容量,带宽,$)三元组。一个前缀**值得放在层 $T$** ⟺ 复用概率 × 省下的重算/重取 > 该层成本。[`08`](08-scheduling.md) 的 recompute-vs-swap 在此**推广**:swap 的目标变成"传到哪一层",交叉点 $BW^\*=\text{KV}_\text{tok}\,C/P$ **选层**(比 $BW^\*$ 快的层 swap、慢的层 recompute);[`07`](07-radix-prefix-reuse.md) 的 radix LRU **跨层 spill**。

## 与架构建模的接口 (Modeling Interface)

- **PD 配比 $N_\text{prefill}:N_\text{decode}$ 是顶层旋钮**:按 workload 的 **prefill 算力需求($\sum s_p$)vs decode 带宽需求($\sum s\cdot N_\text{out}$)** 定——用 [`11`](11-cluster-parallelism.md) 的 per-phase 表分别给两池估算,配比 ≈ 两需求之比。这是把"两阶段非对称"变成一个可解的资源分配问题。
- **$BW_\text{link}$ 是可扫 fabric 参数,且本篇所有公式共用它**:KV 传输 (1)、swap 目标 (4)、分层选择全是 $s\cdot\text{KV}_\text{tok}/BW_\text{link}$——**换一个 $BW_\text{link}$ 数,这些量同时更新**。这就是你要的「换档复用」接口在一处的集中兑现;[`10`](10-quantization.md) 的 $p_{kv}$ 减半则同时砍掉所有这些传输。
- **前缀复用免传**:命中率 $h$ 下实际传输量 $\times(1-h)$ → decode 池的前缀缓存命中率直接决定 PD 链路压力。建模时 [`07`](07-radix-prefix-reuse.md) 的 $h$ 与本篇的 $BW_\text{link}$ 联合定 fabric 规格。
- **分层 KV 把"显存墙"软化成"带宽–容量–成本"连续谱**:archax 可把 KV 池建成多级(各级容量/BW/$),用 [`08`](08-scheduling.md) 的交叉点逐级判 recompute vs fetch——**把单卡显存上限扩展成集群级 KV 经济学**,这是 PD 分离对你工具最有价值的建模对象。
- **异构机会(推理独有)**:两池可用**不同卡**——prefill 用算力强的、decode 用带宽/显存大的。训练做不到(同构同步),这是推理侧专属的 design space,值得在 archax 里显式建成"按阶段选 SKU"。

## 延伸阅读 (References)

- 上游:[`11`](11-cluster-parallelism.md)(两阶段非对称、并行重映射)、[`03`](03-naive-bottlenecks.md)(干扰)、[`02`](02-metrics-slo.md)(goodput/SLO)、[`01`](01-prefill-decode.md)(带宽式)、[`07`](07-radix-prefix-reuse.md)(前缀免传)、[`08`](08-scheduling.md)(recompute vs swap)、[`10`](10-quantization.md)($p_{kv}$)。
- 下游:[`14` 框架对比](14-framework-comparison.md)(各框架对 PD 的支持)。
- 外部(已核实):
  - **DistServe**:*Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving*, Zhong et al., OSDI '24——per-GPU goodput 定义、7.4× 请求 / 12.6× 紧 SLO。[arXiv 2401.09670](https://arxiv.org/abs/2401.09670)
  - **Mooncake**:*A KVCache-centric Disaggregated Architecture for LLM Serving*, Qin et al., FAST '25(Kimi)——分层 DRAM/SSD KV 池 + Conductor 全局调度 + layer-wise 流式传输。[arXiv 2407.00079](https://arxiv.org/abs/2407.00079)
  - **Splitwise**(Microsoft,2024)——混合池 + 两级调度,作对比。
