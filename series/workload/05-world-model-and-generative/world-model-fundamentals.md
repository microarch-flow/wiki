# 世界模型基础：预测对象、条件与用途

上级：[专题导读](README.md)

<span id="world-model-fundamentals" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="基本形式dynamics-是核心rollout-是计算骨架" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


世界模型学习环境的状态或观测如何随时间变化，用于预测、策略学习、规划或生成测试环境。它不是视频生成的同义词，也没有唯一的内部表示。阅读论文时，先写清预测对象、条件、用途和实际调用路径。

## 从部分观测建立状态

智能体通常只能看到传感器观测 $o_t$，不能直接访问完整环境状态。模型可用历史构造内部状态 $z_t$，再预测未来：

$$
z_t=E(o_{\le t},a_{<t}),\qquad
p_\theta(z_{t+1}\mid z_t,a_t)
$$

这是动作条件的一步转移示意，不是所有世界模型的统一实现。模型也可能直接预测多个未来时刻，或预测无动作条件的视频分布。需要比较不同动作后果时，必须明确动作如何进入模型；若没有动作条件，就不能直接把预测解释为候选动作的反事实结果。

<span id="四个互相独立的分类轴" class="workload-legacy-anchor"></span>

## 用五个问题描述同一个模型

| 属性 | 要回答的问题 | BEVWorld 的例子 |
| --- | --- | --- |
| 内部表示 | 状态存成什么、按什么坐标组织 | 相机与 LiDAR 编码成鸟瞰坐标中的隐特征 |
| 预测机制 | 下一段状态怎样得到 | 序列扩散模型逐次更新未来隐特征 |
| 条件输入 | 哪些信息在预测时已经可用 | 历史特征和高层动作 token |
| 预测输出 | 模块交给下游什么 | 预测器输出未来 BEV latent，解码器可生成多视图图像和点云 |
| 系统用途 | 谁使用这些结果 | 用未来观测研究驾驶场景演化，评估感知与运动预测任务 |

这些属性有接口约束。例如，规划器若要比较两个自车动作，预测器必须能接收相应动作或轨迹条件，输出也必须能用同一代价函数评分。仅从历史占用联合预测未来占用和自车轨迹，可以服务预测任务，但还缺少替换候选动作的接口。两种实例见 [BEVWorld](bev-world-model.md) 和 [OccWorld](occupancy-world-model.md)。

## 模型怎样进入决策

```mermaid
flowchart TD
  O["真实观测"] --> E["状态编码"]
  E --> M["环境预测模型"]
  A["动作等条件<br/>（若使用）"] --> M
  M --> Z["预测状态、观测<br/>或回报"]
  Z --> T["训练<br/>策略"]
  Z --> P["在线<br/>比较候选"]
  Z --> D["生成数据<br/>或测试场景"]
```

图中三条分支表示预测结果的使用方式。DreamerV3 的想象轨迹用于训练。真实交互时，观测编码与状态更新产生 actor 的输入。V-JEPA 2-AC 在部署时还会调用预测器，为候选动作评分。两条执行路径见 [Latent 世界模型](latent-world-model.md)。

## 世界模型与视频生成的关系

视频生成可以提供丰富的未来观测，但画面逼真不证明动力学、动作响应和几何一致。相反，只预测 latent 的系统仍可能有效支持策略学习，却不直接给出可视化图像。

判断能否用于某项决策，应检查任务相关预测误差、不同动作下的响应、长时误差累积和闭环结果。模型会预测未来，不等于已经学得完整物理规律。

<span id="三类-world-model同一思想三种-workload-落点" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>

## 成本沿调用路径展开

逐时刻候选 rollout 可按候选数、时间长度和单步成本估算；整段序列 diffusion 的一次求值可能已经包含全部时间位置，不能再重复乘时间长度。候选可批并行，因此工作量乘法也不等于墙钟时延乘法。

后续分别讨论[视频输出](video-world-model.md)、[BEV](bev-world-model.md)、[占用](occupancy-world-model.md)和 [latent](latent-world-model.md)的接口；成本统一到[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [World Models](https://arxiv.org/abs/1803.10122)
- [DreamerV3 原论文 v2](https://arxiv.org/html/2301.04104v2)
- [BEVWorld 原论文 v3](https://arxiv.org/html/2407.05679v3)
- [V-JEPA 2 / 2-AC 原论文 v1](https://arxiv.org/html/2506.09985v1)
