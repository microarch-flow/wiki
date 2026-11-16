# NoC Wiki

本 wiki 从互连问题、router 资源与流控出发，延伸到拓扑、系统集成、AI 流量、评估和仿真器构建。[完整目录](./SUMMARY.md) 列出所有章节和正文。

首次学习可依次阅读：[问题与目标](./01-overview/problem-statement.md)、[Packet / Flit / Phit](./02-router-microarchitecture/packet-flit-phit-hierarchy.md)、[VC 基础](./02-router-microarchitecture/virtual-channel-fundamentals.md)、[Credit 流控](./02-router-microarchitecture/credit-based-flow-control.md) 和 [Mesh 与 Torus](./03-topology/mesh-and-torus.md)。

要实现或检查模型，可从 [核心数据结构](./08-simulator-construction/core-data-structures.md)、[Router 逐拍伪代码](./08-simulator-construction/router-pipeline-pseudocode.md) 和 [验证场景](./08-simulator-construction/verification-and-calibration.md) 入手。时序表属于文中指定的模型，不是硬件实测结果。

## 章节入口

- [01 认识 NoC](./SUMMARY.md#01-overview)
- [02 路由器与逐跳流控](./SUMMARY.md#02-router-microarchitecture)
- [03 拓扑与物理组织](./SUMMARY.md#03-topology)
- [04 路由、仲裁与服务保证](./SUMMARY.md#04-routing-and-flow-control)
- [05 端点与系统集成](./SUMMARY.md#05-system-integration)
- [06 多目标通信与调度](./SUMMARY.md#06-ai-noc-specifics)
- [07 工作负载与系统案例](./SUMMARY.md#workload-cases)
- [08 性能评估与架构探索](./SUMMARY.md#07-evaluation-methodology)
- [09 模拟器构建与验证](./SUMMARY.md#08-simulator-construction)
- [10 查阅与练习](./SUMMARY.md#09-reference)
