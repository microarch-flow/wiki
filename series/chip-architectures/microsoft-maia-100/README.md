# Microsoft Maia 100 的计算命令何时启动？

输入已经就绪，计算也可能要等。在 Maia 100 中，具有输入和输出的命令还要等到输出缓冲可用。硬件信号量让各个执行单元知道数据何时到达、哪些缓冲可以复用。本文先看微软公开的两级控制，再用一次读、算、写说明这两个条件如何共同起作用。 [微软架构说明](https://techcommunity.microsoft.com/blog/azureinfrastructureblog/inside-maia-100-revolutionizing-ai-workloads-with-microsofts-custom-ai-accelerat/4229118) · [Hot Chips，第 9 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=9)

## Cluster 和 tile 怎样分工

微软的公开架构图给出 16 个 cluster，每个 cluster 有 4 个 tile。Cluster 级有读写拷贝引擎和共享暂存区 CSRAM。Tile 级有自己的读写拷贝引擎、张量单元、向量处理器和 tile SRAM。 [Hot Chips，第 4 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=4) · [第 9 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=9)

在控制路径上，cluster 控制处理器向本级模块提交命令，也能把命令送入 tile 控制处理器的队列。Tile 控制处理器再向本级执行单元的队列提交命令。负责执行命令的硬件线程通过信号量直接同步数据路径上的依赖。 [Hot Chips，第 9 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=9)

## 信号量怎样保护缓冲

微软把命令的前置条件和完成通知分别称为输入信号量和输出信号量。

- **启动前。** 命令等待所依赖的输入信号量，确认输入数据就绪、输出缓冲可用。
- **执行后。** 命令通过输出信号量通知后继操作。下游可以读取新结果，上游可以复用已消费的输入缓冲。

这样一来，写入一个槽要等上一轮用完它，读取一个槽要等这一轮填好它。命令入队与命令满足执行条件是两个事件。 [Hot Chips，第 9 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=9)

## 教学推演｜一个输出槽怎样限制两次计算

假设一个 tile 内各有一个输入槽和一个输出槽，起初都为空。读引擎把分块送入输入槽，张量单元把结果放入输出槽，写引擎将结果送往下游。假定下游能够接收写入，读写引擎可以独立推进。下表用公开的信号量规则推演分块 0 和 1 的交接，按完成事件记录。

| 完成事件 | 输入槽 | 输出槽 |
| --- | --- | --- |
| 读入分块 0 | 分块 0 就绪 | 空闲 |
| 算完分块 0 | 空闲 | 结果 0 就绪 |
| 读入分块 1 | 分块 1 就绪 | 结果 0 写回中 |
| 写回结果 0 | 分块 1 就绪 | 空闲 |

第三行就是输入就绪仍要等待的情形。新结果也要写进同一个输出槽，因此前一条写命令完成后，下一次计算才符合两个启动条件。在同样的规则下，分块 1 完成计算和写回后，两个槽都可供下一轮使用。

## 公开 GEMM 案例怎样使用 CSRAM

微软在 Hot Chips 展示了四颗 Maia 芯片上的矩阵乘法（GEMM）。在图示配置中，输入有 2,048 行，收缩维和输出宽度都是 12,288。输入沿收缩维分成四块，权重沿输出维分给四颗芯片。因此一颗芯片负责 3,072 列输出，将四段收缩维各自形成的部分结果累加为一个 **2,048 × 3,072** 的输出分块。 [Hot Chips，第 11 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=11)

图中的权重从各芯片的本地 HBM 读取。激活通过设备间网络和片上 NoC 汇集，在 cluster 内参与计算。CSRAM 用于暂存激活和高精度中间结果，也可供网络控制器直接读写。公开图给出了分块及数据位置。将这些步骤落实为内核时，具体信号量配置和实机时序仍需可验证的实现记录。 [Hot Chips，第 11–12 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=12) · [微软对激活汇集的说明](https://techcommunity.microsoft.com/blog/azureinfrastructureblog/inside-maia-100-revolutionizing-ai-workloads-with-microsofts-custom-ai-accelerat/4229118)

## 软件怎样表达依赖

按微软介绍，Triton 在 cluster 层组织程序，由编译器安排内存、信号量和双缓冲。Maia API 可以分别为 cluster、tile 和向量处理器编写程序，由程序员显式安排同步。 [Hot Chips，第 10 页](https://hc2024.hotchips.org/assets/program/conference/day2/81_HC2024.Microsoft.Xu.Ramakrishnan.final.v2.pdf#page=10)

## 接下来怎么读

- 对照同一个核内的环形缓冲，查看源码怎样发布分块和归还空槽。 [Tenstorrent Wormhole n150s](../tenstorrent-wormhole-n150s/README.md)
- 看推荐推理芯片怎样由命令处理器跟踪专用单元的依赖。 [Meta MTIA 1 与 2i](../Meta_MTIA/README.md#pe-内怎样安排矩阵计算和后处理)
- 跟踪 GPU 上的双缓冲何时可读、何时可覆盖。 [NVIDIA H100 SXM](../nvidia-h100-sxm/README.md#一个缓冲何时能读何时能覆盖)
