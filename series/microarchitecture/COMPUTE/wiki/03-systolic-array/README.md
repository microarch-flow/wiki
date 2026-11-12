# 03 · Systolic Array：局部复用与数据流

本章讨论 PE 阵列如何接收、复用和传递数据。不同 dataflow 改变跨边界流量；面积、带宽、延迟和能耗需要分别评估。

1. [为什么要 systolic array](./why-systolic-array.md)：PE 局部传递与带单位的边界流量例子。
2. [Dataflow 分类](./dataflow-taxonomy.md)：weight、output、row stationary 的复用位置。
3. [权重载入与 trickle-feed](./weight-loading-and-trickle-feed.md)：x 宽通道、y 拍加载、冷启动与双 bank 重叠。
4. [阵列 sizing](./array-sizing-tradeoff.md)：阵列、RF、利用率和带宽的权衡。

下一章讨论[时钟与流水](../04-clocking-and-pipeline/README.md)。
