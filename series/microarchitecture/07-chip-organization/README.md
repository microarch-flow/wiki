# 处理单元与片上组织

<span class="micro-legacy-anchor" id="07-芯片顶层组织"></span>


前面分别看过指令、执行通道、脉动阵列和搬运引擎。现在给定同一块矩阵，看看这些资源怎样配合，再把矩阵切给两个单元，追踪新增加的数据传递。

## 阅读顺序

1. [三种处理器怎样算同一块矩阵](./cpu-vs-gpu-core-area.md)　沿 CPU、GPU 和 NPU 三条执行路径逐一找到操作数、乘加和部分和。
2. [矩阵分给两个单元时的数据传递](./gpu-as-tiled-tpu.md)　深入看两种切分分别要把输入、部分和送到哪里。

基础机制见[指令执行](../03-instruction-execution/README.md)和[SIMD、向量、SIMT](../04-parallel-execution/simd-vector-simt.md)。[功率与能量](../09-power-implementation/brain-vs-chip-power.md)和[建模建议](../reading-and-reference/03-modeling/README.md)分别归入实现权衡和分析方法。
