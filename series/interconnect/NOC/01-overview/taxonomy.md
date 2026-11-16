# NoC 的设计维度与工作负载

上级：[01 认识 NoC](./README.md)

相关：[NoC 在解决什么问题？](./problem-statement.md)、[路由算法分类](../04-routing-and-flow-control/routing-algorithm-classes.md)

<span id="taxonomy"></span><span id="这页在回答什么问题"></span>描述一个 NoC，不能只说“它是 mesh”。还要知道端点产生什么流量，数据怎样选路，资源怎样分配，以及接收端如何消费。本文用一组问题区分这些对象；详细机制留给后续章节。

## 先区分需求、设计和结果

<span id="为什么-noc-特别容易学乱"></span><span id="第一维按系统目标分"></span><span id="第七维按-traffic-pattern-与-workload-分"></span>工作负载和映射给出通信需求，例如谁向谁发送、数据量和发送时机。拓扑、路由、缓冲和仲裁属于设计选择。延迟、吞吐、面积和功耗则是在给定条件下需要评价的结果。

这些问题可以分别描述，但不完全独立。例如，路由只能选择拓扑提供的路径；流控和缓冲组织也必须配合。把它们分开，是为了说明**哪个条件或选择造成了什么结果**，不是承诺所有组合都能实现。

GEMM 是计算任务，不是一种固定流量。输出块在本地累加时，可以没有跨 tile 的部分和归约；把同一输出的不同 K 分片放在不同 tile 时，就需要传递并归约部分和。[GEMM 通信案例](../06-ai-noc-specifics/workload-gemm-on-noc.md)给出了一个具体分块。

## 描述设计时要问什么

| 问题与对象 | 要记录什么，以及从哪里深入 |
| --- | --- |
| 接口与消息语义 | 端点发出事务还是 stream？是否要求响应、顺序或错误报告？网络接口如何转换？见[网络接口 NI](../05-system-integration/ni-network-interface-design.md)。 |
| <span id="第二维按-topology-分"></span>连接与物理实现 | 谁与谁相连？链路宽度、方向、长度和流水怎样映射到布局？逻辑连接图与实际布线需要分别描述。见[拓扑与物理实现](../03-topology/topology-physical-realization.md)。 |
| <span id="第三维按-routing-分"></span>路径选择 | 源端指定路径，还是每跳选择？选择是否依赖运行时状态？路径是否限定为最短路径？见[路由算法分类](../04-routing-and-flow-control/routing-algorithm-classes.md)。 |
| <span id="第四维按-switching-分"></span>交换与转发 | 资源按连接预留，还是按包竞争？分包网络可以使用存储转发、virtual cut-through 或 wormhole 等方式。见[转发与交换方式](../02-router-microarchitecture/wormhole-vs-vct-vs-store-forward.md)。 |
| <span id="第五维按-flow-control-分"></span>流控 | 发送方如何判断接收资源可用？反馈针对哪段路径、什么容量和什么单位？见[Credit 与反压](../02-router-microarchitecture/credit-based-flow-control.md)。 |
| <span id="第六维按资源隔离与服务策略分"></span>资源与服务 | 队列和链路如何共享？是否使用虚通道、虚拟网络、优先级或预留时隙？见[仲裁策略](../04-routing-and-flow-control/arbitration-policies.md)和 [QoS](../04-routing-and-flow-control/qos-and-priority-classes.md)。 |
| 正确性与评价 | 在什么条件下能前进？在哪个边界测量延迟、吞吐和完成？见[死锁、活锁与饥饿](../04-routing-and-flow-control/deadlock-livelock-starvation.md)及[性能指标](../07-evaluation-methodology/metrics-latency-throughput-saturation.md)。 |

## 在一个例子中区分选择

<span id="一个更实用的记忆顺序"></span>假设四个节点构成 2×2 mesh，坐标向东为 X 正方向、向北为 Y 正方向。一个消息从 (0,0) 发往 (1,1)。如果采用先 X 后 Y 的维序路由，路径是先向东、再向北；如果允许另一条最短路径，也可以先向北、再向东。

这里的 **mesh** 描述连接；**XY** 描述允许的选路规则。假设该实现再采用 wormhole 转发和逐跳 credit，才进一步确定缓冲与流控模型。相同拓扑可以使用不同路由；相同路由也可能搭配不同的缓冲和服务策略。路径选定后，等待时间仍取决于其他流量和目的端服务。

<span id="常见误解"></span>source routing 描述由源端提供路径信息；deterministic 或 adaptive 描述路径如何选择。它们回答不同问题，可以组合。固定路径也不自动保证延迟上界。

## 逐跳流控、隔离与服务保证

Arm AXI 的 `VALID/READY` 描述接口上的发送方与接收方何时完成一次传输。某些 NoC 链路用 credit 表示接收侧可用容量；也有 NoC 实现提供其他握手或信用方案。它们不是“总线”和“NoC”的排他分界。[Arm AXI 规范，Issue J](https://documentation-service.arm.com/static/63ff0ebd56ea36189d4e7ee7)；[FlooNoC 实现示例](https://github.com/pulp-platform/FlooNoC/blob/292f676/hw/floo_pkg.sv)

本专题后续的 credit 例子以**相邻节点之间的缓冲槽位**为前提：该跳释放槽位后返回信用，阻塞可能逐跳向上游传播。credit 不等于整个事务完成。也存在端到端信用机制，需要按其自己的容量与反馈范围建模。[端到端 credit 论文](https://cecs.uci.edu/~papers/esweek06/codes/p130.pdf)

虚通道（VC）可以分开排队状态，减轻某些队头阻塞；多个 VC 仍可能争用同一条物理链路或目的端口。仅有 VC、优先级或固定路由，都不能单独证明无死锁或延迟有上界。服务保证还依赖流量约束、资源分配、端点服务及其证明条件。Æthereal 的保证服务就是一种有明确条件的设计实例。[Æthereal 论文](https://kgoossens.estue.nl/docs/research/2005-philipsbook-chap1.pdf)

## 与事务和存储系统的边界

<span id="和-bus-ram-体系的衔接"></span>NoC 可以运输带事务语义的请求和响应，也可以运输 stream 或控制消息。地址映射决定请求落到哪个目标；存储 bank、控制器和接收端的服务能力会影响网络中的等待。描述通信时，应同时记录网络路径和端点边界，而不是先按“控制面”或“数据面”断言它使用哪种结构。

## 如何用于建模

<span id="建模启示"></span>比较方案时，先固定端点、输入流量和计量边界，再明确哪些设计参数改变。若同时改拓扑、路由和目的端服务，就不能仅把结果归因于拓扑。模型是否需要 flit、VC 或信用状态，取决于要回答的问题；这些字段不是所有分析模型的必选项。

<span id="一句话理解"></span>先记录通信需求，再分别描述连接、选路、转发和资源服务，最后在共同条件下评价结果。
