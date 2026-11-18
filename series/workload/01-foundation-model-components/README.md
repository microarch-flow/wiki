# 网络组件与序列建模导读

上级：[算法与模型](../README.md)

<span id="骨干网络与序列建模导读" class="workload-legacy-anchor"></span>

<span id="foundation-model-components" class="workload-legacy-anchor"></span>
<span id="这章在回答什么问题" class="workload-legacy-anchor"></span>
<span id="本章定位" class="workload-legacy-anchor"></span>
<span id="页面列表" class="workload-legacy-anchor"></span>
<span id="本章到-06-的映射" class="workload-legacy-anchor"></span>

<!-- nav-title: 网络组件与序列建模 -->


从 CNN 开始看局部特征，再看不同尺度怎样融合。接着用 Attention 建立位置间交换信息的计算图，再读它在 ViT 与 Swin 中的两种组织方式。后面的 SSM 和 MoE 分别处理时序状态与专家选择。第一次阅读可先熟悉[张量的轴、广播和归约](../00-overview/tensor-shapes-and-cost.md)。

## 阅读顺序

1. [CNN 骨干](cnn-backbone.md)
2. [多尺度特征融合](neck-feature-fusion.md)
3. [Attention 与 Transformer](attention-and-transformer.md)
4. [ViT 与 Swin](vision-transformer-backbone.md)
5. [Attention 效率](attention-variants-and-efficiency.md)
6. [Mamba 与 SSM](mamba-and-ssm.md)
7. [混合专家 MoE](mixture-of-experts.md)

## 阅读边界

训练目标见[表示学习](../learning-objectives/README.md)，完整运行成本见[工作负载分析](../06-chip-workload-analysis/README.md)。骨干名称不等于任务名称。
