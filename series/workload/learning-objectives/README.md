# 表示学习与训练目标导读

上级：[算法与模型](../README.md)

<!-- nav-title: 表示学习与训练目标 -->


训练目标规定模型要从数据中学习什么。本专题比较样本关系、掩码重建、蒸馏和表征预测；它们可以使用相同骨干，但监督信号不同。

## 阅读顺序

1. [对比学习](contrastive-learning.md)
2. [掩码重建与自蒸馏](masked-reconstruction-and-distillation.md)
3. [JEPA 表征预测](jepa-and-self-supervised.md)

## 阅读边界

训练时的教师、掩码或全对比损失未必进入部署路径。先读[训练与推理](../00-overview/tasks-training-inference.md)，再区分表征学习与[生成机制](../generative-models/README.md)。
