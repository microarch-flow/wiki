# 处理单元与片上组织

<span class="micro-legacy-anchor" id="07-芯片顶层组织"></span>


本专题比较控制、算术、寄存器、局部存储与互连怎样组成处理单元和芯片。先固定层级：CPU core、GPU SM、矩阵执行单元和整芯片不是等价对象。

## 阅读顺序

1. [CPU 与 GPU 的资源组织](./cpu-vs-gpu-core-area.md)：控制、并行执行与存储的设计取舍。
2. [GPU 与 TPU 的片上组织](./gpu-as-tiled-tpu.md)：局部矩阵资源、共享边界与跨单元通信。

基础机制见[指令执行](../03-instruction-execution/README.md)和[SIMD、向量、SIMT](../04-parallel-execution/simd-vector-simt.md)。[功率与能量](../09-power-implementation/brain-vs-chip-power.md)和[建模建议](../reading-and-reference/03-modeling/README.md)分别归入实现权衡和分析方法。
