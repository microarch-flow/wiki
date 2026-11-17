# ViT 与 Swin：图像如何变成 token 序列

上级：[专题导读](README.md)

<span id="vision-transformer-backbone" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="分层-vit-与-swin把层次结构装回来" class="workload-legacy-anchor"></span>
<span id="在-ad-vla-world-model-中的意义" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


视觉 Transformer 的关键接口是图像到 token 的转换。ViT 与 Swin 都使用 attention，但 token 数、层级结构和连接范围不同，不能用同一张计算图替代。

<span id="vit-和-cnn-的本质差异" class="workload-legacy-anchor"></span>

## ViT 的输入与输出

将 $H\times W$ 图像划分为不重叠的 $P\times P$ patch。假设尺寸可整除，patch 数为 $N=HW/P^2$。每个 patch 展平后经过线性投影，得到 $D$ 维 token，再加入位置信息。分类模型可额外添加一个分类 token；密集预测通常还要恢复空间结构或连接任务头。

构造例：$224\times224$ 图像、patch 边长 16，得到 196 个 patch token；加入一个分类 token 后为 197。若保持 patch 大小，把图像边长加倍，则 patch 数变为 784；全局 attention 的 token 配对数约增加到 16 倍。投影与 FFN 的计算量只按 token 数增加到约 4 倍。

patch 化不会保留全部原始像素细节。小目标、边界定位和高分辨率输入之间有实际取舍。预训练数据与训练方案也影响结果，不能把质量差异全归因于 CNN 或 Transformer 名称。

## Swin 如何控制连接范围

Swin 在局部窗口内计算 attention，并在相邻层移动窗口划分，使跨窗口信息可以交互。窗口边长固定为 $M$ 时，每个窗口有 $M^2$ 个 token，所有窗口的配对规模为 $NM^2$，而非全局的 $N^2$。移动窗口需要边界掩码；它不等于每层全图两两交互。

阶段之间，patch merging 合并相邻 **2×2 的四个 token**。先拼接成 $4C$ 维，再投影为 $2C$ 维。因此空间 token 数变为原来的四分之一，通道数翻倍。

例如 $56\times56\times C$ 经过一次合并后是 $28\times28\times2C$。token 数从 3136 降到 784；元素总数减半。这里“元素数减半”与“token 数减半”是不同结论。

## 两种骨干怎样选择与衔接

| 结构 | 输出组织 | 更需要关注的条件 |
| --- | --- | --- |
| 原始 ViT | 近似恒定分辨率的 token 序列 | 全局关系、输入分辨率、预训练与位置编码 |
| Swin | 分层、多尺度的特征 | 窗口大小、跨窗口传播、合并造成的细节损失 |

检测器可以使用 ViT、Swin 或 CNN；是否需要 [neck](neck-feature-fusion.md) 取决于任务头要求的尺度。不能把骨干和完整检测方法视为同一分类层级。

<span id="从图像到-token被平方放大的代价" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 工作负载中的实际差异

原始 ViT 的全局 attention、Swin 的小窗口 attention，以及层间的重排和合并，应分别记录形状。很多小窗口未必比一个大矩阵更容易获得高硬件利用率。窗口打包、掩码和内核融合决定额外开销。

骨干推理通常一次处理已知图像 token，不天然具有语言生成的逐 token decode 阶段。通用算子机制见 [Attention 与 Transformer](attention-and-transformer.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [ViT 原论文](https://arxiv.org/abs/2010.11929)
- [Swin 原论文（ICCV 2021）](https://openaccess.thecvf.com/content/ICCV2021/papers/Liu_Swin_Transformer_Hierarchical_Vision_Transformer_Using_Shifted_Windows_ICCV_2021_paper.pdf)
