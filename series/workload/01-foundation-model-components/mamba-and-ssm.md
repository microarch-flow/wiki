# Mamba 与状态空间模型：用递推状态处理序列

上级：[专题导读](README.md)

<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="selective-scan机制与硬件的双重面孔" class="workload-legacy-anchor"></span>
<span id="与-transformer-的互补不是替代" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


状态空间模型（SSM）用内部状态压缩已处理的历史。新输入更新状态，再从状态产生输出。固定宽度状态避免逐步保存全部历史，但也限制可直接访问的细节；这不是无损保存无限上下文。

## 从一个递推例子开始

简化离散模型为：

$$
h_t=\bar A h_{t-1}+\bar B x_t,\qquad y_t=Ch_t+Dx_t
$$

$x_t$ 是输入，$h_t$ 是持久状态，$y_t$ 是输出。构造标量例：$h_t=0.5h_{t-1}+x_t$，$h_0=0$，输入为 2、0、4，则状态依次为 2、1、4.5。旧信息逐步衰减，新信息进入状态。这里的系数只是教学假设。

若系统线性且时不变，展开递推可得到与输入序列的卷积形式。这个等价关系有条件；不能把输入相关的选择性递推一概视为固定卷积核。

<span id="mamba-and-ssm" class="workload-legacy-anchor"></span>

## Mamba 的选择性来自哪里

Mamba 让部分参数依赖当前输入，使模型可以根据内容控制状态更新和读取。原论文的选择性 SSM 将输入映射到离散化步长以及 B、C 等参数；A 保持结构化参数化。完整模块还包含投影、局部卷积和门控，成本不只有一条标量递推。

直觉上，固定衰减只能统一遗忘；输入相关的更新可以为不同内容采用不同保留方式。但“选择性”不等于把任意过去 token 原样存入可寻址表。

## 训练扫描与流式推理

已知整个输入序列时，递推的仿射变换可以组合，并通过并行 scan 组织计算。生成新 token 时，新输入尚未产生，仍存在跨步因果依赖。

对于固定 batch、状态宽度和层数，纯 SSM 的递推状态容量不随已处理长度增长。训练时仍可能保存输入、中间激活和反向传播所需信息，因此不能把“推理状态固定”扩展成“训练显存固定”。

Mamba-2 进一步研究 SSM 与结构化 attention 的联系。实际系统也可混合 SSM 和 attention；混合模型里的 attention 层仍有自己的 KV 状态。应按层统计，不能整模型套一个复杂度标签。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 适用边界

固定状态适合流式更新，但精确回查长历史、输入长度外推和训练稳定性仍需任务验证。复杂度随长度线性也不保证短序列延迟低：投影、scan 实现、状态精度和融合都会影响结果。

状态读写与 scan 的具体计数见 [SSM 工作负载](../06-chip-workload-analysis/ssm-workload.md)。与 attention 的比较应使用同等质量和执行阶段，不以“线性取代平方”代替实验。

## 来源与延伸

- [Mamba：选择性状态空间模型](https://arxiv.org/abs/2312.00752)
- [Mamba-2：结构化状态空间对偶性](https://arxiv.org/abs/2405.21060)
