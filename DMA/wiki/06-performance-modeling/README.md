# 06 性能建模与调优

这一部分面向工程判断。前面几章已经把 DMA 的对象、微架构、软件契约和系统耦合拆开；这一章回答的是：如果要把这些知识变成实验设计、性能模型和调优路径，应该保留哪些状态、量哪些指标、先怀疑哪里。

## 推荐阅读顺序

1. [指标、瓶颈与实验设计](./metrics-bottlenecks.md)
2. [从抽象模型到系统诊断](./modeling-method.md)
3. [优化与调参手册](./optimization-playbook.md)
4. [观测、计数器与调试路径](./debug-observability.md)

如果你的目标是**开发性能建模 / 架构探索工具**，建议改读这条规格向的路径：

1. [从抽象模型到系统诊断](./modeling-method.md) —— 先定层次
2. [参数与公式速查](./parameter-reference.md) —— 拿到可计算的参数与公式
3. [模型数据结构与事件规范](./model-schema.md) —— 统一字段与事件命名
4. [指标、瓶颈与实验设计](./metrics-bottlenecks.md) —— 定义采样点
5. [校准与验证](./calibration-validation.md) —— 用 counter 标定参数、验证趋势
6. [旋钮敏感度与耦合](./sensitivity-coupling.md) —— 剪枝设计空间，决定该扫哪些维度

## 本章输出物

- 一套指标口径：submit、service、completion、consumer-ready 分别怎么量
- 一条建模主线：先做最小可解释模型，再按瓶颈逐层补真实度
- 一份调优顺序：先验证定义和边界，再扫粒度、并发和系统冲突
- 一份建模规格：[参数与公式速查](./parameter-reference.md) + [统一数据结构与事件链](./model-schema.md)
