# 驾驶世界模型：预测未来、比较动作与生成测试场景

上级：[专题导读](README.md)

<span id="world-model-for-autonomous-driving" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="三类-world-model-与两种用法" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


驾驶世界模型用于描述环境随时间的演化。它可以预测观测、场景表示或交通状态，并服务训练、规划或测试。不同用途需要不同条件与评估，不能把“能生成未来视频”直接当作“能可靠规划”。

## 三个用途有三种接口

预测模块根据历史输出未来场景，帮助下游理解可能变化。候选评估模块还需要动作或轨迹条件，比较不同自车行为的后果。数据生成模块则输出训练或测试材料，可能完全离线运行。

BEVWorld 在 BEV latent 中建模多模态未来，并使用高层动作条件；OccWorld 从历史 occupancy 联合预测未来 occupancy 与自车轨迹。二者不能统一解释为同一种候选动作 MPC 接口。

## 反事实需要什么证据

在一段记录中，车辆实际只执行了一条动作轨迹。模型学到这段未来，并不自动说明它能准确预测其他动作的后果。动作覆盖、环境响应以及分布外行为都需要验证。

构造例：自车提前减速会影响后车跟驰。若生成器只移动自车视角、其他车辆仍按固定记录行驶，它没有完整模拟这种交互。这个限制应进入测试结论。

## 生成质量与任务质量

视觉质量指标可以检查图像分布，但未必发现速度不连续、交通规则冲突或几何穿透。规划用途还要看碰撞、可行性、时间一致性和对动作变化的响应。

ReSim 展示了视频生成与学习奖励结合的闭环策略学习研究。其结论应限定到论文模型与实验环境，不能用“闭环”一词推导已验证真实道路安全。

<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 在线与离线成本

离线场景生成可以优先吞吐；在线候选评估要满足决策截止时间。若一次 diffusion 求值已经覆盖整个未来序列，计算次数不能再重复乘预测帧数。调用模型见[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)。

表示与生成机制的关系见[世界模型基础](../05-world-model-and-generative/world-model-fundamentals.md)，评估环境见[数据闭环与仿真](data-closed-loop-and-simulation.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [BEVWorld](https://arxiv.org/abs/2407.05679)
- [OccWorld](https://arxiv.org/abs/2311.16038)
- [ReSim](https://arxiv.org/abs/2506.09981)
