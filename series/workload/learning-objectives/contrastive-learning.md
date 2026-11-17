# 对比学习：用样本关系定义表示空间

上级：[专题导读](README.md)

<span id="contrastive-learning" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="对自动驾驶和机器人的实际作用" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


对比学习规定哪些表示应接近、哪些应分开。它是训练目标，不是一种固定骨干，也不必部署为双塔检索系统。CNN、ViT 或语言编码器都可参与这种训练。

## 正样本与负样本从哪里来

图像自监督学习可把同一图像的两种增强视图作为正样本，把其他图像视图作为负样本。图文训练可把配对图像和文本视为正样本。这个定义带有数据假设：增强应保留任务所需内容，配对文本应描述图像。

设归一化表示为 $z_i,z_j$，温度为 $\tau$，一类 InfoNCE 形式为：

$$
\ell_i=-\log\frac{\exp(\operatorname{sim}(z_i,z_j)/\tau)}
{\sum_{k\in\mathcal C_i}\exp(\operatorname{sim}(z_i,z_k)/\tau)}
$$

分母候选集合包含正样本，通常排除自身。温度控制分布尖锐程度。损失促使正确配对在候选中获得更高概率，并不强制绝对欧氏距离等于某个值。

构造例：正样本和两个负样本的缩放后 logits 为 2、0、0，正样本概率约 0.787，损失约 0.240。若某个“负样本”其实也是同一语义类别，推远它可能与下游目标冲突，这就是假负样本问题。

<span id="从-simclr-moco-到自蒸馏负样本问题的两种解法" class="workload-legacy-anchor"></span>

## SimCLR、MoCo 与 CLIP 的不同接口

SimCLR 用较大 batch 提供候选，并使用投影头计算训练损失。MoCo 用动量编码器和队列扩展候选集合。CLIP 分别编码图像和文本，在 batch 内形成相似度矩阵，并训练两个方向的配对分类。

这些设计不能直接互换。队列中的表示可能陈旧；batch 内全对比需要通信；图文配对也不提供逐像素定位或可靠的细粒度因果监督。

## 训练路径不等于部署路径

构造 batch 为 $B$ 的双塔训练会形成 $B\times B$ 配对分数。部署时可以预先计算候选文本或数据库向量，只编码新查询再检索。用于下游任务时，投影头还可能被移除或替换。

因此，训练的全对比矩阵不能自动计入每次端侧推理。多设备 all-gather、温度参数和损失归约也应归于实际训练路径。

对比学习依赖负样本的典型形式，与 [JEPA 的表征预测](jepa-and-self-supervised.md)、[掩码重建与自蒸馏](masked-reconstruction-and-distillation.md)需要分别描述。它们都可用于自监督，但不能归为同一损失。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [SimCLR](https://arxiv.org/abs/2002.05709)
- [MoCo](https://arxiv.org/abs/1911.05722)
- [CLIP](https://arxiv.org/abs/2103.00020)
