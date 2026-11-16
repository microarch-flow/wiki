# NoC Wiki Summary

本文按问题组织 NoC 的阅读顺序。每个分组列出现有文章；[专题首页](./README.md)提供学习和建模入口。

## 01 认识 NoC {#01-overview}

先明确网络要解决的问题，再区分协议、连接结构和网络组织。

- [NoC 在解决什么问题](./01-overview/problem-statement.md)
- [共享总线、Crossbar 与 NoC](./01-overview/bus-vs-noc-vs-crossbar.md)
- [设计维度与工作负载](./01-overview/taxonomy.md)
- [学习与建模路线](./01-overview/learning-roadmap.md)

## 02 路由器与逐跳流控 {#02-router-microarchitecture}

从传输单位和路由器资源出发，理解排队、分配和反压。

- [Packet、Flit 与 Phit](./02-router-microarchitecture/packet-flit-phit-hierarchy.md)
- [转发与交换方式](./02-router-microarchitecture/wormhole-vs-vct-vs-store-forward.md)
- [路由器流水线](./02-router-microarchitecture/router-pipeline-stages.md)
- [输入缓冲组织](./02-router-microarchitecture/input-buffer-organization.md)
- [虚通道基础](./02-router-microarchitecture/virtual-channel-fundamentals.md)
- [Credit 与反压](./02-router-microarchitecture/credit-based-flow-control.md)
- [VC 与交换分配](./02-router-microarchitecture/allocator-design-vc-switch.md)
- [路由器面积与功耗](./02-router-microarchitecture/router-power-area-tradeoff.md)

## 03 拓扑与物理组织 {#03-topology}

比较网络连接方式、结构指标及其物理实现代价。

- [拓扑设计指标](./03-topology/topology-design-metrics.md)
- [Mesh 与 Torus](./03-topology/mesh-and-torus.md)
- [Ring 与分层 Ring](./03-topology/ring-and-hierarchical-ring.md)
- [Tree 与 Fat-tree](./03-topology/tree-and-fat-tree.md)
- [Crossbar 与 Concentrated Mesh](./03-topology/crossbar-and-concentrated-mesh.md)
- [Flattened Butterfly 与 Dragonfly](./03-topology/flattened-butterfly-dragonfly.md)
- [层次化与混合互连](./03-topology/hierarchical-and-hybrid-topology.md)
- [拓扑与物理实现](./03-topology/topology-physical-realization.md)
- [拓扑选型](./03-topology/topology-selection-framework.md)

## 04 路由、仲裁与服务保证 {#04-routing-and-flow-control}

区分路径选择、资源仲裁、前进条件和服务策略。

- [路由算法分类](./04-routing-and-flow-control/routing-algorithm-classes.md)
- [维序路由](./04-routing-and-flow-control/dimension-order-routing.md)
- [死锁、活锁与饥饿](./04-routing-and-flow-control/deadlock-livelock-starvation.md)
- [Turn Model 与逃逸资源](./04-routing-and-flow-control/deadlock-avoidance-turn-model.md)
- [自适应路由](./04-routing-and-flow-control/adaptive-routing-tradeoffs.md)
- [Source Routing](./04-routing-and-flow-control/source-routing-for-deterministic-systems.md)
- [仲裁策略](./04-routing-and-flow-control/arbitration-policies.md)
- [QoS 与优先级](./04-routing-and-flow-control/qos-and-priority-classes.md)
- [端到端服务保证](./04-routing-and-flow-control/service-guarantees-and-latency-bounds.md)

## 05 端点与系统集成 {#05-system-integration}

沿请求和返回路径，理解网络与事务、DMA、存储及芯粒网关的边界。

- [BUS 与 NoC 的系统边界](./05-system-integration/noc-vs-bus-revisited.md)
- [网络接口 NI](./05-system-integration/ni-network-interface-design.md)
- [地址映射与路由表](./05-system-integration/address-map-and-routing-table.md)
- [事务拆分、顺序与完成](./05-system-integration/transaction-ordering-and-completion.md)
- [Tile 与 NoC 的接口](./06-ai-noc-specifics/tile-architecture-and-noc.md)
- [DMA 与 NoC](./05-system-integration/dma-engine-noc-interaction.md)
- [NoC 与存储系统](./05-system-integration/noc-meets-memory-system.md)
- [Memory-centric NoC](./06-ai-noc-specifics/memory-centric-noc.md)
- [多网络与资源隔离](./05-system-integration/multiple-physical-networks.md)
- [芯粒与跨 Die 互连](./06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)

## 06 多端通信与调度 {#06-ai-noc-specifics}

先区分集体通信的语义，再理解复制、归约、交换和通信计划。

- [集体通信基础](./06-ai-noc-specifics/collective-communication-basics.md)
- [广播、多播与复制](./06-ai-noc-specifics/broadcast-multicast-tree.md)
- [归约与 AllReduce](./06-ai-noc-specifics/reduction-and-collective-networks.md)
- [All-to-All 与通信矩阵](./06-ai-noc-specifics/all-to-all-and-traffic-matrix.md)
- [确定性与静态调度](./06-ai-noc-specifics/deterministic-noc-and-static-scheduling.md)
- [编译器与 NoC 协同](./06-ai-noc-specifics/compiler-noc-co-design.md)

## 07 工作负载与系统案例 {#workload-cases}

从任务、数据放置和阶段依赖出发，分析计算与一致性访问产生的通信。

- [工作负载与 NoC 流量](./06-ai-noc-specifics/why-ai-noc-is-different.md)
- [GEMM 通信案例](./06-ai-noc-specifics/workload-gemm-on-noc.md)
- [Attention Prefill 案例](./06-ai-noc-specifics/workload-attention-prefill.md)
- [Attention Decode 与 KV Cache 案例](./06-ai-noc-specifics/workload-attention-decode-kv-cache.md)
- [MoE 通信案例](./06-ai-noc-specifics/workload-moe-routing.md)
- [缓存一致性通信案例](./07-workload-cases/coherent-access-and-noc.md)

## 08 性能评估与架构探索 {#07-evaluation-methodology}

从流量和指标出发，建立性能界、模型与实验，再结合成本比较候选。

- [流量模式与表征](./05-system-integration/traffic-patterns-and-characterization.md)
- [延迟、吞吐与饱和](./07-evaluation-methodology/metrics-latency-throughput-saturation.md)
- [性能界与瓶颈分析](./07-evaluation-methodology/performance-bounds-and-bottlenecks.md)
- [如何选择模型粒度](./07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)
- [从工作负载到流量 Trace](./07-evaluation-methodology/from-workload-to-traffic-trace.md)
- [Trace 生成与核算实作](./07-evaluation-methodology/trace-generation-worked-example.md)
- [Stall 分类与归因](./07-evaluation-methodology/stall-taxonomy-and-attribution.md)
- [功耗、能量与面积建模](./07-evaluation-methodology/power-area-modeling.md)
- [架构探索与实验设计](./07-evaluation-methodology/architecture-exploration-loop.md)
- [实验与案例记录](./07-evaluation-methodology/case-card-template.md)

## 09 模拟器构建与验证 {#08-simulator-construction}

固定模型与时间契约，再连接端点、逐拍实作和分阶段验证。

- [模拟器设计规格](./08-simulator-construction/simulator-design-spec.md)
- [核心数据结构](./08-simulator-construction/core-data-structures.md)
- [事件推进与逐拍精度](./08-simulator-construction/event-driven-vs-cycle-accurate.md)
- [路由器逐拍推进](./08-simulator-construction/router-pipeline-pseudocode.md)
- [流量注入、分包与完成](./08-simulator-construction/traffic-injection-and-tracing.md)
- [工作负载与端点执行](./08-simulator-construction/workload-endpoint-execution.md)
- [最小逐拍仿真实作](./08-simulator-construction/minimal-cycle-simulator.md)
- [验证、校准与适用边界](./08-simulator-construction/verification-and-calibration.md)
- [参数与配置参考](./08-simulator-construction/parameter-reference.md)
- [实现路线与阶段验收](./08-simulator-construction/implementation-roadmap.md)

## 10 查阅与练习 {#09-reference}

用术语、问答和决策路径定位问题，再通过清单、练习和资料核对结论。

- [NoC 术语表](./09-reference/glossary.md)
- [高频问题](./09-reference/high-frequency-questions.md)
- [设计决策路径](./09-reference/noc-design-decision-tree.md)
- [检查清单](./09-reference/checklists.md)
- [练习与参考解答](./09-reference/exercises-and-worked-solutions.md)
- [参考资料与工具](./09-reference/references-and-tools.md)

### 原章节入口

这些导读保留原章节的说明和链接；当前阅读分组以上面的目录为准。

- [原 01 概览](./01-overview/README.md)
- [原 02 路由器微架构](./02-router-microarchitecture/README.md)
- [原 03 拓扑](./03-topology/README.md)
- [原 04 路由与流控](./04-routing-and-flow-control/README.md)
- [原 05 系统集成](./05-system-integration/README.md)
- [原 06 AI NoC](./06-ai-noc-specifics/README.md)
- [原 07 评估方法](./07-evaluation-methodology/README.md)
- [原 08 模拟器构建](./08-simulator-construction/README.md)
- [原 09 参考资料](./09-reference/README.md)
