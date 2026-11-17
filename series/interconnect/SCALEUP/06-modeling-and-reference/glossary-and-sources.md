# 加速器互连术语、版本与一手资料

上级：[建模、诊断与查阅](README.md)

本页用于查阅对象、版本与证据范围。资料核查日期为 2026-11-17。指向 `latest` 或 `master` 的页面会继续变化，复现实验时应另行保存软件版本及提交号。

## 容易混淆的术语

| 术语 | 本专题使用的含义 |
| --- | --- |
| rank | 一个通信组中的逻辑参与者编号，不是物理端口号 |
| PE | NVSHMEM 的参与处理实体；其对应关系由启动与运行方式确定 |
| peer access | 指定设备方向对对端资源的受支持访问能力 |
| communication domain | 在明确接口与配置下协同通信的端点范围 |
| coherence | 对共享数据副本的约束；不等于所有访问具有同一顺序 |
| ordering | 对操作或观察次序的规定；不自动等于完成 |
| completion | 针对规定操作、观察者和资源复用边界的完成事件 |
| injection bandwidth | 端点向所分析路径注入数据的能力 |
| busbw | 通信测试按算子换算的归一化带宽，不是物理总线计数器 |
| in-network compute | 在网络组件中执行受支持计算，需说明算子和参与范围 |

## 协议与平台资料

| 来源 | 本专题使用范围 | 不能据此推断 |
| --- | --- | --- |
| [UALink 规范目录](https://ualinkconsortium.org/specification/) | 200G 1.0、Common 2.0、DL/PL、Chiplet 与管理组件的发布关系 | 任意产品已实现全部功能或已完成互操作认证 |
| [UALink 1.0 分层概览](https://ualinkconsortium.org/blog/ualink-200g-1-0-specification-overview-802/) | 操作、分层、请求／响应与信用职责 | 未公开器件参数或完整错误状态机 |
| [GB200 系统说明](https://docs.nvidia.com/multi-node-nvlink-systems/multi-node-tuning-guide/system.html) | 具体机架与托盘配置 | 所有代际的 NVLink 都采用同一拓扑 |
| [AMD MI350 架构](https://rocm.docs.amd.com/en/latest/reference/gpu-arch/mi350.html) | MI350X／MI355X 八 GPU 平台 | 所有 AMD GPU 都有同一组对端链路 |

## 软件接口与测量资料

- [CUDA 对端访问](https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__PEER__ACCESS.html)与[HIP 对端访问](https://rocm.docs.amd.com/projects/HIP/en/latest/doxygen/html/group___peer_to_peer.html)：能力、方向及启用规则；实际分配方式另查对应 API。
- [NVSHMEM API 概览](https://docs.nvidia.com/nvshmem/api/latest/api/overview.html)：GPU／CPU 作用范围、对称对象与执行接口。
- [NCCL 概述](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/overview.html)与[RCCL 概述](https://rocm.docs.amd.com/projects/rccl/en/latest/what-is-rccl.html)：通信原语及支持路径，不是具体系统的性能保证。
- [NCCL Tests](https://github.com/NVIDIA/nccl-tests)及[指标定义](https://github.com/NVIDIA/nccl-tests/blob/master/doc/PERFORMANCE.md)：测试配置、正确性检查和带宽换算。
- [Megatron-LM](https://arxiv.org/abs/1909.08053)、[大规模训练并行研究](https://arxiv.org/abs/2104.04473)、[DeepSeek-V3](https://arxiv.org/abs/2412.19437)：具体并行算法与系统案例，不能推广为所有模型的固定通信模式。

## 怎样记录新结论

新增技术结论时，记录对象、版本、原始来源及适用条件。理论估算另列输入、单位、简化假设和未覆盖因素；实测另列硬件、软件、命令、原始结果及统计方法。

本专题的窗口、通信矩阵、TP、MoE 和重叠数字均为教学模型。未开展 GPU 实测、设备互操作认证或硬件错误注入。对尚无公开依据的厂商内部协议，不补写猜测字段；对 UALink 新组件的详细能力，使用目标规范正文和器件文档进一步核实。
