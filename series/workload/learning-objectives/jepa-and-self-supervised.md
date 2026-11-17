# JEPA：预测目标表示，而非重建每个像素

上级：[专题导读](README.md)

<span id="jepa-and-self-supervised-representation" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="i-jepav-jepa-与-v-jepa-2从图像到可规划的视频表征" class="workload-legacy-anchor"></span>
<span id="对-world-model-的意义为什么是分水岭" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


联合嵌入预测架构（JEPA）在表示空间预测被隐藏或尚未观察到的信息。核心区别是预测目标所在的空间；“自监督”是监督来源，二者不能作为同义词。

## 上下文、目标编码器与预测器

以 I-JEPA 为例，上下文编码器读取可见区域，预测器结合目标位置信息输出目标表示。目标编码器处理相应图像内容，提供学习目标。目标分支停止梯度，并通过上下文编码器参数的指数移动平均更新。

$$
\hat z_{\rm target}=g_\phi(f_\theta(x_{\rm context}),m),\qquad
\mathcal L=\operatorname{dist}(\hat z_{\rm target},
\operatorname{stopgrad}(f_{\bar\theta}(x)_{\rm target}))
$$

$m$ 指明要预测的位置，$\bar\theta$ 是目标编码器参数。公式表示一般结构；具体距离、掩码和归一化以论文实现为准。

构造例：图像被分成 16 个 patch，只给上下文编码器其中 8 个，要求预测另外 4 个位置的表示。目标不是 4 个 patch 的 RGB 原值，而是目标编码器产生的向量。表示维度和 token 数仍可很大，不能把 latent 直接理解成“几个语义标签”。

## 为什么需要避免坍塌

若所有输入都映射成同一个向量，表征预测也可能得到很小的损失，却没有可用信息。目标分支、停止梯度、预测器以及掩码和训练策略共同影响学习行为。不能仅凭“有 EMA”就证明任何改写后的系统都不会坍塌。

与 [MAE](masked-reconstruction-and-distillation.md) 相比，JEPA 不要求主目标重建像素；与典型[对比学习](contrastive-learning.md)相比，它不以样本间负对比为核心。是否更适合某任务仍需下游评估。

## 从图像表征到视频与动作

视频中的目标还可沿时间轴选择。V-JEPA 2 的基础模型通过无动作的视频学习表示；V-JEPA 2-AC 再引入动作条件，用预测表示支持机器人规划。**动作条件预测能力属于相应的后训练模型，不能归给所有 JEPA 编码器。**

做规划时，系统还需要目标表示、候选动作和比较代价。单次表征预测的速度不能替代整个规划器的延迟。模型及其调用路径见 [latent 世界模型](../05-world-model-and-generative/latent-world-model.md)。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 工作负载需要分开记录

训练通常运行上下文编码器、目标编码器和预测器；下游部署可能只保留编码器，也可能使用预测器做多次候选评估。目标编码器无反向梯度，不代表其前向计算免费。应先画出被部署的子图，再统计成本。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [I-JEPA](https://arxiv.org/abs/2301.08243)
- [V-JEPA 2 / 2-AC 原论文 v1](https://arxiv.org/html/2506.09985v1)
