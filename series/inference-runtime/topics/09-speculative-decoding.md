# 09 投机解码 / Speculative Decoding

> 状态:草稿
>
> 一句话定位:用**便宜的 draft 猜多个 token、贵的 target 一次并行 verify**,把 decode 的「每步 1 token」变成「每步 $E>1$ token」。本质是**拿 memory-bound decode 闲置的算力,换更少的访存步**——所以它是个**低 batch / 低延迟**杠杆,和大 batch 吞吐互相拉扯([`01`](01-prefill-decode.md) 算术强度、[`05`](05-attention-kernels.md) split-KV 的同一根张力)。

## 概念 (Concept)

[`01`](01-prefill-decode.md) 已证:decode 每步只生成 1 token,memory-bound,**算力大量闲置**(读一遍权重只做了 $2Pb$ FLOP)。投机解码就是把这份闲置算力用起来:

1. **draft(草稿)**:一个小而快的模型自回归猜 $\gamma$ 个候选 token(便宜)。
2. **verify(验证)**:大 target 模型把这 $\gamma$ 个候选**在一次 forward 里并行验证**($s_q=\gamma$,相当于一次 $\gamma$ token 的 mini-prefill)——**仍只读一遍权重**,却能一次性吐出最多 $\gamma+1$ 个被接受的 token。

关键:verify 那一步的访存量(读权重 $\sim Pp$)和普通 decode 一步几乎一样,但产出从 1 涨到 $E$ 个 token。**只要还在 memory-bound 区间,这多出来的算力就是"免费"的。**

## 机制 (Mechanism)

### draft–verify 流程

draft 给出候选序列 $x_1,\dots,x_\gamma$ 及其分布 $q(\cdot)$;target 一次 forward 算出每个位置的真实分布 $p(\cdot)$。逐位置做接受判定,接受的最长前缀 + 1 个 target 采的 bonus token 一并产出,然后从第一个被拒位置重启下一轮。

### rejection sampling 的无损性(为什么不掉质量)

逐位置:以概率 $\min\!\big(1,\ \tfrac{p(x)}{q(x)}\big)$ 接受 draft 的 $x$;若拒绝,从**残差分布** $p'(x)=\mathrm{norm}\big(\max(0,\,p(x)-q(x))\big)$ 重采。可证:这样产出的 token **精确服从 target 分布 $p$**,与直接从 target 采样**分布完全一致**(Leviathan et al. 2023 / Chen et al. 2023 给出证明)。

> 对架构师的意义:**投机解码只改性能,不改输出分布**。所以它在成本模型里是一个**纯加速旋钮,没有质量代价**——不像量化([`10`](10-quantization.md))要权衡精度。$\alpha$(接受率)高低只影响**速度**,不影响正确性。

### 变体(都保持无损,差别在"怎么造更准的 draft")

| 变体 | draft 来源 | 关键点 | 报告加速 |
|---|---|---|---|
| **vanilla SD** | 独立小模型 | 原始 draft-verify | ~2.8× |
| **Medusa** | target 上加多个 MLP 头 | 无独立模型;并行预测 t+1,t+2,…;tree attention 验证 | ~2–3× |
| **EAGLE-1/2/3** | 轻量头 + **特征级**自回归 | 在 hidden feature 层外推(更准);EAGLE-2 动态 draft tree;EAGLE-3 融合多层特征 | 最高 **6.5×**(EAGLE-3) |
| **Lookahead** | 无 draft 模型 | 把自回归看成 Jacobi 迭代,直接从 target 并行抽取/验证 n-gram | 视任务 |

【加速为论文报告值,依模型/任务/batch 差异大】共同点:**target 的验证机制不变(rejection sampling),故都无损**;差别只在 draft 的命中率 $\alpha$ 与成本 $c$。

## 量化与公式 (Quantification)

新符号:$\gamma$ 每轮 draft token 数;$\alpha$ 接受率(单 token 被接受的近似概率);$c$ = draft 单步成本 / target 单步成本;$E$ target 每次 forward 的期望产出 token 数。

### (1) 期望产出与加速比(Leviathan 公式)

每轮接受到第一个被拒处,几何分布 + 1 个 bonus:

$$E = \frac{1-\alpha^{\gamma+1}}{1-\alpha}$$

一轮总成本(以 target 一次 forward 为单位)$\approx 1 + \gamma c$(target 1 次 + draft $\gamma$ 次)。故

$$\text{speedup} = \frac{E}{1+\gamma c} = \frac{1-\alpha^{\gamma+1}}{(1-\alpha)(1+\gamma c)}\ \xrightarrow[c\to0,\ \gamma\to\infty]{}\ \frac{1}{1-\alpha}$$

**上界 $\tfrac{1}{1-\alpha}$**:$\alpha=0.8\Rightarrow$ 至多 5×;$\alpha=0.7\Rightarrow$ 3.3×。

**算例**:$\alpha=0.8,\ \gamma=4,\ c=0.1$ → $E=\frac{1-0.8^5}{0.2}=\frac{0.672}{0.2}=3.36$ token/轮,成本 $1+0.4=1.4$ → **speedup $=3.36/1.4\approx2.4\times$**。【估算,$\alpha$ 为假设值】

### (2) 与 batch 的张力(核心架构结论)

verify 那次 forward 处理 $b\gamma$ 个 token($s_q=\gamma$/请求),FLOP $\approx 2P\,b\gamma$、读权重 $\approx Pp$ → 算术强度 $AI\approx 2b\gamma/p$。沿用 [`01`](01-prefill-decode.md) 的 ridge $=C/BW\approx295$(H100,fp16):

$$\text{"免费算力"区间}:\quad b\gamma \lesssim \frac{\text{ridge}\cdot p}{2}\approx 295\quad\Rightarrow\quad b^\* \approx \frac{\text{ridge}\cdot p}{2\gamma}=\frac{295}{\gamma}$$

- $b\gamma \lesssim 295$:verify 仍 memory-bound,墙钟时间≈普通一步 → 多出的 $\gamma\times$ 算力**白拿** → 延迟与吞吐**双赢**。$\gamma=4$ 时 $b^\*\approx74$。
- $b\gamma \gtrsim 295$:verify 自身变 compute-bound,$\gamma\times$ FLOP 变成**真实开销** → speedup 退化,大 batch 下甚至**拖慢**。

> 一句话:**投机解码是低 batch / 延迟敏感场景的杠杆**;大 batch(已 compute-efficient、无闲置算力)下它和「攒 batch」抢的是同一份算力,二者**替代而非叠加**。这与 [`05`](05-attention-kernels.md) split-KV「价值随 batch 衰减」同源——都是"低 batch 才有富余资源可榨"。

## 与架构建模的接口 (Modeling Interface)

- **建成 ITL 的乘子(仅在 memory-bound 区间有效)**:
  $$\text{ITL}_\text{spec} = \text{ITL}_\text{base}\cdot\frac{1+\gamma c}{E}\quad(\text{当 } b\gamma\lesssim \text{ridge}\cdot p/2)$$
  超出区间则按 verify 的 compute-bound 时间重算,**speedup 归零甚至 <1**。
- **$\alpha$ 是唯一不能从硬件推出的参数**:它由 draft 质量 × workload 决定,**必须实测**(代码任务 $\alpha$ 高、开放对话低)。建模时把 $\alpha$ 当**输入分布**,别当常数——这是 spec decoding 收益预测最大的不确定源。`TODO(确认)`:你的目标 workload 有没有 $\alpha$ 的实测档,以便 `15` 代入。
- **自适应开关**:交叉点 $b^\*=\text{ridge}\cdot p/(2\gamma)$ 是调度器([`08`](08-scheduling.md))决定**当前 batch 下是否开投机**的判据——低载开、高载关,真实系统都这么做。
- **roofline 视角**:投机把 decode 的 $s_q$ 从 1 抬到 $\gamma$ → $AI$ 右移,**字面意义上是沿 roofline 移动工作点的旋钮**。量化([`10`](10-quantization.md))缩小 $p$ 会改变 ridge·p,进而移动 $b^\*$。
- **kernel 形态(接 [`05`](05-attention-kernels.md))**:verify = mini-prefill($s_q=\gamma$),kernel 形态介于 decode 与 prefill 之间;Medusa/EAGLE 的 tree 验证带**不规则 tree mask**,attention kernel 要支持 tree-attention(非块对角)——这是仿真器里要单独建模的一类不规则 attention。

## 延伸阅读 (References)

- 上游:[`01`](01-prefill-decode.md)(memory-bound 闲置算力、ridge)、[`05`](05-attention-kernels.md)(verify kernel、tree attention、低 batch 张力)、[`08`](08-scheduling.md)(自适应开关)。
- 下游:[`10` 量化](10-quantization.md)(改 ridge·p 移动 $b^\*$)、[`14` 框架对比](14-framework-comparison.md)(各框架的 spec 支持)。
- 外部(已核实):
  - 无损性原典:Leviathan et al., *Fast Inference from Transformers via Speculative Decoding*, 2023;Chen et al.(DeepMind), 2023——rejection sampling 分布无损 + $E$ 公式。
  - **EAGLE-1/2/3**(ICML'24 / EMNLP'24 / NeurIPS'25,特征级 + 动态 draft tree,EAGLE-3 max 6.5×)。[arXiv 2503.01840](https://arxiv.org/pdf/2503.01840) / [SafeAILab/EAGLE](https://github.com/SafeAILab/EAGLE)
  - **Medusa**(多头 + tree attention);**Lookahead Decoding**(Jacobi,无 draft,ICML'24)。[LMSYS blog](https://lmsys.org/blog/2023-11-21-lookahead-decoding/)
  - 综述:*A Survey of Speculative Decoding*(arXiv 2401.07851)。
