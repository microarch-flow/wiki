# 并行执行与计算阵列

<span class="micro-legacy-anchor" id="03-systolic-array局部复用与数据流"></span>


本专题先区分软件可见的并行模型，再讨论 PE 阵列如何接收、复用和传递数据。不同 dataflow 改变跨边界流量；面积、带宽、延迟和能耗需要分别评估。

## 阅读顺序

1. [SIMD、向量与 SIMT](./simd-vector-simt.md)：软件对象、活动掩码与物理执行宽度。
2. [Systolic 阵列逐拍执行](./why-systolic-array.md)：2×2 矩阵的逐拍轨迹、停顿和排空。
3. [Dataflow 分类](./dataflow-taxonomy.md)：weight、output、row stationary 的复用位置。
4. [权重载入与 trickle-feed](./weight-loading-and-trickle-feed.md)：x 宽通道、y 拍加载、冷启动与双 bank 重叠。
5. [阵列 sizing](./array-sizing-tradeoff.md)：阵列、RF、利用率和带宽的权衡。

下一章讨论[时钟与流水](../02-pipeline/README.md)。
