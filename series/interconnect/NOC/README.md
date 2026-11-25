# NoC Wiki

桥要从加速卡的 SRAM 读回 42。站在桥旁，看到的是一次读地址握手。把观察点移到路由器，链路上传的是什么？如果桥同时在等两笔读，返回的 42 又该交给谁？从[《一次读取怎样变成 NoC 里的请求包和返回包？》](./05-system-integration/ni-network-interface-design.md)开始，跟着这笔读走一个来回。

如果桥和 DMA 同时发起请求，它们在哪个出口会相遇？接着比较[共享总线、交叉开关与 NoC](./01-overview/bus-vs-noc-vs-crossbar.md)。要细看一个包怎样在网络里前进，可从[认识 NoC](./SUMMARY.md#01-overview)进入 [Packet、Flit 与 Phit](./02-router-microarchitecture/packet-flit-phit-hierarchy.md)、[Credit 与反压](./02-router-microarchitecture/credit-based-flow-control.md)和 [Mesh 与 Torus](./03-topology/mesh-and-torus.md)。

[完整目录](./SUMMARY.md)收录路由器、流控、拓扑、系统集成、工作负载案例、性能评估和仿真器构建等文章。按系统分析或建模目标选读，可查看[学习与建模路线](./01-overview/learning-roadmap.md)。

要实现或检查模型，可从[核心数据结构](./08-simulator-construction/core-data-structures.md)、[Router 逐拍伪代码](./08-simulator-construction/router-pipeline-pseudocode.md)、[最小逐拍实作](./08-simulator-construction/minimal-cycle-simulator.md)和[验证场景](./08-simulator-construction/verification-and-calibration.md)入手。再用[练习与参考解答](./09-reference/exercises-and-worked-solutions.md)检查理解。时序表属于文中指定的模型，不是硬件实测结果。

## 章节入口

- [01 认识 NoC](./SUMMARY.md#01-overview)
- [02 路由器与逐跳流控](./SUMMARY.md#02-router-microarchitecture)
- [03 拓扑与物理组织](./SUMMARY.md#03-topology)
- [04 路由、仲裁与服务保证](./SUMMARY.md#04-routing-and-flow-control)
- [05 端点与系统集成](./SUMMARY.md#05-system-integration)
- [06 多端通信与调度](./SUMMARY.md#06-ai-noc-specifics)
- [07 工作负载与系统案例](./SUMMARY.md#workload-cases)
- [08 性能评估与架构探索](./SUMMARY.md#07-evaluation-methodology)
- [09 模拟器构建与验证](./SUMMARY.md#08-simulator-construction)
- [10 查阅与练习](./SUMMARY.md#09-reference)
