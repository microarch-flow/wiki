# Attention 与 Transformer：从加权读取到一个完整 block

上级：[专题导读](README.md)

<span id="attention-and-transformer" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="attention-的计算结构与真实形状" class="workload-legacy-anchor"></span>
<span id="为什么-softmax-前要除-sqrtd_k" class="workload-legacy-anchor"></span>
<span id="为什么-pre-norm为什么-rmsnorm" class="workload-legacy-anchor"></span>
<span id="它为什么成为自动驾驶机器人world-model-的通用底座" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


Attention 根据输入内容计算信息的混合权重。标准稠密 attention 仍访问既定的 token 集合；权重变化不等于访存地址随机变化。Transformer 在 attention 之外还包含投影、前馈网络、归一化与残差连接。

## 从形状理解加权读取

设输入为 $X\in\mathbb R^{B\times N\times d}$。投影后分成 $h$ 个头，每头维度 $d_h=d/h$。一个头的计算为：

$$
Q=XW_Q,\quad K=XW_K,\quad V=XW_V
$$

$$
A=\operatorname{softmax}\left(QK^\top/\sqrt{d_h}+M\right),\qquad O=AV
$$

$M$ 是掩码。双向 encoder 通常允许读取所有有效位置；因果模型禁止读取未来位置。softmax 对每个 query 的 key 轴归一化，输出是 value 的加权和。不同头的结果拼接后，再经过输出投影。

构造例：两个 value 分别为 2 和 10，某 query 的注意力权重为 0.75 和 0.25，则输出为 4。两处 value 都参与计算；这不是只读取权重最大的那个地址。稀疏 attention 或显式检索才可能改变参与集合。

缩放因子 $\sqrt{d_h}$ 的直觉来自方差：若 query/key 各分量独立、零均值、单位方差，点积的方差为 $d_h$。缩放可控制 logits 的典型幅度。这是一个解释性假设，不是所有训练状态下的统计保证。

<span id="多头为什么不改-flops-却要拆" class="workload-legacy-anchor"></span>

## 多头与完整 block

在总宽度 $d$ 固定时，多头给出多个独立的权重分布。它不要求每个头预先负责语法、几何或某一种语义。不同头可能学到不同关系，也可能冗余。

常见 Pre-Norm block 可写为：

$$
U=X+\operatorname{Attention}(\operatorname{Norm}(X)),\qquad
Y=U+\operatorname{FFN}(\operatorname{Norm}(U))
$$

FFN 对每个位置独立做通道变换；attention 在位置之间交换信息。残差提供直接通路，归一化控制数值尺度。Post-Norm、LayerNorm、RMSNorm 是不同设计选择，不能把一种布局当成 Transformer 的定义。

LayerNorm 使用均值和方差；RMSNorm 基于均方根缩放，省去减均值。是否降低端到端延迟还取决于融合、数据布局与实现，不能由公式少一项直接推断。

<span id="transformer-block逐算子的代价分布" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 计算量交点不是性能分界线

以下只针对标准稠密 MHA、$d=hd_h$、两层 FFN 隐藏宽度 $4d$，忽略偏置、激活与归一化，并按 1 MAC = 2 FLOP：

| 部分 | 每层前向 FLOP |
| --- | ---: |
| Q、K、V 与输出投影 | $8BNd^2$ |
| 两层 FFN | $16BNd^2$ |
| 两次 attention 矩阵乘 | $4BN^2d$ |

由此，attention 两次矩阵乘与其余线性层的计算量在 $N=6d$ 相等。这个交点依赖上述结构；GQA、门控 FFN、交叉注意力会改变它。它也**不表示**硬件在此处从计算受限切换为带宽受限。

固定总宽度时，多头不改变上述矩阵乘的主要项，但 softmax 工作量和显式分数张量大小与头数有关。若 $B=1,h=16,N=2048$ 且分数为 FP16，完整分数张量为 128 MiB，约 134.2 MB。只有选择物化该张量的实现才产生相应存储；[FlashAttention](attention-variants-and-efficiency.md) 可避免把完整矩阵写入 HBM。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 适用边界与后续阅读

Attention 提供长距离交互路径，不保证一定优于卷积，也不保证自动学到可靠因果关系。位置编码、掩码、训练目标和数据决定模型能使用什么信息。

沿视觉路线继续读 [ViT 与 Swin](vision-transformer-backbone.md)，看图像 patch 怎样交换信息。沿语言路线读[自回归生成](../generative-models/autoregressive-generation.md)，看因果掩码允许每个位置看到哪些 token。要计算同一层在 prefill 与 decode 两个阶段的工作量和 KV 流量，读 [Transformer 工作负载](../06-chip-workload-analysis/transformer-workload.md)。

## 来源与延伸

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Transformer 中 LayerNorm 的位置](https://arxiv.org/abs/2002.04745)
- [RMSNorm](https://arxiv.org/abs/1910.07467)
- [FlashAttention](https://arxiv.org/abs/2205.14135)
