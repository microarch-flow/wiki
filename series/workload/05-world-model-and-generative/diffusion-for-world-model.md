# 扩散世界模型：时间长度与采样次数怎样计量

上级：[专题导读](README.md)

<span id="diffusion-for-world-model" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="三重乘法world-model-的乘法又被乘上步数" class="workload-legacy-anchor"></span>
<span id="在不同输出上的差异同一矛盾不同代价" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


本页只讨论扩散或 flow 生成器如何预测环境未来。[扩散基础](../generative-models/diffusion-models.md)解释训练与采样，[flow matching](../generative-models/flow-matching.md)解释连续速度场；这里重点是环境条件和调用次数。

## 输出整段未来还是递推下一步

序列生成器可以一次处理多个未来位置，再通过多次网络求值更新整段样本。递推模型则在每个时刻产生下一状态，再把结果作为后续输入。两种执行图不同。

设候选 batch 为 $C$、未来长度为 $H$、采样 NFE 为 $S$。整段生成的工作量可记为：

$$
F_{\rm total}=S\,F_{\rm seq}(C,H)+F_{\rm encode}+F_{\rm decode}
$$

若 $F_{\rm seq}$ 已包含 $H$，不能再乘一次 $H$。只有模型每次调用只预测一个时间步时，才可使用相应的逐时刻求和。

## 条件如何影响未来

历史场景、动作、地图或导航可作为条件。BEVWorld 使用高层动作 token 条件预测 BEV latent 序列。生成器能跟随训练中的条件，不自动说明它对所有反事实动作都准确。

多模态未来允许同一历史产生多种可能结果。候选之间的差异既可能来自环境不确定性，也可能来自采样噪声；应用需要说明如何利用它们，不能把样本多样性直接称为校准后的概率。

## 少步采样的收益需要质量约束

减少 NFE 可减少网络调用，但误差、条件服从和长时一致性可能变化。Flow matching 不是天然一步生成；蒸馏也需要训练代价和质量验证。

构造例：一次序列网络求值需要 8 ms，10 NFE 的串行主干约 80 ms，另加编码、解码和调度。这只是固定每次耗时且无额外求值的预算模型，不是任意设备的测量。

## 与动作生成分开

生成未来场景和生成动作使用类似网络，不代表任务相同。Diffusion Policy 的输出是动作，世界模型的输出是环境预测；只有后者具有相应环境学习目标时才应按世界模型讨论。

资源评估见[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)，在线与离线分工见[端云协作](../06-chip-workload-analysis/edge-cloud-collaborative-world-model.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [DDPM](https://arxiv.org/abs/2006.11239)
- [Flow Matching](https://arxiv.org/abs/2210.02747)
- [BEVWorld](https://arxiv.org/abs/2407.05679)
- [Diffusion Policy](https://arxiv.org/abs/2303.04137)
