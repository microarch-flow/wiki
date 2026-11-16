# NoC 参考资料与工具：按什么问题继续查？

上级：[10 查阅与练习](../SUMMARY.md#09-reference)

相关：[NoC 术语表](./glossary.md)、[练习与参考解答](./exercises-and-worked-solutions.md)、[如何选择模型粒度](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)

这些资料用于追溯机制、语义和模型接口。先选要回答的问题，再对照资料的对象、假设和版本；引用资料不代表本专题实现了其中所有功能。

## 流控与路由

- [Dally，Virtual-Channel Flow Control](https://groups.csail.mit.edu/cag/PSRG/papers/dally-ieee92.pdf)：理解逻辑缓冲与物理带宽的分配，以及特定假设下 VC 的作用。配套：[VC 基础](../02-router-microarchitecture/virtual-channel-fundamentals.md)。
- [Dally 与 Seitz，Deadlock-Free Message Routing](https://authors.library.caltech.edu/records/fd0yr-br438)：了解通道依赖分析。使用证明时，要检查实际路由与资源是否满足所选模型。配套：[死锁、活锁与饥饿](../04-routing-and-flow-control/deadlock-livelock-starvation.md)。
- [Glass 与 Ni，The Turn Model for Adaptive Routing](https://researchportal.hkust.edu.hk/en/publications/the-turn-model-for-adaptive-routing-2/)和 [Duato，自适应路由的无死锁理论](https://web.csl.cornell.edu/courses/ece5750/duato.tpds93.pdf)：阅读限制转向及逃逸资源的不同思路；不能只凭增加一个 VC 宣称无死锁。配套：[Turn Model 与逃逸资源](../04-routing-and-flow-control/deadlock-avoidance-turn-model.md)。

## 事务与集体通信

- [Arm，AMBA AXI 入门，Version 3.0](https://documentation-service.arm.com/static/66fd59a21669c0388dca99b7)：查 AXI 通道、事务与 QoS 信号。它介绍接口协议，不规定所有 NoC 的内部实现。配套：[事务拆分、顺序与完成](../05-system-integration/transaction-ordering-and-completion.md)。
- [MPI 4.1 集体通信](https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report/node114.htm)及[非阻塞集体操作的完成](https://www.mpi-forum.org/docs/mpi-4.1/mpi41-report/node145.htm)：查参与组、结果和局部完成语义。这里借用通信形状，不假定 NoC 接口实现 MPI。配套：[集体通信基础](../06-ai-noc-specifics/collective-communication-basics.md)。

## 系统集成与公开实现

- [AMD PG327：独立时钟 FIFO](https://docs.amd.com/r/en-US/pg327-emb-fifo-gen/Independent-Clocks-Block-RAM-and-Distributed-RAM)：查读写域及状态标志的可见条件。配套：[跨时钟域、复位与流控](../05-system-integration/clock-domains-and-reset.md)。
- [AMD PG313：Versal NoC 读事务](https://docs.amd.com/r/en-US/pg313-network-on-chip/Read-Transactions)及[性能监控](https://docs.amd.com/r/en-US/pg313-network-on-chip/NoC-Performance-Monitoring)：查一个产品族的端点、网络路径与观测位置。配套：[公开 NoC 案例](../07-workload-cases/published-noc-case.md)；具体配置和文档版本需另行记录。

## Trace 与模拟工具

- [Netrace：Dependency-Driven Trace-Based Network-on-Chip Simulation](https://www.research.ed.ac.uk/en/publications/netrace-dependency-driven-trace-based-network-on-chip-simulation/)：了解保留消息依赖的一种 Trace 方法。本专题 `noc-workload-v1` 是独立教学契约，不等同 Netrace 格式。配套：[从工作负载到流量 Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)。
- **BookSim 2.0**：[固定提交的手册](https://github.com/booksim/booksim2/blob/54e2e6d2608297e4374a9a5f9b3baa0ca2c5d687/doc/manual.tex)介绍拓扑、流控与实验配置；[同一提交的配置源码](https://github.com/booksim/booksim2/blob/54e2e6d2608297e4374a9a5f9b3baa0ca2c5d687/src/booksim_config.cpp)给出参数。手册列有根据文件连接节点和 router 的 AnyNet，也描述物理子网络；具体功能应按所用版本和配置核实。
- **gem5 Garnet 2.0**：[官方文档](https://www.gem5.org/documentation/general_docs/ruby/garnet-2/)介绍 Ruby 网络中的路由器、VC 与配置。其 `vcs_per_vnet` 是每个 vnet 的 VC 数；文档中的多播在 NI 展开为单播，并非网络内硬件复制。配套：[参数与配置参考](../08-simulator-construction/parameter-reference.md)。

固定提交的 BookSim 手册将物理子网络参数写作 `physical_subnetworks`；同一提交的配置源码及 [traffic manager](https://github.com/booksim/booksim2/blob/54e2e6d2608297e4374a9a5f9b3baa0ca2c5d687/src/trafficmanager.cpp)使用 `subnets`。实际运行前应对照源码和配置验证参数，不直接照搬不同版本的示例。

## 使用资料时记录什么

1. 记录资料版本、使用的模型或协议范围，以及目标页面和正文对应的概念。
2. 比较工具结果前，对齐拓扑、端点、路由、缓冲、反馈时序、流量和统计边界。
3. 把原论文中的假设和构造结果与真实系统测量分开；一项仿真回归通过，不等于硬件已经校准。

整理实验输入、结果和未验证假设，可使用[实验与案例记录](../07-evaluation-methodology/case-card-template.md)。需要练习时间与容量口径时，回到[练习与参考解答](./exercises-and-worked-solutions.md)。
