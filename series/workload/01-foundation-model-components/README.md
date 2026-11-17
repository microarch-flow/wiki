# 骨干网络与序列建模导读

上级：[算法与模型](../README.md)

<span id="foundation-model-components" class="workload-legacy-anchor"></span>
<span id="这章在回答什么问题" class="workload-legacy-anchor"></span>
<span id="本章定位" class="workload-legacy-anchor"></span>
<span id="页面列表" class="workload-legacy-anchor"></span>
<span id="本章到-06-的映射" class="workload-legacy-anchor"></span>

<!-- nav-title: 骨干网络与序列建模 -->


这里解释可复用的网络组件：输入怎样变成特征，位置或时间之间怎样交换信息。对比学习等训练目标、扩散等生成机制已分到各自专题。

## 阅读顺序

1. [CNN 骨干](cnn-backbone.md)
2. [ViT 与 Swin](vision-transformer-backbone.md)
3. [多尺度特征融合](neck-feature-fusion.md)
4. [Attention 与 Transformer](attention-and-transformer.md)
5. [Attention 效率](attention-variants-and-efficiency.md)
6. [Mamba 与 SSM](mamba-and-ssm.md)
7. [混合专家 MoE](mixture-of-experts.md)

## 阅读边界

训练目标见[表示学习](../learning-objectives/README.md)，完整运行成本见[工作负载分析](../06-chip-workload-analysis/README.md)。骨干名称不等于任务名称。
