# 04 软件与集体通信

<!-- nav-title: 04 软件与集体通信 -->

硬件连接通过运行时和通信库向应用提供能力。程序必须先建立有效资源，再正确表达数据依赖和完成条件。

如果要让 GPU A 直接读取 GPU B 的缓冲区，可先查看[CUDA 与 HIP 怎样查询能力并启用 A 到 B 的访问](../01-access-semantics/address-mapping-and-permissions.md#peer-access)。本章接着讨论 GPU 发起通信与集体通信库，最后把逻辑通信步骤映射到实际链路。算子基本语义和环形算法推导复用 NoC 文章。

## 阅读顺序

1. [GPU 发起通信与通知](gpu-initiated-communication.md)
2. [NCCL／RCCL 通信契约](nccl-rccl-contracts.md)
3. [映射、分块与交换归约](collective-mapping-and-offload.md)

返回[专题导读](../README.md)，选择机制、系统或任务分析路线。
