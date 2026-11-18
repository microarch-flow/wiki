# Latent 世界模型：压缩状态怎样服务学习与规划

上级：[专题导读](README.md)

<span id="latent-world-model" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="基本结构与-rollout-的状态递推" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


Latent 世界模型在学习到的内部表示中预测未来。它可能减少与任务无关的细节，但是否使用解码器、随机状态或多步采样，取决于训练和部署路径。

## DreamerV3：在想象中训练策略

DreamerV3 的循环状态空间模型包含确定性递推状态和分类随机 latent。训练还使用观测解码器、奖励预测与继续概率等头。actor-critic 在模型生成的想象轨迹上学习。

在真实环境中，上一状态和已执行动作先产生新的确定性状态，观测编码提供证据来估计同一时刻的随机状态。actor 读取两者后选择动作。每个控制节拍都要为观测编码与状态更新计费。原论文在这一阶段直接从策略选动作，候选轨迹搜索的成本只适用于实际执行搜索的系统。

<span id="与-jepa-的关系从表征学习走到可行动" class="workload-legacy-anchor"></span>

## V-JEPA 2-AC：预测目标表示来规划

V-JEPA 2 先做无动作视频表征预训练；2-AC 用机器人数据学习动作条件预测，再以目标图像的表示距离作为规划代价，通过 CEM 搜索动作。每次执行首个动作后重新规划。

目标距离只是一个任务代价，不能替代所有碰撞或接触约束。原论文 v1 的特定 RTX 4090 规划实验报告每动作约 16 s，说明“latent 预测”与“满足高频控制”之间还隔着候选搜索等成本。

## 何时可以不解码

如果代价与策略直接消费 latent，在线路径可以不生成像素；训练时仍可能依赖解码损失。若用户需要未来图像，则必须运行相应解码器。BEVWorld 还说明 latent 预测本身可以采用 diffusion。

构造例：编码器输出 $16\times16\times256$ 的 FP16 特征，共 128 KiB。它虽小于原始高分辨率图像的一些中间特征，却不是“几百维向量”。状态大小必须用真实形状描述。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 压缩的收益与边界

表示应保留任务相关信息，但训练目标可能忽略未来决策需要的细节。单步预测误差小，不保证长时间 rollout 无偏；规划器还可能利用模型误差选出看似优良的动作。

是否适合端侧部署，应测完整路径和质量约束。本文不保留“latent 是唯一可部署路线”“必定省一两个数量级”等无统一条件的结论。

## 来源与延伸

- [DreamerV3 原论文 v2](https://arxiv.org/html/2301.04104v2)
- [V-JEPA 2 / 2-AC 原论文 v1](https://arxiv.org/html/2506.09985v1)
- [BEVWorld 原论文 v3](https://arxiv.org/html/2407.05679v3)
