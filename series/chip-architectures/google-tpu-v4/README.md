# Google TPU v4 怎样分工处理矩阵乘与 embedding

推荐模型的一次前向计算可以同时包含稠密矩阵乘法和 embedding 查表。矩阵乘法能重复使用规则排列的数据块。查表由输入索引决定访问位置，向量还可能分布在多颗芯片上。TPU v4 为这两类工作分别提供 TensorCore 和 SparseCore。 [TPU v4 原论文，第 3 节](https://arxiv.org/abs/2304.01433v3)

## 规则分块交给 MXU

一颗 TPU v4 有两个 TensorCore，每个包含四个矩阵乘单元（MXU）、向量单元和标量单元。两个 TensorCore 使用统一的 32 GiB HBM 地址空间。可供应用分配的容量还要扣除系统和运行时保留空间。 [Google Cloud TPU v4 架构](https://docs.cloud.google.com/tpu/docs/v4#system_architecture)

以矩阵乘法为例，程序将操作数划分成适合阵列的块。芯片有两个 TensorCore 各自的向量存储（VMEM），还有共享的片上存储（CMEM）。映射可以将一块 HBM 数据搬到靠近计算的缓冲，再交给 MXU 做乘加。向量单元可继续处理逐元素计算，将结果交给后续操作或者写回。阵列利用率取决于块形状和数据能否持续供应。这个顺序表示功能路径，实际路径与调度由编译结果决定。 [Google Hot Chips 2023，芯片框图](https://hc2023.hotchips.org/assets/program/conference/day2/ML%20training/HC2023.Session5.ML_Training.Google.Norm_Jouppi.Andy_Swing.Final_2023-08-25.pdf#page=4)

## 索引驱动的查表交给 SparseCore

SparseCore 面向 embedding。索引决定读取表中的哪些行，表可能按行分散。TPU v4 每颗芯片有四个 SparseCore。论文描述的 SparseCore 包含读写 HBM 的硬件、局部向量存储、SIMD 运算和跨通道的专用操作单元，可组织数据读取、排序和归约。训练中的反向传播还可以写回更新后的参数。 [TPU v4 原论文，第 3.3 至 3.6 节](https://arxiv.org/abs/2304.01433v3)

下面是一个逻辑示例。假定同一张表按行分片，节点 A 持有第 0 至 3 行，节点 B 持有第 4 至 7 行。节点 A 收到索引 2、5、5，请求按元素求和。

1. 根据分片规则，将索引 2 送到节点 A 的本地查表路径，将索引 5 送到节点 B 的查表路径。
2. 读取索引指定的向量。对重复索引可复用已读向量，归约时要保留出现次数。
3. 汇合两个分片的结果。输出为第 2 行向量与两倍第 5 行向量之和。

例子只说明索引、分片和归约的依赖。真实请求的通信量取决于索引分布、分片、合并策略和批大小。这里的稀疏访问是**从表中选行**。矩阵硬件的 2:4 稀疏则规定某个操作数的非零元素布局，适用条件不同。 [TPU v4 原论文，embedding 案例](https://arxiv.org/abs/2304.01433v3) · [稀疏矩阵乘的结构约束](https://docs.nvidia.com/cuda/cusparselt/)

## 从芯片扩展到 Pod

当表分布到多颗芯片时，读取请求和向量结果可以经过芯片间互连（ICI）。查表可能形成跨节点的 all-to-all 流量，性能由访问热点、HBM 有效带宽、链路负载等共同决定。稠密训练中的参数集合通信也使用系统互连，但消息大小和通信模式可以不同。

TPU v4 Pod 包含 4096 颗芯片。多立方体配置使用光路交换机（OCS）连接各个 4 × 4 × 4 立方体的边界链路，形成选定的拓扑。OCS 改变的是系统链路连接。一个具体任务的通信还由分片与拓扑映射决定。 [Google Cloud TPU v4 文档的 Configurations 小节](https://docs.cloud.google.com/tpu/docs/v4) · [Google Cloud TPU 互连架构](https://docs.cloud.google.com/tpu/docs/system-architecture-tpu-vm)

## 接下来怎么读

- 了解推荐推理如何在另一款芯片上放置 embedding、权重和激活。 [Meta MTIA 1 与 2i](../Meta_MTIA/README.md)
- 比较 HBM 到局部工作缓冲的显式供数。 [NVIDIA H100 SXM](../nvidia-h100-sxm/README.md)
