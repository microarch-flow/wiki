# 概念关系图：任务、结构、目标与执行不是同一层

上级：[专题导读](README.md)

<span id="unified-relationship-map" class="workload-legacy-anchor"></span>
<span id="这页在回答什么问题" class="workload-legacy-anchor"></span>
<span id="共享的底座" class="workload-legacy-anchor"></span>
<span id="四条线如何分化又如何交汇" class="workload-legacy-anchor"></span>
<span id="自动驾驶与机器人-vla-的同与异" class="workload-legacy-anchor"></span>
<span id="world-model-的横向角色" class="workload-legacy-anchor"></span>
<span id="横切四条线的三条主线" class="workload-legacy-anchor"></span>
<span id="一句话理解" class="workload-legacy-anchor"></span>


同一个名称可能描述任务，也可能描述模块或训练方式。先把问题分层，再看它们如何组合，可以避免把“CNN、对比学习、VLA、世界模型”排成互斥算法。

## 一张组合图

```mermaid
flowchart TD
  T["任务：输入、输出、成功标准"] --> S["结构：CNN / Transformer / SSM / MoE"]
  T --> L["学习目标：监督 / 对比 / 掩码 / 模仿 / 强化"]
  S --> M["一个确定版本的模型"]
  L --> M
  M --> E["执行：编码 / 自回归 / 采样 / 搜索"]
  C["配置：形状、精度、状态、设备"] --> E
  E --> W["工作量、流量、容量与依赖"]
```

图中箭头表示设计与分析关系，不表示训练和推理一定按此时间顺序运行。

## 三个具体组合

目标检测可以使用 CNN 骨干和集合预测头，训练时使用匹配损失。匹配属于训练职责，不自动进入部署。

VLA 可以使用视觉语言骨干，以模仿数据训练连续动作头；动作头再用 flow matching 采样。训练目标、网络和采样机制分别描述不同问题。

BEVWorld 以 BEV latent 组织场景，用序列 diffusion 预测未来，再解码观测。BEV 与 latent 是表示属性，diffusion 是生成机制，视频是输出之一。

## 从概念走到计量

只有确定模型版本、执行阶段与输入形状后，才能估算资源。参数量没有说明激活峰值，FLOPs 没有说明内存流量，生成长度没有说明 NFE。

继续阅读[张量与成本](tensor-shapes-and-cost.md)及[工作负载分析方法](../06-chip-workload-analysis/workload-analysis-methodology.md)。需要反查缩写时使用[术语表](glossary.md)。
