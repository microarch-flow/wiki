# 机器人世界模型：预测怎样进入策略学习或规划

上级：[专题导读](README.md)

<span id="robot-world-model" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="world-model-怎么接进机器人系统" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


机器人世界模型预测动作之后的状态或观测，用于学习策略、选择动作或构造训练数据。它与直接生成动作的策略具有不同职责。二者可以在同一系统内共同使用。

## 三种调用方式

第一种用想象轨迹训练策略。以 DreamerV3 为例，每次真实交互仍需编码新观测，结合上一步动作更新循环状态，再由 actor 根据当前状态选择动作。训练时展开的多步想象属于另一条调用路径。两条路径的输入和更新步骤见 [Latent 世界模型](../05-world-model-and-generative/latent-world-model.md)。

第二种在部署时比较候选动作。系统把当前观测编码成状态，预测不同动作序列的结果，根据目标代价选出动作，然后重新观测。V-JEPA 2-AC 使用表征预测与 CEM 搜索，是明确的案例。

第三种生成观测或场景，用于数据扩增与测试。生成数据若改变了物理关系、动作标签或接触结果，会把错误带入策略训练，必须检查。

## 一个候选规划例子

构造例：当前夹爪位于物体左侧，规划器比较“直接闭合”和“先移动再闭合”两条候选序列。世界模型预测两者的后续状态，代价函数比较目标距离、碰撞和约束。规划器选择动作，模型本身不自动决定哪个目标重要。

若只训练了无动作条件的视频预测器，它学到的可能是数据中常见的未来，不能直接回答“换一个动作会怎样”。动作条件也不自动证明因果正确，数据覆盖和反事实验证仍然重要。

## 接触与模型误差

抓取中的摩擦、接触点和遮挡可能难以从图像准确识别。预测误差会沿 rollout 累积；优化器还可能挑中模型过度乐观的区域。缩短执行段、重新观测和约束检查可缓解，但不能取代真实验证。

## 延迟不能只看 latent 大小

接触发生时，旧的状态估计可能已失效。如果从拍照到动作下发经过多个控制周期，候选的评分针对的是采样时刻的手、物体和夹爪状态。工程上应记录观测时间、规划完成时间、实际接触时间，以及何时重新观测。V-JEPA 2-AC 的搜索配置与计时集中在[规划案例](../05-world-model-and-generative/latent-world-model.md)。

系统分析应分开编码、候选预测、代价计算与执行。定义与模型差异见[世界模型基础](../05-world-model-and-generative/world-model-fundamentals.md)，计算路径见[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [DreamerV3 原论文 v2](https://arxiv.org/html/2301.04104v2)
- [V-JEPA 2 / 2-AC 原论文 v1，表 3](https://arxiv.org/html/2506.09985v1)
