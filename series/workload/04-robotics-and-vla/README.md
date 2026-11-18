# 机器人策略与视觉语言动作模型导读

上级：[算法与模型](../README.md)

<span id="robotics-and-vla" class="workload-legacy-anchor"></span>
<span id="这章在回答什么问题" class="workload-legacy-anchor"></span>
<span id="主线" class="workload-legacy-anchor"></span>
<span id="页面列表" class="workload-legacy-anchor"></span>
<span id="到-06-的映射" class="workload-legacy-anchor"></span>

<!-- nav-title: 机器人策略与视觉语言动作模型 -->


先读[图文模型](../language-and-multimodal/vision-language-models.md)，弄清策略收到哪些特征。本章从动作接口进入模型案例。读离散动作前先看[自回归](../generative-models/autoregressive-generation.md)，读连续动作前先看[扩散](../generative-models/diffusion-models.md)与 [Flow Matching](../generative-models/flow-matching.md)。最后一篇使用[世界模型](../05-world-model-and-generative/latent-world-model.md)比较机器人动作，需要知道候选怎样被评分。

<span id="阅读方式" class="workload-legacy-anchor"></span>

## 阅读顺序

1. [VLA 基础](vla-fundamentals.md)
2. [动作表示与生成](action-tokenizer.md)
3. [RT-1 与 RT-2](rt-series.md)
4. [OpenVLA 原模型](openvla.md)
5. [GR00T N1](groot.md)
6. [机器人世界模型](robot-world-model.md)

## 阅读边界

语言和图文编码见[多模态模型](../language-and-multimodal/README.md)，环境转移模型见[世界模型](../05-world-model-and-generative/README.md)。动作生成本身不等于环境预测。
