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

DDPM 从标准高斯噪声 $x_T$ 开始。在第 $t$ 步，网络看见 $x_t$ 和时刻，给出噪声估计 $\hat\epsilon$。训练时不同干净样本和噪声可能产生相似的 $x_t$。平方损失学到的是这个条件下的平均噪声方向。采样器用该方向确定下一步分布的中心，再按选定的方差采样。

令 $\beta_t$ 为前向每步加噪的方差系数，$\alpha_t=1-\beta_t$，$\bar\alpha_t=\prod_{j=1}^t\alpha_j$。在噪声预测参数化下，反向一步为

$$
\mu_\theta=\frac{1}{\sqrt{\alpha_t}}
\left(x_t-\frac{\beta_t}{\sqrt{1-\bar\alpha_t}}\hat\epsilon\right).
$$

当 $t>1$ 时，独立抽取 $z\sim\mathcal N(0,I)$，令 $x_{t-1}=\mu_\theta+\sigma_t z$。最后一步取 $z=0$。所得 $x_{t-1}$ 正是下一次网络的输入。[DDPM 原论文，式 11 与算法 2](https://arxiv.org/html/2006.11239v2)

**手算采样链的最后两步。** 设 $\alpha_1=\alpha_2=0.8$，当前标量 $x_2=0.6$，网络预测噪声 0.3。此时 $\bar\alpha_2=0.64$，反向均值为 $(0.6-0.2\times0.3/0.6)/\sqrt{0.8}\approx0.5590$。本例取 DDPM 的固定后验方差 $\sigma_2^2=\beta_2(1-\bar\alpha_1)/(1-\bar\alpha_2)=1/9$。若这次抽到 $z=0.3$，则 $x_1\approx0.6590$。网络在 $t=1$ 重新读取这个值。若此时预测噪声为 0，最后输出 $x_0=x_1/\sqrt{0.8}\approx0.7368$。日程、两次网络输出和随机数都是构造值。

用 NFE（网络函数求值次数）计成本，比只写“采样步数”更明确：一个数值求解步可能调用网络多次。无分类器引导也可能需要有条件与无条件两次预测；实现可合批，但总工作量仍需计入。

不同采样器按各自规则使用网络预测。DDIM 可以采用确定性更新。比较采样代价时记录采样器、时间日程、实际求值次数和质量。对整段未来进行采样的计数例见[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)。

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
