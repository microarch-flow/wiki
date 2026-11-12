# 02 服务指标与 SLO / Serving Metrics & SLOs

> 状态:草稿
>
> 一句话定位:把延迟/吞吐的口径一次性定死,作为后续所有篇与**你的 SLA 判定模块**的输入契约。本篇是「参考页」,被 `03`(浪费)、`08`(准入)、`15`(算例)反复引用。

## 概念 (Concept)

服务指标分两类**互相对立**的视角:

- **单请求体验(latency)**:用户感知的快慢。
- **系统效率(throughput / cost)**:单位硬件、单位时间、单位成本产出多少 token。

二者对立的物理根源已在 [`01`](01-prefill-decode.md) 给出:decode 是 [memory-bound](../glossary.md#memory-bound),**攒大 batch 提升系统吞吐,但每步要搬的 KV 字节变多 → 单请求 ITL 变长**。SLO(Service Level Objective)就是在这条 tradeoff 曲线上划一条线:**在不违反延迟约束的前提下,把吞吐/成本压到最优**。这条线正是 SLA 判定要算的东西。

**一个请求的生命周期时间线**(后面所有指标都从这条线上取):

```
到达        准入        prefill 完成          decode 逐 token
 │  queue   │  prefill   │   ITL   ITL   ...   ITL   │
 ▼─────────▶▼──────────▶▼──tok1──▶tok2 ...  ──▶tokN ▼
            │◀───────  TTFT  ──────▶│
 │◀──────────────────  E2E latency  ──────────────────▶│
```

## 机制 (Mechanism):定义表

| 指标 | 全称 | 精确定义 | 主导阶段 |
|---|---|---|---|
| **[TTFT](../glossary.md#ttft)** | Time To First Token | 请求**到达**到吐出**第 1 个** token 的墙钟时间 = 排队等待 + prefill 计算(+ 第一步 decode) | prefill([compute-bound](../glossary.md#compute-bound)) + 排队 |
| **TPOT** | Time Per Output Token | 首 token 之后,**平均**每个输出 token 的时间 $=\dfrac{\text{E2E}-\text{TTFT}}{N_\text{out}-1}$ | decode(memory-bound) |
| **[ITL](../glossary.md#itl)** | Inter-Token Latency | 相邻两个输出 token 的**实际间隔**,是一个**分布**(有 jitter);其均值≈TPOT | decode |
| **E2E** | End-to-End latency | 到达到**最后一个** token $=\text{TTFT}+(N_\text{out}-1)\cdot\text{TPOT}$ | 全程 |
| **吞吐** | throughput | 单位时间产出 token 数;需指明口径(见下) | 系统级 |
| **[goodput](../glossary.md#goodput)** | — | 仅计**满足 SLO** 的请求贡献的吞吐 | 系统级 |
| **MBU** | Model Bandwidth Utilization | decode 实测吞吐对应的 HBM 带宽 ÷ 峰值带宽,decode 效率上界指标 | decode |
| **MFU** | Model FLOPs Utilization | prefill/训练实测 FLOP/s ÷ 峰值,compute 效率指标 | prefill |

**解决 ITL vs TPOT 的歧义**(对应 glossary 里的 `TODO`):本 wiki 约定——**TPOT 指均值(一个标量),ITL 指逐 token 间隔的分布**(均值≈TPOT,但 SLO 关心其尾部 p99,因为一次卡顿就是一次可感知的"结巴")。很多厂商文档把两者混用为同一均值;遇到外部数字时按上下文判断它指均值还是分布。

**吞吐的三种口径**(必须指明,否则差一个数量级):

| 口径 | 表达式 | 用途 |
|---|---|---|
| 单用户 | $1/\text{TPOT}$ [tok/s/req] | 用户感知速度;对照"人阅读速度~5–10 tok/s" |
| 系统级 | $\sum_\text{req}$ 输出速率 [tok/s] | 集群产能 |
| 归一化 | tok/s/GPU、tok/s/$ | 成本模型、架构对比的可比量 |

**为什么 SLO 看百分位而非均值**:延迟受排队、抢占([`08`](08-scheduling.md))、变长([`04`](04-dynamic-shape-batching.md))影响,分布长尾。SLO 几乎总写成**百分位约束**:`TTFT_p99 ≤ 2s`、`TPOT_p99 ≤ 50ms`。均值达标但 p99 爆掉 = 1% 用户体验崩溃。

## 量化与公式 (Quantification)

符号:$N_\text{out}$ 输出 token 数;$T_q$ 排队时延;其余沿用 [`01`](01-prefill-decode.md)。

### (1) E2E 分解 —— SLA 判定的骨架式

$$\text{E2E} = \underbrace{T_q}_{\text{排队}} + \underbrace{T_\text{prefill}}_{\approx\,2Pb\,s_p/C\ \text{(compute-bound)}} + \underbrace{(N_\text{out}-1)\cdot \text{TPOT}}_{\text{decode,}\ \text{TPOT}\approx (Pp+b\,s\,\text{KV}_\text{tok})/BW}$$

- $\text{TTFT} = T_q + T_\text{prefill}$(+ 1 步 decode,通常可并入)。
- 两个 SLO **正好分管两个阶段**:**TTFT SLO ← prefill 侧(算力/排队)**;**TPOT SLO ← decode 侧(带宽/KV)**。这让 SLA 判定可拆成两个独立约束,分别对应不同的硬件设计参数。

### (2) throughput–latency tradeoff 与 batch 旋钮

由 [`01`](01-prefill-decode.md) (3):系统吞吐 $=\dfrac{b\,BW}{Pp+b\,s\,\text{KV}_\text{tok}}$ 随 $b$ 单调增(趋于 $BW/(s\,\text{KV}_\text{tok})$);而 $\text{TPOT}=(Pp+b\,s\,\text{KV}_\text{tok})/BW$ 随 $b$ 单调增。**同一个 $b$ 同时是吞吐的朋友、TPOT 的敌人**——SLO 给出 $b$ 的上界:

$$\text{TPOT}(b)\le \text{SLO}_\text{TPOT}\ \Rightarrow\ b \le \frac{BW\cdot \text{SLO}_\text{TPOT}-Pp}{s\,\text{KV}_\text{tok}}$$

这就是 [`08`](08-scheduling.md) 准入水位的延迟侧上界(另一侧是显存上界,见 `15`)。

### (3) Goodput —— 架构探索的目标函数

$$\text{goodput} = \frac{\#\{\text{满足 TTFT}_\text{SLO}\ \wedge\ \text{TPOT}_\text{SLO}\ \text{的已完成请求产出 token}\}}{\text{墙钟时间}}$$

或工程上常用的等价表述:**在保证 X%(如 99%)请求满足 SLO 的前提下,系统能承受的最大请求到达率 / 最大 token 产出率**。注意 goodput **不是**吞吐打折——超过拐点后继续加 batch,吞吐还在涨但 goodput 会**掉头向下**(违约请求不计数),这个峰值点才是部署/选型要找的工作点。

### (4) MBU —— decode 效率的单一数字

$$\text{MBU} = \frac{\text{实测每步 HBM 字节} / \text{实测 } t_\text{step}}{BW_\text{peak}} = \frac{(Pp + b\,s\,\text{KV}_\text{tok})/t_\text{step}}{BW_\text{peak}}$$

MBU 接近 1 表示 decode 已被带宽喂满(理想 memory-bound);MBU 低说明 kernel/调度有空泡(→ `05` FlashDecoding、`08` 抢占),还有提速空间。`TODO(确认)`:你们内部对 decode 效率是用 MBU 还是别的口径(如 achieved tok/s vs roofline 上界)?以便 `15` 对齐。

### 算例(示意,非某型号实测)

设某配置 prefill 后 $\text{TTFT}=0.5$ s,$\text{TPOT}=25$ ms,$N_\text{out}=500$:
$$\text{E2E}=0.5 + 499\times0.025 \approx 13.0\ \text{s},\quad \text{单用户吞吐}=1/0.025=40\ \text{tok/s}$$
SLO `TTFT_p99 ≤ 2s ∧ TPOT_p99 ≤ 50ms`:该请求 0.5s/25ms **达标**。若为提系统吞吐把 batch 翻倍致 $\text{TPOT}=55$ ms → **TPOT 违约**,这条请求即从 goodput 里**剔除**——哪怕系统总 tok/s 更高。【示意,数字为说明判定逻辑而设】

## 与架构建模的接口 (Modeling Interface)

- **SLA 判定的布尔契约**(可直接落成仿真器输出层):
  $$\text{satisfied}(r) = [\,\text{TTFT}(r)\le \text{SLO}_\text{TTFT}\,]\ \wedge\ [\,\text{TPOT}(r)\le \text{SLO}_\text{TPOT}\,]$$
  整机判定 = 满足比例 $\ge$ 目标分位(如 99%)。**两个子约束分别由 prefill 侧(算力 $C$、排队)与 decode 侧(带宽 $BW$、$\text{KV}_\text{tok}$)决定**,可独立做敏感度分析。
- **目标函数**:架构探索扫设计参数时,**最大化 goodput(或 goodput/$)**,而非裸吞吐——这是 batching/PD 切分/并行度等旋钮的统一评判标准。
- **可扫设计参数 → 指标的映射**(供你建 response surface):
  | 旋钮 | 主要影响 | 来源篇 |
  |---|---|---|
  | batch $b$ | ↑系统吞吐、↑TPOT | (2) |
  | 精度 $p$(量化) | ↓$Pp$、↓$\text{KV}_\text{tok}$ → ↓TPOT、↑并发 | `10` |
  | chunk 大小 | prefill/decode 干扰、TTFT vs TPOT 平衡 | `04` |
  | PD 切分 | 解耦 TTFT 与 TPOT 的优化 | `12` |
  | 并行度 TP/PP | ↑聚合 $BW,C$、↑通信 | `11` |
- **喂给 SLA 判定的最小量**:每请求的 $(\text{到达时刻}, s_p, N_\text{out})$ + 仿真器算出的 $(T_q, T_\text{prefill}, \text{TPOT}\text{ 序列})$ → 即可判定并聚合成 goodput。

## 延伸阅读 (References)

- 上游:[`01` 推理基础](01-prefill-decode.md)(TTFT/TPOT 的物理来源公式)。
- 下游:[`03` 朴素瓶颈](03-naive-bottlenecks.md)(指标如何被浪费)、[`08` 调度](08-scheduling.md)(准入水位用本篇 (2))、[`15` 算例](15-quantitative-estimation.md)(代入真实数字)。
- 外部:goodput 的系统化定义见 **DistServe**(Zhong et al., OSDI '24,arXiv 2401.09670)——**per-GPU goodput = 满足 SLO 达成率(如 90%)下每 GPU 能服务的最大请求率**(已核实,详见 [`12`](12-pd-disaggregation.md));TTFT/TPOT/ITL 工程口径可对照 vLLM、NVIDIA NIM/TensorRT-LLM 的 benchmark 文档。`TODO(核实)`:取一份官方 benchmark 文档确认其 TPOT 是否含首 token。
