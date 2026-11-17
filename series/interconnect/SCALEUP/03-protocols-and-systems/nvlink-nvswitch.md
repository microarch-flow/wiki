# NVLink 与 NVSwitch：从 GPU 链路到机架通信域

上级：[协议与系统案例](README.md)

NVLink 提供 GPU 间通信连接，NVSwitch 把连接组成交换结构。理解性能时，需要同时看每颗 GPU 的接口、交换拓扑和实际软件操作。本文固定使用 GB200 NVL72 的第五代 NVLink 案例，不把其数字用于其他代际。

## 72 个 GPU 怎样接入交换结构

NVIDIA 的 DGX GB200 参考架构描述了 18 个计算托盘和 9 个 NVLink 交换托盘。每个计算托盘有 4 个 GPU；每个交换托盘有 2 个交换芯片。每颗 GPU 的 18 条 NVLink 分别接向 18 个交换芯片。[DGX GB200 参考架构，第 3.1 与第 4 章](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-gb200/latest/_downloads/238ab33ee345a7241fc2f15eedc2ff6c/RA11338001-DSPGB200-ReferenceArch.pdf)

这里的任意 GPU 间可通信，是通过交换结构实现的，不是 72 个 GPU 之间各拉一条专用直连。GPU、交换芯片和托盘是不同的计数对象。

## 带宽的观察边界

第五代 NVLink 在该平台给出的每 GPU 1.8 TB/s 是双向聚合吞吐口径。[NVIDIA 技术说明](https://developer.nvidia.com/blog/nvidia-gb200-nvl72-delivers-trillion-parameter-llm-training-and-real-time-inference/) 在两个方向对称的预算下，单方向对应 0.9 TB/s；这仍是接口预算，不是任意消息大小的实测值。

| 量 | 应怎样解释 |
| --- | --- |
| 每 GPU 的 1.8 TB/s | 该 GPU 接口的双向聚合口径 |
| 整域约 130 TB/s | 72 个 GPU 接口按该口径聚合后的量级 |
| 某对 GPU 的测试结果 | 受选用路径、并发、操作和目标内存影响 |
| AllReduce 的 busbw | 软件测试采用的归一化指标，需按算子解释 |

不能把整域聚合值除以任意消息大小，就当作任务时间。也不能把双向接口总量与单方向网络端口直接相除后宣称性能倍数。

## 通信域不等于一个普通共享内存对象

在同一 NVLink 域内，软件仍需建立设备、进程与内存访问关系。消费者仍需遵守 CUDA 或通信库的同步规则。NVLink-C2C 的 CPU—GPU 连接和这里的 GPU—交换结构，也不能仅因名称相似而共享同一套一致性结论。

跨越 NVLink 域时，任务可能继续通过 NIC 和系统网络通信。应用需要记录 rank 到域、GPU 和网络出口的映射；同一个 NCCL 调用可以覆盖多种路径。下一步可读[通信库组织](../04-software-and-collectives/nccl-rccl-contracts.md)和[指标口径](../05-workloads-and-performance/metrics-and-units.md)。
