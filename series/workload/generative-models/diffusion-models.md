# 扩散模型：学习去噪，再逐步生成样本

上级：[专题导读](README.md)

<span id="diffusion-models" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与那个决定性的乘积" class="workload-legacy-anchor"></span>
<span id="三个部署变体把成本压在不同地方" class="workload-legacy-anchor"></span>
<span id="与-autoregressive-生成的硬件性格对比" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


扩散模型用加噪过程构造训练任务，再学习反向生成过程。它可以生成图像、场景表示或动作序列；生成对象决定任务，不能仅凭使用 diffusion 就称为世界模型。

## 训练时如何构造输入

以 DDPM 的噪声预测参数化为例，$x_0$ 是真实样本，$\epsilon\sim\mathcal N(0,I)$。选择时间步 $t$，直接构造：

$$
x_t=\sqrt{\bar\alpha_t}x_0+\sqrt{1-\bar\alpha_t}\epsilon
$$

网络输入 $x_t,t$ 及可选条件 $c$，预测噪声 $\epsilon_\theta(x_t,t,c)$。常见简化目标为：

$$
\mathcal L=\mathbb E\|\epsilon-\epsilon_\theta(x_t,t,c)\|_2^2
$$

这里 $\bar\alpha_t$ 是噪声日程中系数的累积乘积。训练不需要为每个样本先逐步走完全部加噪过程；一个训练样本常随机抽取一个时间步。反向传播成本另计。

## 采样时为何反复调用网络

采样从噪声开始，根据预测结果更新当前样本，再进入下一时间点。DDPM、DDIM 和其他采样器采用不同更新规则，确定性或随机性也可能不同。训练目标、时间步日程和采样器需要配套，不能任意减少步数而假定质量不变。

用 NFE（网络函数求值次数）计成本，比只写“采样步数”更明确：一个数值求解步可能调用网络多次。无分类器引导也可能需要有条件与无条件两次预测；实现可合批，但总工作量仍需计入。

构造例：一个网络一次同时处理未来 16 个时刻的特征，采样共调用 10 次，则主干调用数为 10，**不是 160**。只有单次网络调用只推进一个时刻、且沿时间递推 16 次时，才另乘时间长度。

## 像素、latent 与条件是不同维度

Latent diffusion 先用编码器压缩数据，在 latent 中生成，再由解码器还原。压缩可降低生成器处理的空间规模，但引入编码误差与解码成本。若应用最终要图像，不能因为内部使用 latent 就删去解码器。

条件可来自文本、历史帧、地图、动作或机器人状态。预测未来环境需要环境演化目标与相应条件；[Diffusion Policy](../04-robotics-and-vla/action-tokenizer.md)生成动作，本身不等于环境动力学模型。

## 与其他生成方式比较

[自回归生成](autoregressive-generation.md)通常沿输出顺序逐项生成；扩散常在一次求值中同时更新整个输出。并行更新不等于只有一次求值。[Flow matching](flow-matching.md)学习连续路径上的速度场，可用 ODE 求解器生成；两类方法有联系，但训练目标与采样口径应分别注明。

质量应按目标任务评估。图像清晰、动作平滑或视频连续，都不足以单独证明物理正确性或闭环控制可靠性。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [DDPM](https://arxiv.org/abs/2006.11239)
- [DDIM](https://arxiv.org/abs/2010.02502)
- [Latent Diffusion](https://arxiv.org/abs/2112.10752)
- [Classifier-Free Guidance](https://arxiv.org/abs/2207.12598)
