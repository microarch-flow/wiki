---
search:
  exclude: true
---

# 扩散世界模型的条件与成本（历史入口）

上级：[专题导读](README.md)

<span id="扩散世界模型时间长度与采样次数怎样计量" class="workload-legacy-anchor"></span>

<span id="diffusion-for-world-model" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么它有效直觉与类比" class="workload-legacy-anchor"></span>
<span id="三重乘法world-model-的乘法又被乘上步数" class="workload-legacy-anchor"></span>
<span id="在不同输出上的差异同一矛盾不同代价" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


原文的生成机制、环境条件和成本推导分别归入下列主文。旧书签仍可从相应小节继续阅读。

## 输出整段未来还是递推下一步

[世界模型工作负载的两个算例](../06-chip-workload-analysis/world-model-workload.md#两个可复算的例子)用相同候选数与时域，对照逐步递推和整段求值。

## 条件如何影响未来

[BEVWorld 的完整路径](bev-world-model.md#bevworld-的完整路径)跟踪历史观测、动作条件和未来输出，并区分改变动作与改变采样噪声的实验。

## 少步采样的收益需要质量约束

一次更新如何产生下一个样本，见 [DDPM 反向采样](../generative-models/diffusion-models.md#采样时为何反复调用网络)和 [Flow Matching 积分](../generative-models/flow-matching.md#训练一步与生成多步)。求值次数、耗时和质量的计量归入[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)。

## 与动作生成分开

需要执行机器人动作时，转到[动作表示与生成](../04-robotics-and-vla/action-tokenizer.md)。需要预测未来观测时，转到[世界模型基础](world-model-fundamentals.md)。

<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>

## 来源与延伸

- [DDPM](https://arxiv.org/abs/2006.11239)
- [Flow Matching](https://arxiv.org/abs/2210.02747)
- [BEVWorld](https://arxiv.org/abs/2407.05679)
- [Diffusion Policy](https://arxiv.org/abs/2303.04137)
