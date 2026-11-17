---
search:
  exclude: true
---

# 世界模型与视频生成：关系速查

上级：[专题导读](README.md)

<span id="world-model-is-not-video-generation" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么这个区分成立直觉与类比" class="workload-legacy-anchor"></span>
<span id="常见误解-实际上" class="workload-legacy-anchor"></span>
<span id="为什么这个区分直接改变-workload" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="演进与未来方向判断" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>
<span id="参考来源" class="workload-legacy-anchor"></span>


世界模型可以生成视频，也可以只预测状态、latent、占用或回报。视频生成是否能用于环境决策，取决于时间一致性、条件控制和任务验证。

## 三个常见问题

**有未来视频就能规划吗？** 还需要动作如何改变未来的接口、可比较的代价，以及预测和闭环证据。单帧逼真不足以满足这些条件。

**使用 latent 就没有 decoder 吗？** 不一定。DreamerV3 在训练中使用观测 decoder；BEVWorld 从 BEV latent 解码图像和点云。是否在线调用，应看部署路径。

**所有世界模型都必须输入动作吗？** 不是统一定义。但要比较不同动作的后果，就必须说明动作条件或等效干预机制；无动作预测不能直接承担这个职责。

## 继续阅读

完整定义与分类已合并到[世界模型基础](world-model-fundamentals.md)。需要比较模型时，依次检查表示、预测机制、条件和用途，再到[工作负载分析](../06-chip-workload-analysis/world-model-workload.md)计量成本。

本页保留原公开入口和锚点，避免旧引用失效。
