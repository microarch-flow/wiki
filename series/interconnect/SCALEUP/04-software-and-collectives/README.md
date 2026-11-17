# 04 软件与集体通信

<!-- nav-title: 04 软件与集体通信 -->

硬件连接通过运行时和通信库向应用提供能力。程序必须先建立有效资源，再正确表达数据依赖和完成条件。

本章区分对端访问、GPU 发起通信与集体通信库，最后把逻辑通信步骤映射到实际链路。算子基本语义和环形算法推导复用 NoC 文章。

## 阅读顺序

1. [CUDA／HIP 对端访问](peer-access-setup.md)
2. [GPU 发起通信与通知](gpu-initiated-communication.md)
3. [NCCL／RCCL 通信契约](nccl-rccl-contracts.md)
4. [映射、分块与交换归约](collective-mapping-and-offload.md)

返回[专题导读](../README.md)，选择机制、系统或任务分析路线。
