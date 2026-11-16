# NoC 学习与建模路线

上级：[01 认识 NoC](./README.md)

相关：[NoC 的设计维度与工作负载](./taxonomy.md)、[完整知识地图](../SUMMARY.md)

<span id="learning-roadmap"></span><span id="这页在回答什么问题"></span>可以先选一个需要回答的问题，再选择阅读路线。下面三条路线分别用于认识机制、分析系统和建立模型；完整文章列表与当前分组见[知识地图](../SUMMARY.md)。

## 路线一：认识机制

<span id="最短主线"></span><span id="第一阶段先把问题边界钉住"></span>适合第一次学习 NoC，目标是能说明一次传输经过哪些共享资源，以及它为什么会等待。

1. 从[问题与目标](./problem-statement.md)理解端点、网络和接收服务的关系。
2. 阅读[共享总线、Crossbar 与 NoC](./bus-vs-noc-vs-crossbar.md)，区分协议、连接结构和资源竞争。
3. 用[设计维度与工作负载](./taxonomy.md)整理后续会遇到的问题。
4. 阅读 [Packet、Flit 与 Phit](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)和[路由器流水线](../02-router-microarchitecture/router-pipeline-stages.md)，理解一次分包传输中的单位与阶段。
5. 阅读[Credit 与反压](../02-router-microarchitecture/credit-based-flow-control.md)和[虚通道基础](../02-router-microarchitecture/virtual-channel-fundamentals.md)，区分下游容量、队列和共享链路。
6. 阅读 [Mesh 与 Torus](../03-topology/mesh-and-torus.md)及[维序路由](../04-routing-and-flow-control/dimension-order-routing.md)，区分连接图和选路规则。

<span id="第二阶段建立最小-router-心智模型"></span><span id="第三阶段把怎么连和怎么走拆开学"></span>读完后，应能画出“发送端 → 网络接口 → 交换节点与链路 → 接收端”，并指出至少一个可能发生竞争或等待的位置。具体每跳延迟仍取决于实现。

## 路线二：分析系统

<span id="第四阶段把-noc-放回系统而不是只盯着网络本身"></span>适合已经知道基本传输机制、需要判断通信瓶颈的读者。目标是把工作负载、端点和网络资源放在同一条因果链中。

1. 阅读[网络接口 NI](../05-system-integration/ni-network-interface-design.md)，区分上层事务与网络传输的边界。
2. 阅读[流量模式与表征](../05-system-integration/traffic-patterns-and-characterization.md)，记录源、目的、数据量和发送时间。
3. 阅读[延迟、吞吐与饱和](../07-evaluation-methodology/metrics-latency-throughput-saturation.md)，明确注入、到达和消费的计量边界。
4. 用 [GEMM 通信案例](../06-ai-noc-specifics/workload-gemm-on-noc.md)检查分块、数据放置和通信方式怎样改变流量。

<span id="第五阶段进入-ai-noc-主线"></span>例如，比较两个 GEMM 映射时，先确定每个数据块由谁产生、谁使用，再计算分发和可选归约。不能仅凭算子名称推断固定的网络流量，也不能把网络到达等同于计算任务完成。

## 路线三：建立与验证模型

<span id="第六阶段把分析方法和仿真器分开建立"></span>适合需要比较设计或实现模拟器的读者。先选要预测的指标和完成边界，再选择足以表达主要瓶颈的模型粒度。

1. 阅读[如何选择模型粒度](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)，比较解析、事件和逐拍模型。
2. 阅读[从 Workload 到 Traffic Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)，确定生成的流量和依赖。
3. 需要实现网络时，再阅读[模拟器设计规格](../08-simulator-construction/simulator-design-spec.md)及[路由器流水线伪代码](../08-simulator-construction/router-pipeline-pseudocode.md)。
4. 用[验证与校准](../08-simulator-construction/verification-and-calibration.md)中的明确场景核对模型；模型结果和真实硬件测量分别报告。

<span id="建模启示"></span>如果只想估算某个目的端的容量上界，可以先使用流量需求和端口服务率，不必先模拟每个 flit。如果问题是 credit 等待或逐跳反压，就要补充相关队列、链路与反馈时序。若目标是延迟保证，还必须定义流量约束、仲裁、端点服务及证明条件。

<span id="常见误解"></span>mesh、wormhole、credit、source routing 或静态时隙都可以是具体模型的选择，但并非所有 NoC 模型、NPU 或确定性系统的必选配置。

<span id="一句话理解"></span>按问题选择模型：先明确输入和输出，再决定需要保留哪些网络状态。
