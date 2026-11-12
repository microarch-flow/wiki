# 11 集群并行:TP / PP / EP / Cluster Parallelism

> 状态:草稿
>
> 一句话定位:模型放不进一张卡时怎么切。三种切法(TP 切层内、PP 切层间、EP 切专家)各有**不同的通信模式与链路要求**,且**推理的两阶段非对称**让它们的取舍与训练截然不同——这正是 [`12`](12-pd-disaggregation.md) PD 分离的动机。

## 概念 (Concept)

Llama-3 70B FP16 权重 140 GB > 80 GB([`01`](01-prefill-decode.md))→ 单卡装不下,必须切。三个正交维度:

| 维度 | 切什么 | 通信模式 | 链路要求 | 主要换来 |
|---|---|---|---|---|
| **[TP](glossary.md#tp)** 张量并行 | 每层权重(层**内**) | 每层 2 次 all-reduce(同步、在关键路径) | **必须 NVLink**(节点内) | ↓延迟、↓单卡显存 |
| **[PP](glossary.md#pp)** 流水线并行 | 层(层**间**分 stage) | 仅相邻 stage 点对点(小) | 容忍慢链路(跨节点) | ↑容量/吞吐 |
| **[EP](glossary.md#ep)** 专家并行 | MoE 的专家 | 每 MoE 层 2 次 all-to-all | 中高(routing 流量) | 服务超大 MoE |

实际是三者 + 数据并行(DP,整模型复制)的**组合**:总卡数 $=N_{tp}\cdot N_{pp}\cdot N_{ep}\cdot N_{dp}$。

## 机制 (Mechanism)

### TP(张量并行,Megatron 式)

把每层的权重矩阵按维度切到 $N_{tp}$ 卡:

- **注意力**:按 head 切(每卡 $h/N_{tp}$ 个 query head)→ **KV 也随 head 切**,每卡 KV $=\text{KV}_\text{tot}/N_{tp}$。
- **FFN**:up/gate 列并行、down 行并行。Megatron 的精妙在于**列并行接行并行**,使前向**每层只需 2 次 all-reduce**(注意力后 1 次、FFN 后 1 次)。

all-reduce 同步、在**每一层的关键路径上** → 必须 NVLink;跨节点做 TP 会让延迟崩。受 head 数限制 $N_{tp}\le h$,且通信随 $N_{tp}$ 涨,故通常 $N_{tp}\le 8$(节点内)。

### PP(流水线并行)

把 $L$ 层按 stage 切到 $N_{pp}$ 卡(stage1 = 层 1..k,…)。stage 间只传一次激活 $[b,s,d]$(**点对点、小**,非 all-reduce)→ 可走慢链路、跨节点。代价是**流水线气泡(bubble)**:用 $m$ 个 micro-batch 填,气泡占比 $\frac{N_{pp}-1}{m+N_{pp}-1}$。**PP 提吞吐/容量,不降单请求延迟**(一个请求仍要串行穿过所有 stage)。

### EP(专家并行,MoE)

MoE 每层有 $E$ 个专家,每 token 路由到 top-$k$ 个。EP 把不同专家放不同卡,token 经 **all-to-all** 派发到持有其专家的卡、算完再 all-to-all 合回(每 MoE 层 2 次)。

- 痛点:**负载不均**(热门专家拖尾)、all-to-all 延迟 → 用 capacity factor 封顶。
- 推理特性:**每 token 只激活 $k/E$ 的权重**(稀疏),但总权重巨大 → 大 batch 下不同 token 命中不同专家、专家利用率才上来。

## 量化与公式 (Quantification)

新符号:$N_{tp},N_{pp},N_{ep},N_{dp}$ 各维并行度;$m$ micro-batch 数;$BW_\text{link}$ 互连带宽 [byte/s]。

### (1) 各维如何重映射成本模型的量

| 量 | 单卡 | TP=$N_{tp}$ | PP=$N_{pp}$ |
|---|---|---|---|
| 权重/卡 | $P p_w$ | $P p_w/N_{tp}$ | $P p_w/N_{pp}$ |
| KV/卡 | $\text{KV}_\text{tot}$ | $\text{KV}_\text{tot}/N_{tp}$(切 head) | $\text{KV}_\text{tot}/N_{pp}$(切层) |
| 聚合带宽 | $BW$ | $N_{tp}\,BW$ | $N_{pp}\,BW$(但串行) |
| 聚合算力 | $C$ | $N_{tp}\,C$ | $N_{pp}\,C$(但串行) |
| 额外通信 | — | 每层 2× all-reduce | stage 间 p2p + 气泡 |

→ **TP 把 [`01`](01-prefill-decode.md) 的 $BW,C$ 真正聚合**(降 TPOT/TTFT),PP 只是把容量摊开(总延迟还加了气泡)。这就是 **TP 是延迟工具、PP 是吞吐工具**的根。

### (2) TP 通信成本(为什么 TP 吃 NVLink)

decode 每步,TP 的 all-reduce 在关键路径上,激活 $[b,1,d]$,ring all-reduce 每卡每次约 $2\frac{N_{tp}-1}{N_{tp}}\,b\,d\,p$ 字节,每层 2 次、共 $L$ 层:

$$T_\text{comm}^\text{decode} \approx 2L\cdot 2\frac{N_{tp}-1}{N_{tp}}\cdot\frac{b\,d\,p}{BW_\text{link}}$$

**算例(70B,$N_{tp}=8$,$b=32$,$d=8192$,$p=2$,NVLink $\sim$450 GB/s)**:每 all-reduce/卡 $\approx 2\cdot\frac{7}{8}\cdot32\cdot8192\cdot2\approx 0.92$ MB,$\times2\times80$ 层 $\approx 147$ MB/step,$T_\text{comm}\approx147\text{e}6/450\text{e}9\approx 0.33$ ms/step。【估算,理想 NVLink、忽略 latency 项】若换成 PCIe(~64 GB/s)则 $\approx 2.3$ ms——**直接说明 TP 为何不能跨慢链路**:通信会吃掉 decode 一步的预算([`02`](02-metrics-slo.md) 的 ITL)。

### (3) PP 气泡

$$\text{气泡占比} = \frac{N_{pp}-1}{m+N_{pp}-1}$$

decode 尤其难:每步只 1 token,micro-batch $m$ 难做大 → 气泡大。这是 PP 对 decode 不友好、更适合 prefill/吞吐的量化原因。

## 推理 vs 训练的差异(架构师视角)

| 维度 | 训练 | 推理 |
|---|---|---|
| 计算图 | 前向 + 反向 | **仅前向** |
| 每参数显存 | ~16–20 B(参数+梯度+Adam 状态)【典型】 | ~2 B(权重)**+ KV** |
| 算术强度 | 几乎全程 compute-bound(大 batch 全序列,类 prefill) | **两阶段非对称**:prefill compute / **decode memory**([`01`](01-prefill-decode.md)) |
| 通信摊薄 | all-reduce 摊给大 GEMM,占比小 | decode 是 GEMV,**all-reduce 占比被放大** → TP 对 decode 更伤 |
| shape | 静态、已知 | 动态、变长 + continuous batching + 分页([`04`](04-dynamic-shape-batching.md)/[`06`](06-paged-kv-cache.md)) |
| 目标 | 只看吞吐 | **有延迟 SLO** → TP(降延迟)vs PP(加延迟)是推理独有的取舍 |
| 新增内存消费者 | — | **KV cache**(训练没有);其跨 TP/PP 的切分是推理独有问题 |

**两条最该记住的推理结论**:(a) 推理显存被**权重 + KV** 主导(无 Adam 状态),所以「装得下」主要靠 $N_{tp}\cdot N_{pp}$ 切权重 + 量化压 $p_w$([`10`](10-quantization.md));(b) **decode 的 GEMV 把通信占比放大** → 同一个 $N_{tp}$,训练能吃、decode 可能吃不消,这是 PD 分离要给两阶段**不同并行配置**的直接动机。

## 与架构建模的接口 (Modeling Interface)

- **$(N_{tp},N_{pp},N_{ep},N_{dp})$ 是顶层可扫配置**:每组取值就把 (1) 表里的「权重/卡、KV/卡、聚合 $BW$、聚合 $C$、通信项」一次性重映射 → 喂回 [`01`](01-prefill-decode.md) 的 TPOT/TTFT 与 [`06`](06-paged-kv-cache.md) 的并发。
- **通信项用 $BW_\text{link}$、和 [`08`](08-scheduling.md) 的 offload 链路同一套换档接口**:TP 必须 intra-node NVLink、PP 容忍 inter-node——**"哪个并行放节点内 / 哪个跨节点"就是按 $BW_\text{link}$ 档位决定的拓扑探索**,直接是 archax 要扫的 fabric 配置。
- **TP 有最优点**:(2) 的通信随 $N_{tp}$ 升,而单卡 $BW/C$ 收益随 $N_{tp}$ 边际递减 → 存在 $N_{tp}^\*$ 使 decode TPOT 最小;扫它是延迟优化的核心。
- **推理的两阶段非对称 → 单一全局并行配置是次优的**:prefill 想要大 TP/大算力,decode 想要省通信 + 大聚合带宽。**统一池只能折中** → 这正是 [`12`](12-pd-disaggregation.md) 把两阶段拆成各自独立并行配置的池的根据。把本篇的 (1) 表对 prefill / decode **各算一份**,差异就是 PD 分离的收益估计。

## 延伸阅读 (References)

- 上游:[`01`](01-prefill-decode.md)($BW,C$、两阶段)、[`02`](02-metrics-slo.md)(延迟 SLO)、[`10`](10-quantization.md)(压 $p_w$ 与切权重互补)。
- 下游:[`12` PD 分离](12-pd-disaggregation.md)(两阶段各用各的并行配置 + KV 过链路)。
- 外部:Megatron-LM(Shoeybi et al., 2019,TP 的列/行并行 + 每层 2 all-reduce);GPipe / PipeDream(PP 与气泡);MoE 推理与 EP(GShard、DeepSpeed-MoE、DeepSeek-V3 等)。`TODO(核实)`:若 `15` 要精确通信开销,补一份目标互连(NVLink 代际 / IB)带宽与 all-reduce 实现的 latency 项。
