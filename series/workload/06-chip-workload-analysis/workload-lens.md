---
search:
  exclude: true
---

# 从算法到工作负载：阅读入口

上级：[专题导读](README.md)

<span id="workload-lens" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="为什么需要一个固定的视角" class="workload-legacy-anchor"></span>
<span id="这副眼镜的五个反射动作" class="workload-legacy-anchor"></span>
<span id="这副眼镜最容易纠正的四个直觉错误" class="workload-legacy-anchor"></span>
<span id="这副眼镜怎么连到硬件和-archax" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>
<span id="怎么用这页" class="workload-legacy-anchor"></span>


算法说明任务与机制，工作负载说明它在一个确定配置中怎样执行。二者之间需要补齐输入形状、阶段、状态、实现和时限。

## 从哪里开始

先读[张量形状与计算量](../00-overview/tensor-shapes-and-cost.md)，掌握 MAC、FLOP、容量与流量的区别。再按[工作负载分析方法](workload-analysis-methodology.md)画执行图、计算资源并验证假设。

需要填写实验记录时使用[记录字段](workload-characterization-axes.md)；需要选择案例时使用[工作负载比较索引](workload-comparison-table.md)。

## 一个最小检查

“世界模型要乘候选数和预测长度”还不完整。必须先说明单次调用是否已经覆盖整段未来，以及候选是否合批。定义清楚后才能计算工作量；延迟还需结合依赖和硬件。

本页原有的方法说明已合并到主文，保留旧公开入口和锚点。
