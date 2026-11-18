# Attention 效率：哪些方法改变计算，哪些改变实现

上级：[专题导读](README.md)

<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="sparse-block-sparse-与-gqamqa两种不同的稀疏" class="workload-legacy-anchor"></span>
<span id="cross-deformable-temporal不对称与动态访存" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


“高效 attention”不是单一机制。先确认改动对象：token 之间的连接、KV 头数、计算顺序，还是缓存管理。只有在相同任务质量、长度、精度和硬件条件下，性能数字才可以比较。

## 四种常被混淆的改动

| 方法 | 改动对象 | 保留什么 | 主要代价 |
| --- | --- | --- | --- |
| 窗口或稀疏 attention | 参与计算的 token 对 | 选定连接上的注意力 | 全局信息路径改变，依赖稀疏模式 |
| MQA / GQA | query 头与 KV 头的对应 | 每个 query 仍可读取全部允许位置 | 需要适配模型与训练，质量需测 |
| FlashAttention | 分块、融合与归约次序 | 稠密 attention 的数学目标 | 内核与设备约束，浮点舍入可不同 |
| PagedAttention | KV 的存储与分配 | 模型定义的 attention | 地址管理、块粒度与调度开销 |

不能把 GQA 称为 token 稀疏化，也不能把 KV 分页当成减少模型参数。

## GQA 为什么减少 KV cache

令 query 头数为 $h_q$，KV 头数为 $h_{kv}$，每头维度为 $d_h$。MHA 通常 $h_{kv}=h_q$；MQA 使用一组 KV；GQA 位于两者之间。一组 query 头共享相同的 K/V，但仍各自计算注意力权重。

例如 4 个 query 头共用 2 个 KV 头，前两个 query 头读取同一份 K/V，后两个读取另一份。与 4 组独立 KV 相比，每个历史位置只需保存一半的键和值，4 个 query 头仍各有自己的注意力分布。固定层数、长度和精度后的字节数，以及 prefill 与 decode 的完整算例见 [Transformer 工作负载](../06-chip-workload-analysis/transformer-workload.md)。

<span id="attention-variants-and-efficiency" class="workload-legacy-anchor"></span>
<span id="flashattention把-attention-重新定性为-io-问题" class="workload-legacy-anchor"></span>
<span id="window-local-attention用局部性换平方" class="workload-legacy-anchor"></span>

## FlashAttention 怎样避免大中间张量

朴素实现先生成完整分数矩阵，再 softmax，再乘 V。分块实现依次处理 K/V 块，维护每个 query 行的最大值、归一化分母及加权和。

若已有最大值 $m$、分母 $\ell$ 和未归一化加权和 $u$，新块分数为 $S_j$，可更新：

$$
m'=\max(m,\max S_j),\quad
\ell'=e^{m-m'}\ell+\sum_j e^{S_j-m'}
$$

$$
u'=e^{m-m'}u+\sum_j e^{S_j-m'}V_j
$$

处理全部块后输出 $u/\ell$。重缩放让不同块共享同一归一化基准；无需把完整 $N\times N$ 分数留在 HBM。数学上仍是原来的稠密 attention，不是删去低权重项。浮点计算顺序改变，所以“exact attention”不代表逐位相同。

## 何时需要改变模型本身

固定窗口减少连接数，但远距离交互要依赖移位、跨层传播或额外全局 token。线性 attention 通常改变核表达或计算分解，不应直接等同于原始 softmax attention。SSM 则以递推状态建模序列，见 [Mamba 与 SSM](mamba-and-ssm.md)。

选择方法时，先记录质量约束，再测请求长度分布、batch、prefill/decode 比例和存储边界。某种内核在长序列训练中有效，不意味着它在单请求短 decode 中收益相同。运行时缓存与调度的主要归属见[推理与运行时系列](../../inference-runtime/README.md)；其中规划中的页面不能当作已验证实现。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [GQA 原论文](https://aclanthology.org/2023.emnlp-main.298/)
- [FlashAttention](https://arxiv.org/abs/2205.14135)
- [PagedAttention / vLLM](https://arxiv.org/abs/2309.06180)
