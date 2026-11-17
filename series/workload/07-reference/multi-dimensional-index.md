# 按问题查阅：从术语找到主文

上级：[专题导读](README.md)

<span id="multi-dimensional-index" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="按算法类别" class="workload-legacy-anchor"></span>
<span id="按算法概念" class="workload-legacy-anchor"></span>
<span id="按应用场景" class="workload-legacy-anchor"></span>
<span id="按第一瓶颈" class="workload-legacy-anchor"></span>
<span id="按硬件资源" class="workload-legacy-anchor"></span>
<span id="按-archax-建模对象" class="workload-legacy-anchor"></span>
<span id="workload-characterization" class="workload-legacy-anchor"></span>


本索引按问题连接不同专题。文章在侧栏只保留一个主要归属，这里提供其他阅读入口。

## 机制与任务

| 想理解的问题 | 首选入口 | 后续 |
| --- | --- | --- |
| 模型训练和部署为何不同 | [任务与阶段](../00-overview/tasks-training-inference.md) | [训练目标](../learning-objectives/README.md) |
| token 数怎样影响成本 | [Attention](../01-foundation-model-components/attention-and-transformer.md) | [Transformer 工作负载](../06-chip-workload-analysis/transformer-workload.md) |
| 固定状态怎样处理长序列 | [Mamba / SSM](../01-foundation-model-components/mamba-and-ssm.md) | [SSM 工作负载](../06-chip-workload-analysis/ssm-workload.md) |
| 激活参数为何少于总参数 | [MoE](../01-foundation-model-components/mixture-of-experts.md) | [MoE 路由与成本](../06-chip-workload-analysis/moe-workload.md) |
| 对比、重建与预测有何不同 | [表示学习导读](../learning-objectives/README.md) | [JEPA](../learning-objectives/jepa-and-self-supervised.md) |
| 扩散与 flow 要调用几次 | [生成机制](../generative-models/README.md) | [世界模型调用图](../06-chip-workload-analysis/world-model-workload.md) |
| 看图说话怎样变成动作 | [VLM](../language-and-multimodal/vision-language-models.md) | [VLA](../04-robotics-and-vla/vla-fundamentals.md) |
| 检测、分割、BEV 和占用如何区分 | [感知导读](../02-vision-and-3d-perception/README.md) | [Occupancy](../02-vision-and-3d-perception/occupancy-prediction.md) |

## 决策与资源

| 想解决的问题 | 首选入口 | 后续 |
| --- | --- | --- |
| 预测、规划、控制的边界 | [决策接口](../decision-and-policy/prediction-planning-control.md) | [模仿与强化](../decision-and-policy/imitation-and-reinforcement-learning.md) |
| 开放环结果能说明什么 | [数据与仿真](../03-autonomous-driving-algorithms/data-closed-loop-and-simulation.md) | [驾驶规划](../03-autonomous-driving-algorithms/planning-oriented-e2e.md) |
| 动作频率如何转成计算次数 | [动作表示](../04-robotics-and-vla/action-tokenizer.md) | [VLA 工作负载](../06-chip-workload-analysis/vla-workload.md) |
| latent、BEV、视频是否互斥 | [世界模型基础](../05-world-model-and-generative/world-model-fundamentals.md) | [BEVWorld 案例](../05-world-model-and-generative/bev-world-model.md) |
| 如何计算容量与流量 | [张量与计数](../00-overview/tensor-shapes-and-cost.md) | [分析方法](../06-chip-workload-analysis/workload-analysis-methodology.md) |
| 如何比较端侧与云端 | [端侧约束](../06-chip-workload-analysis/edge-inference-chip-requirements.md) | [端云协作](../06-chip-workload-analysis/edge-cloud-collaborative-world-model.md) |

找论文时使用[代表论文](representative-papers.md)；确认版本和测量条件时使用[来源记录](source-tracking.md)。
