# 模型加载与执行计划

上级：[推理运行时](../README.md)

本专题解释模型怎样成为设备上的执行工作。模型结构、权重、形状与后端是输入；可提交的算子计划及完成事件是输出。

## 阅读顺序

1. [模型加载与执行后端](model-loading.md)
2. [动态形状与数据布局](dynamic-shapes.md)
3. [CPU 与设备协作](host-device-execution.md)

## 本专题的边界

动态形状属于执行表示，连续批处理属于请求选择。这里讨论二者的交接，不重复调度策略。

前置阅读：[完整请求路径](../01-request-and-metrics/request-path.md)中的引擎与执行器职责。继续阅读：[算子内核与低精度执行](../03-kernels-and-precision/README.md)。
