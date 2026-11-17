# AMD xGMI：八 GPU 直连系统怎样分配链路

上级：[协议与系统案例](README.md)

AMD Instinct 的 GPU 间连接不能只用一个“总带宽”描述。链路连接到谁，决定某次通信能使用多少资源。本文使用 MI350X／MI355X 八 GPU 平台，不推广到所有 AMD 产品。

## 先画出实际邻接关系

[AMD MI350 架构资料](https://rocm.docs.amd.com/en/latest/reference/gpu-arch/mi350.html)描述了八 GPU 全连接节点：每颗 GPU 通过七条 Infinity Fabric 连接与其他 GPU 通信，并通过 PCIe Gen5 x16 连接主机侧。这里讨论的是 GPU 间 xGMI 路径，封装内芯粒连接是另一层结构。

如果每对 GPU 具有独立直连，八 GPU 共形成 28 对连接。单个 GPU 到某一个对端的专用路径，只占其七个邻居方向之一。不能把七个方向的聚合带宽都视为任意一对 GPU 的直接带宽。

## 为什么参与者子集影响通信

假设只使用其中两颗 GPU，采用两者直接通信的实现，则其他六个邻居方向不会自动加入该次传输。使用全部八颗 GPU 的集体通信，有机会同时利用更多连接，但仍需要算法及分块实际产生对应流量。

AMD 的[工作负载优化资料](https://rocm.docs.amd.com/projects/ai-ecosystem/en/latest/optimization/workload-optimization.html)也强调参与 GPU 子集与可用链路的关系。这里不把“使用更多 GPU”写成任务一定更快：更多参与者也可能增加同步、分块和计算切分成本。

如果软件借助其他 GPU 转发，两端的可用路径会改变，同时增加中转 GPU、链路及内存的消耗。比较时必须记录是否发生转发，不能把这种结果当作单条直连能力。

## CPU 路径与 GPU 路径分开记录

| 操作 | 首先确认的资源 |
| --- | --- |
| GPU 访问 GPU 缓冲 | 对端能力、xGMI 或实际回退路径、目标内存 |
| CPU 与 GPU 传输 | PCIe 拓扑、NUMA 放置、主机内存与搬运引擎 |
| 跨节点通信 | GPU 到 NIC 的路径、NIC 和外部网络 |

RCCL 为 AMD GPU 提供多 GPU、多节点通信，并支持 xGMI、PCIe 及网络路径。[RCCL 概述](https://rocm.docs.amd.com/projects/rccl/en/latest/what-is-rccl.html) 实际运行仍需记录 ROCm／RCCL 版本、设备分区、GPU 子集和拓扑。

本页没有把官方链路速率直接换算为应用有效载荷吞吐；速率、lane 数、方向及编码开销未统一时，这种换算容易产生错误。测量方法见[通信测试](../05-workloads-and-performance/benchmarking.md)。
