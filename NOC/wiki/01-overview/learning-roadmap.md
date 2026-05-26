# Learning Roadmap

上级：[01 Overview](./README.md)
相关：[Taxonomy](./taxonomy.md), [../02-router-microarchitecture/README.md](../02-router-microarchitecture/README.md)

## 这页在回答什么问题

面对这套新目录，应该按什么顺序建立语言体系，才能尽快获得“能做 NoC 建模和设计判断”的能力，而不是在概念之间来回打转。

这条路线专门面向你的目标：deterministic NPU、编译器友好、以数据搬运为主线的架构探索，而不是面向通用 CPU NoC 教程。

## 第一阶段：先把问题边界钉住

先读这一章，不是因为它最轻松，而是因为后面所有 trade-off 都依赖这里的边界判断。

建议顺序：

1. [Problem Statement](./problem-statement.md)
2. [Bus Vs NoC Vs Crossbar](./bus-vs-noc-vs-crossbar.md)
3. [Taxonomy](./taxonomy.md)

这一阶段结束后，你至少应该稳定区分三件事：

- NoC 解决的是规模化并发通信，不是“带宽更大的 BUS”
- topology、routing、flow control 是正交维度，不该一起记
- AI NoC 的主线是数据搬运与可调度性，不是 coherence 协议

如果这三点不稳，后面学得越细，越容易把结论套错对象。

## 第二阶段：建立最小 router 心智模型

这一步的目标不是会写 RTL，而是知道一个 packet 为什么会被切成 flit，为什么会卡，为什么这种卡顿会被系统放大。

建议顺序：

1. [Packet Flit Phit Hierarchy](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)
2. [Wormhole Vs VCT Vs Store Forward](../02-router-microarchitecture/wormhole-vs-vct-vs-store-forward.md)
3. [Credit Based Flow Control](../02-router-microarchitecture/credit-based-flow-control.md)
4. [Router Pipeline Stages](../02-router-microarchitecture/router-pipeline-stages.md)
5. [Virtual Channel Fundamentals](../02-router-microarchitecture/virtual-channel-fundamentals.md)
6. [Allocator Design VC Switch](../02-router-microarchitecture/allocator-design-vc-switch.md)

这一阶段建立的是 NoC 的“局部物理学”：一个 flit 怎样前进、怎样等待、怎样占用路径资源。你后面看到任何系统瓶颈，最终都能沿着这条链回到 router 内部状态。

## 第三阶段：把“怎么连”和“怎么走”拆开学

旧版 wiki 的一个大问题，就是把 topology 和 routing 缠在一起。新结构里必须强行拆开，因为它们的设计问题不同。

先学 topology：

1. [Topology Design Metrics](../03-topology/topology-design-metrics.md)
2. [Mesh And Torus](../03-topology/mesh-and-torus.md)
3. [Crossbar And Concentrated Mesh](../03-topology/crossbar-and-concentrated-mesh.md)
4. [Topology Physical Realization](../03-topology/topology-physical-realization.md)
5. [Topology Selection Framework](../03-topology/topology-selection-framework.md)

再学 routing 和 flow control：

1. [Routing Algorithm Classes](../04-routing-and-flow-control/routing-algorithm-classes.md)
2. [Dimension Order Routing](../04-routing-and-flow-control/dimension-order-routing.md)
3. [Deadlock Avoidance Turn Model](../04-routing-and-flow-control/deadlock-avoidance-turn-model.md)
4. [Source Routing For Deterministic Systems](../04-routing-and-flow-control/source-routing-for-deterministic-systems.md)
5. [QoS And Priority Classes](../04-routing-and-flow-control/qos-and-priority-classes.md)
6. [Deadlock Livelock Starvation](../04-routing-and-flow-control/deadlock-livelock-starvation.md)

为什么这样排？因为如果你先看 adaptive routing 或 QoS，却对 topology 的 path diversity、长线代价和集中热点没有感觉，就会高估策略的作用，低估结构的约束。

## 第四阶段：把 NoC 放回系统，而不是只盯着网络本身

这一阶段是 NoC 能否进入架构分析的分水岭。很多教程学到这里以前都还算顺；一进系统就开始模糊，因为 DMA、memory controller、bank parallelism 和 BUS 控制面会把局部结论打乱。

建议顺序：

1. [NI Network Interface Design](../05-system-integration/ni-network-interface-design.md)
2. [Address Map And Routing Table](../05-system-integration/address-map-and-routing-table.md)
3. [DMA Engine NoC Interaction](../05-system-integration/dma-engine-noc-interaction.md)
4. [Multiple Physical Networks](../05-system-integration/multiple-physical-networks.md)
5. [NoC Meets Memory System](../05-system-integration/noc-meets-memory-system.md)
6. [NoC Vs Bus Revisited](../05-system-integration/noc-vs-bus-revisited.md)

这里你需要主动和 BUS/RAM 体系联动，而不是把 NoC 当孤岛：

- 对照 [AI 芯片里的 BUS vs NoC](../../../BUS/wiki/06-scenarios-case-studies/bus-vs-noc-in-ai-chip.md)，明确控制面和数据面的边界
- 对照 [RAM 分类框架](../../../RAM/wiki/01-overview/taxonomy.md) 和 [把 register、cache、scratchpad、DRAM、HBM 看作一个系统](../../../RAM/wiki/07-system-architecture/memory-hierarchy-as-system.md)，理解为什么 response path 经常比 request path 更危险

## 第五阶段：进入 AI NoC 主线

你的最终目标不是“泛泛会讲 NoC”，而是让 NoC 能进入 deterministic NPU 的架构探索框架。所以到了这里，学习优先级要从“网络知识全覆盖”切到“哪些内容会直接改变建模结果”。

建议顺序：

1. [Why AI NoC Is Different](../06-ai-noc-specifics/why-ai-noc-is-different.md)
2. [Deterministic NoC And Static Scheduling](../06-ai-noc-specifics/deterministic-noc-and-static-scheduling.md)
3. [Tile Architecture And NoC](../06-ai-noc-specifics/tile-architecture-and-noc.md)
4. [Compiler NoC Co Design](../06-ai-noc-specifics/compiler-noc-co-design.md)
5. [Memory Centric NoC](../06-ai-noc-specifics/memory-centric-noc.md)
6. [Workload GEMM On NoC](../06-ai-noc-specifics/workload-gemm-on-noc.md)
7. [Workload Attention Prefill](../06-ai-noc-specifics/workload-attention-prefill.md)
8. [Workload Attention Decode KV Cache](../06-ai-noc-specifics/workload-attention-decode-kv-cache.md)
9. [Workload MoE Routing](../06-ai-noc-specifics/workload-moe-routing.md)

这一阶段的关键词不是“知识点”，而是“工作负载怎样长成流量，再怎样逼出互连选择”。

## 第六阶段：把分析方法和仿真器分开建立

这里是旧版 wiki 另一个明显错误：把评估方法和 simulator 实现揉在一起。正确顺序是先方法，后工程。

先学评估方法：

1. [Metrics Latency Throughput Saturation](../07-evaluation-methodology/metrics-latency-throughput-saturation.md)
2. [Modeling Layers Analytical Event Cycle](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)
3. [From Workload To Traffic Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)
4. [Stall Taxonomy And Attribution](../07-evaluation-methodology/stall-taxonomy-and-attribution.md)
5. [Architecture Exploration Loop](../07-evaluation-methodology/architecture-exploration-loop.md)

再学仿真器实现：

1. [Simulator Design Spec](../08-simulator-construction/simulator-design-spec.md)
2. [Core Data Structures](../08-simulator-construction/core-data-structures.md)
3. [Event Driven Vs Cycle Accurate](../08-simulator-construction/event-driven-vs-cycle-accurate.md)
4. [Router Pipeline Pseudocode](../08-simulator-construction/router-pipeline-pseudocode.md)
5. [Traffic Injection And Tracing](../08-simulator-construction/traffic-injection-and-tracing.md)
6. [Verification And Calibration](../08-simulator-construction/verification-and-calibration.md)
7. [Implementation Roadmap](../08-simulator-construction/implementation-roadmap.md)

你如果反过来先写 simulator，通常会遇到一个经典问题：代码越写越多，但不知道哪些统计项真正能支撑设计判断。

## 最短主线

如果你现在只想尽快进入“能做第一版 deterministic NPU NoC 建模”的状态，可以先读这 12 页：

1. [Problem Statement](./problem-statement.md)
2. [Bus Vs NoC Vs Crossbar](./bus-vs-noc-vs-crossbar.md)
3. [Packet Flit Phit Hierarchy](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)
4. [Credit Based Flow Control](../02-router-microarchitecture/credit-based-flow-control.md)
5. [Router Pipeline Stages](../02-router-microarchitecture/router-pipeline-stages.md)
6. [Mesh And Torus](../03-topology/mesh-and-torus.md)
7. [Dimension Order Routing](../04-routing-and-flow-control/dimension-order-routing.md)
8. [Source Routing For Deterministic Systems](../04-routing-and-flow-control/source-routing-for-deterministic-systems.md)
9. [NI Network Interface Design](../05-system-integration/ni-network-interface-design.md)
10. [Deterministic NoC And Static Scheduling](../06-ai-noc-specifics/deterministic-noc-and-static-scheduling.md)
11. [From Workload To Traffic Trace](../07-evaluation-methodology/from-workload-to-traffic-trace.md)
12. [Simulator Design Spec](../08-simulator-construction/simulator-design-spec.md)

读完这 12 页，你已经可以开始搭第一版模型，并且知道哪些问题暂时可以抽象掉。

## 常见误解

常见误解：先把所有 topology 和 routing 算法学完，再开始建模。  
实际上：对 deterministic NPU 来说，先建立 `wormhole + credit + simple mesh + source/dimension-order routing` 的可用模型，收益比“百科全书式覆盖”高得多。

常见误解：AI NoC 专题应该最先读，因为目标就是 AI。  
实际上：如果 router、topology、routing 的语言体系还没立住，AI 专题只会变成案例印象，难以转成可复用模型。

## 一句话理解

正确的学习顺序不是从名词多到少，而是从问题边界、局部机制、网络结构、系统集成到 AI workload 和建模方法逐层收紧。

## 建模启示

这页的作用是告诉你“当前该建哪一层模型”，所以最关键的状态不是网络内部状态，而是学习阶段对应的模型边界：

```text
ModelScope {
  level  // SYSTEM, ROUTER, TOPOLOGY, AI_WORKLOAD, EVALUATION
  required_states[]
  ignorable_details[]
}
```

例如在第二阶段，`required_states` 应至少包含 `packet_size`, `flit_size`, `buffer_depth`, `credit_count`；而 `ignorable_details` 可以先包括 `adaptive_route_state`, `physical_wire_rc`, `protocol_deadlock_between_message_classes`。

等到第五阶段进入 deterministic NPU，模型必须新增 `route_id`, `static_schedule_slot`, `traffic_class`, `endpoint_service_curve`。换句话说，这页不是课程导航而已，它实际上定义了“什么时候该把哪些变量引入你的 simulator 或分析框架”。
