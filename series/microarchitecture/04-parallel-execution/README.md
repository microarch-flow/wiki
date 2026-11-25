# 并行执行与计算阵列

<span class="micro-legacy-anchor" id="03-systolic-array局部复用与数据流"></span>


十个加法彼此独立，可以分给几条通道一起做。换成矩阵乘，阵列里的四个乘加单元却要在不同的拍等到各自的输入。先逐拍画出这两种分工，再追问哪些数据值得留在单元里反复用。

## 阅读顺序

1. [十个加法怎样分给执行通道](./simd-vector-simt.md)　用 SIMD、向量和 SIMT 安排十个元素，观察最后一组有几条通道会写出结果。
2. [四个乘加单元怎样做八次乘加](./why-systolic-array.md)　逐拍看一个 2×2 脉动阵列里哪几个单元开工，区分算出结果和把它送出。
3. [Dataflow 分类](./dataflow-taxonomy.md)：weight、output、row stationary 的复用位置。
4. [权重载入与 trickle-feed](./weight-loading-and-trickle-feed.md)：x 宽通道、y 拍加载、冷启动与双 bank 重叠。
5. [阵列 sizing](./array-sizing-tradeoff.md)：阵列、RF、利用率和带宽的权衡。

接下来要处理另一块数据，读《[第一块还在算，第二块能开始搬吗？](../06-task-control/dma-compute-writeback.md)》。要回看每拍何时采样，见[流水线、时序与时钟域](../02-pipeline/README.md)。
