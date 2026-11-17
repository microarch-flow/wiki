# GPUDirect RDMA：NIC 怎样访问 GPU 内存并交付结果？

上级：[系统集成与新协议](README.md)

GPUDirect RDMA 允许受支持的第三方设备与 GPU 内存建立直接数据路径。对网络而言，关键收益是减少通过主机内存中转的需要；它不自动消除连接管理、权限交换或消费者同步。

## 建立路径需要三个条件

首先，GPU 内存必须通过平台支持的方式暴露给 NIC，并在使用期间保持有效。其次，NIC 与 GPU 之间的互连、地址映射和路由必须支持该访问。最后，通信库及驱动需要实际选择这条路径。

平台可采用 nvidia-peermem 或符合要求的 DMA-BUF 等机制，适用条件随驱动、内核、GPU 和软件版本变化。不要把“安装某个模块”作为所有平台的固定步骤，也不要未经平台确认就修改 ACS 或 IOMMU。[NCCL GPU 排查文档](https://docs.nvidia.com/deeplearning/nccl/archives/nccl_2312/user-guide/docs/troubleshooting/gpu_troubleshooting.html)

## 一次网络接收的职责

远端发送数据，本地 NIC 根据授权把数据写入 GPU 内存。通信软件观察相应网络完成，并按支持的 GPU 同步机制建立到后续计算的依赖。消费者随后处理数据，最后归还或复用缓冲区。

NVIDIA 的 [GPUDirect RDMA 文档](https://docs.nvidia.com/cuda/gpudirect-rdma/index.html#synchronization-and-memory-ordering)指出，正在运行的 GPU 工作可能观察到尚未正确排序的第三方写入。因此，“NIC 写完”不能无条件推出“并发 kernel 已可直接读取”。具体同步或 flush 要使用该平台和通信库提供的契约。

## 三种直连不要混用

| 概念 | 主要路径 | 仍需核对 |
| --- | --- | --- |
| GPU P2P | GPU 与 GPU 之间 | 对端访问能力、映射和 GPU 执行依赖 |
| GPUDirect RDMA | NIC 等设备与 GPU 内存之间 | 注册、设备间路径和远端访问完成 |
| GPU 发起通信 | GPU 工作提交或推进通信 | 发起接口、进度资源和通信软件语义 |

数据绕过主机内存不表示请求一定由 GPU 发起。GPU 发起通信的程序模型见[加速器专题](../../SCALEUP/04-software-and-collectives/gpu-initiated-communication.md)，PCIe P2P 约束见[路径条件](../../PCIE/07-advanced-topics/p2p-switch-topology-constraints.md)。

## 怎样确认实际生效

对照主机内存和 GPU 内存测试，记录 GPU→NIC 放置、注册方式、库日志及端口流量。性能相近不证明路径相同，性能下降也不一定是网络拥塞。若 NIC 端口空闲而 PCIe 或 GPU 内存服务受限，应先分析设备侧路径。
