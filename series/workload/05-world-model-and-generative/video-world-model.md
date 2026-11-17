# 视频世界模型：从未来画面到可用环境预测

上级：[专题导读](README.md)

<span id="video-world-model" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="计算结构与那个四维乘积" class="workload-legacy-anchor"></span>
<span id="价值与边界信息完整-可直接规划" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


视频世界模型以未来图像或视频作为可观察输出。内部可以使用离散 token 或连续 latent，再由解码器还原画面。视频输出描述的是接口，不限定模型一定逐像素计算。

## 从历史与条件到未来

输入可包含历史帧、文本、动作或轨迹条件。编码器压缩观测，时序模型预测未来表示，解码器生成帧。GAIA-1 使用视频 token 的自回归建模，并连接视频解码过程；Genie 使用视频 tokenizer、动作表示和动态模型构造可交互环境。

不同模型中的动作语义不同：真实控制量、轨迹条件、高层命令或学习到的 latent action，不能互相当作同一接口。

## 一致性比单帧清晰更难

构造例：一辆车在相邻帧中突然改变车道、尺寸或身份，每帧都可能看起来逼真，但运动不连续。多相机输出还需要同一物体在不同视角中具有一致几何，而不是每个视角独立生成一辆相似的车。

评价因此要覆盖时间、视角、几何和条件响应。图像分布指标可提供一种证据，却不能独立证明模型适合碰撞判断或策略优化。

## 输出规模和模型内部规模

构造 6 路相机、每路 16 帧、$256\times448$、RGB uint8 的视频，原始输出约 31.5 MiB。这不包括解码器激活和内部 latent，也不是传输编码后的视频大小。

若压缩器降低空间分辨率，预测器的 token 数会减少，但细节损失和解码成本仍在。动作条件一致性也不能由压缩率推断。

## 适用范围

视频输出适合人工检查、传感器级数据生成和部分可交互环境研究。规划若只需要目标位置或代价，完整图像解码可能不是必要路径；是否省略必须由系统用途决定。

不能断言视频模型永远只能在云端，也不能把某演示的帧率当作所有硬件上的保证。判断部署可行性需要分辨率、视角数、生成长度、NFE、质量目标及设备测量。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [GAIA-1](https://arxiv.org/abs/2309.17080)
- [Genie](https://arxiv.org/abs/2402.15391)
- [BEVWorld：从 BEV latent 解码多模态观测](https://arxiv.org/abs/2407.05679)
