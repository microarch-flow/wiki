# 世界模型工作负载：调用图比模型类别更重要

上级：[专题导读](README.md)

<span id="world-model-workload" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="成本的乘法结构world-model-与一次性推理的根本不同" class="workload-legacy-anchor"></span>
<span id="三类-world-model-的-workload-谱系" class="workload-legacy-anchor"></span>
<span id="可建模参数" class="workload-legacy-anchor"></span>
<span id="硬件连接" class="workload-legacy-anchor"></span>
<span id="archax-建模" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


世界模型可能用于训练、在线搜索或离线生成。只有执行图相同，候选数、预测长度和采样次数才能按同一公式比较。表示名称不能直接推出算力或延迟排序。

## 三种调用图分别计数

| 路径 | 工作量模型 | 必须说明 |
| --- | --- | --- |
| 逐时刻候选 rollout | 编码 + 各候选各时刻 transition 求和 + 评分 | 状态复用、候选 batch、递推依赖 |
| 整段序列 diffusion/flow | 编码 + NFE × 序列网络 + 解码/评分 | 单次求值已含哪些时间和候选轴 |
| 想象中训练策略，在线按观测选动作 | DreamerV3 每次交互计观测编码、循环状态更新和 actor | 想象时域进入训练账，实际观测与状态进入在线账 |

DreamerV3 的真实交互属于第三种；BEVWorld 的未来 latent 生成采用序列 diffusion；V-JEPA 2-AC 的在线规划包含候选搜索。不能给三者统一乘上 candidate×horizon。

## 两个可复算的例子

构造例 A：32 个候选、8 步递推，每次 transition 为 1 MFLOP，则主体为 256 MFLOP。候选可合批，8 步之间仍有依赖；不能据此说延迟为单步时延的 256 倍。

构造例 B：一个序列网络一次处理这 32 个候选的完整 8 步，单次为 40 MFLOP，NFE=10，则为 400 MFLOP。再乘 8 会重复计数。编码和解码按实际调用次数另计。

对一次处理整段的扩散或 Flow Matching 生成器，可以把上例写成 $F_{\rm total}=F_{\rm encode}+S\,F_{\rm seq}(C,H)+F_{\rm decode}$。$S$ 表示网络函数求值次数，$F_{\rm seq}(C,H)$ 已含 $C$ 个候选、$H$ 个未来时刻。若另外运行无条件分支做引导，要将该分支纳入每次求值的工作量，或另列其调用。为演示时延预算，假设一次求值耗时 8 ms，十次串行且每次耗时相同，主干即占 80 ms。编码、解码、排队和质量约束还要按整条链核对。

候选规划还有一个外层搜索循环。例如各候选展开 $H$ 步，CEM 精炼 $R$ 轮，便要在每轮为一批候选完成预测、评分和更新。真实交互若采用 DreamerV3 的 actor，在线则计一次观测编码、RSSM 更新和动作选择。沿这两条路径推导成本所需的状态见[策略学习与候选规划](../05-world-model-and-generative/latent-world-model.md)。

## 状态与输出的峰值容量

候选共享历史可以避免重复编码，但分叉后的状态通常不同。若每候选状态为 2 MiB，32 个候选同时驻留需要约 64 MiB，另加共享状态和工作区。分批可减少容量，却可能增加时延。

生成器若最终输出视频或 occupancy，解码成本不能删去；若下游直接消费 latent，则可能省掉在线解码。训练存在 decoder 与部署调用 decoder 是两个问题。

<span id="参考来源" class="workload-legacy-anchor"></span>

## 质量和系统边界

减少候选、时间长度或 NFE 会降低成本，也会改变搜索覆盖和预测质量。应在固定任务结果约束下比较，而非只给“每帧成本”。

在线链路应测编码、预测、评分、选择、通信与执行等待。离线链路则更关注有效样本吞吐、复现和存储。模型边界见[世界模型基础](../05-world-model-and-generative/world-model-fundamentals.md)。

## 来源与延伸

- [DreamerV3 原论文 v2](https://arxiv.org/html/2301.04104v2)
- [BEVWorld 原论文 v3](https://arxiv.org/html/2407.05679v3)
- [V-JEPA 2 / 2-AC 原论文 v1](https://arxiv.org/html/2506.09985v1)
