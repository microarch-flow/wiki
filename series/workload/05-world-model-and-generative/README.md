# 世界模型与环境预测导读

上级：[算法与模型](../README.md)

<span id="world-model-and-generative-intelligence" class="workload-legacy-anchor"></span>
<span id="这章在回答什么问题" class="workload-legacy-anchor"></span>
<span id="主线" class="workload-legacy-anchor"></span>
<span id="页面列表" class="workload-legacy-anchor"></span>
<span id="到-06-的映射" class="workload-legacy-anchor"></span>

<!-- nav-title: 世界模型与环境预测 -->


一个模型可以在鸟瞰坐标（BEV）中维护隐状态（latent），预测未来，再解码为视频。读导读时先确定你关心的问题。Latent 一篇解释状态怎样服务策略或规划，BEV 一篇解释空间组织，视频和占用两篇分别解释未来观测与空间语义。各案例的表示、机制、条件、输出与用途在[世界模型基础](world-model-fundamentals.md)中对照。

## 阅读顺序

1. [世界模型基础](world-model-fundamentals.md)
2. [Latent 世界模型](latent-world-model.md)
3. [视频世界模型](video-world-model.md)
4. [BEV 世界模型](bev-world-model.md)
5. [占用世界模型](occupancy-world-model.md)

## 原入口

这些页面保留旧引用，完整内容已合并到对应主文。

1. [世界模型与视频关系速查](world-model-is-not-video-generation.md)
2. [扩散世界模型的条件与成本](diffusion-for-world-model.md)

## 阅读边界

生成机制基础见[自回归与扩散](../generative-models/README.md)；部署位置和成本见[世界模型工作负载](../06-chip-workload-analysis/world-model-workload.md)。
