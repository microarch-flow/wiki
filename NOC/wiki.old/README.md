# NoC Wiki

本目录用于把 `/mnt/e/noc/raw/` 下的对话会话，整理成一套面向 `AI 推理芯片 / AI tile dataflow / workload-driven architecture exploration` 的可持续扩展知识库。

> `NoC 不是“片上连线”的别名，而是连接 tile、SRAM、DMA、HBM 与数据流调度的分布式通信系统；真正要理解的是 NoC 如何服务 workload，以及它如何反过来限制系统吞吐。`

## Dashboard

| 你现在要做什么 | 直接入口 |
| --- | --- |
| 5 分钟快速建立判断力 | [NoC 在解决什么问题](./01-overview/problem-statement.md) |
| 第一次系统学习 NoC | [学习路线图](./01-overview/learning-roadmap.md) |
| 先抓住 router 核心 | [Packet / Flit / Wormhole](./02-router-microarchitecture/packet-flit-wormhole.md) |
| 搞懂 credit 和 compute stall | [Credit / Backpressure](./02-router-microarchitecture/credit-backpressure.md) |
| 深入看 buffer / credit / allocator 取舍 | [Buffer Depth / Credit Sizing / Allocator Policy](./02-router-microarchitecture/buffer-depth-credit-sizing-allocator-policy.md) |
| 从 AI 芯片视角理解 NoC | [AI Dataflow NoC vs CPU Coherent NoC](./04-ai-dataflow-system/ai-vs-cpu-noc.md) |
| 开始做 workload-driven 建模 | [建模层次](./05-modeling-evaluation/modeling-layers.md) |
| 开始做架构探索 | [架构探索方法](./05-modeling-evaluation/architecture-exploration.md) |
| 补齐 QoS / stall / collective 缺口 | [QoS、公平性与 Stall Taxonomy](./05-modeling-evaluation/qos-fairness-stall-taxonomy.md) / [Collective Communication](./04-ai-dataflow-system/collective-communication.md) |
| 直接开始做 simulator 设计 | [Simulator 设计规格](./05-modeling-evaluation/simulator-design-spec.md) |
| 直接进入实现细节 | [Simulator 数据结构与伪代码](./05-modeling-evaluation/simulator-data-structures-pseudocode.md) |
| 把 NoC 放回 memory 路径里理解 | [Memory-Centric NoC](./04-ai-dataflow-system/memory-centric-noc.md) |
| 细看 decode 的关键 memory 路径 | [KV Cache / Decode Memory Path 深化](./04-ai-dataflow-system/kv-cache-decode-memory-path.md) |
| 细看端点局部存储与 DMA 行为 | [SRAM Bank Conflict / Local Memory System](./04-ai-dataflow-system/sram-bank-conflict-local-memory-system.md) / [DMA Engine / Request-Response Scheduling](./04-ai-dataflow-system/dma-engine-request-response-scheduling.md) |
| 直接套实验模板与实现路线 | [实验模板与结果模板](./05-modeling-evaluation/experiment-result-templates.md) / [Simulator 最小实现路线](./05-modeling-evaluation/simulator-implementation-roadmap.md) |
| 建立完整对照系与实现约束视角 | [CPU/Cache Coherent NoC 对照专题](./04-ai-dataflow-system/cpu-cache-coherent-noc-reference.md) / [Physical Realization 与 Floorplan-Aware NoC](./04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md) |
| 深入看层级化互连 | [Hierarchical NoC 深化](./03-topology-routing/hierarchical-noc-deep-dive.md) |
| 理解 crossbar 和 cluster 化设计 | [Crossbar 与 Concentrated Mesh](./03-topology-routing/crossbar-concentrated-mesh.md) |
| 理解多网络分离设计 | [多网络组织（Multi-Network NoC）](./04-ai-dataflow-system/multi-network-organization.md) |
| 理解 broadcast/reduce 专用网络 | [Broadcast / Multicast / Reduction 网络](./04-ai-dataflow-system/broadcast-multicast-reduction-network.md) |
| 系统看 topology 家族差异 | [Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./03-topology-routing/topology-family-deep-dive.md) |
| 开始沉淀研究卡片 | [AI Accelerator NoC Case Cards 与论文卡模板](./05-modeling-evaluation/ai-accelerator-noc-case-cards-templates.md) |
| 直接参考第一批真实案例 | [第一批真实 NoC / Accelerator Case Cards](./05-modeling-evaluation/first-batch-real-noc-accelerator-case-cards.md) |
| 直接看第一批具体实例卡 | [第一批具体论文卡与架构实例卡](./05-modeling-evaluation/first-batch-concrete-paper-architecture-cards.md) |
| 开始沉淀实验结果 | [实验结果沉淀模板与状态页](./05-modeling-evaluation/experiment-results-log-and-status.md) |
| 把 workload 变成可建模输入 | [从 Workload 到 Traffic Trace 操作手册](./05-modeling-evaluation/from-workload-to-traffic-trace.md) |
| 直接拿来做架构判断训练 | [架构分析题库 / 决策模板 / 自测清单](./05-modeling-evaluation/architecture-analysis-playbook.md) |
| 按最短主线把整套 wiki 读完 | [推荐阅读顺序：面向 Workload-Based NoC 架构分析](./05-modeling-evaluation/recommended-reading-path-for-workload-based-analysis.md) |
| 从 NoC 知识设计 DSL | [从 NoC 知识到 DSL 设计](./06-reference/noc-to-dsl-bridge.md) |
| 理解 tile 与 NoC 的接口 | [Tile 微架构与 NoC 接口](./04-ai-dataflow-system/tile-architecture-noc-interface.md) |
| 理解地址空间对 NoC 的影响 | [地址空间与路由映射](./04-ai-dataflow-system/address-map-routing.md) |
| 理解编译器如何使用 NoC | [NoC 与编译器的完整接口](./03-topology-routing/noc-compiler-interface.md) |
| 理解功耗面积约束 | [NoC 功耗与面积建模](./05-modeling-evaluation/power-area-modeling.md) |
| 理解多 die 互连层次 | [Chiplet 与 Die-to-Die 互连](./04-ai-dataflow-system/chiplet-die-to-die-interconnect.md) |
| 快速查术语与 checklist | [术语表](./06-reference/glossary.md) / [检查清单](./06-reference/checklists.md) |

## 快速开始

### 路线 1：第一次学 NoC

1. [NoC 在解决什么问题](./01-overview/problem-statement.md)
2. [NoC 分类框架](./01-overview/taxonomy.md)
3. [AI Dataflow NoC vs CPU Coherent NoC](./04-ai-dataflow-system/ai-vs-cpu-noc.md)
4. [学习路线图](./01-overview/learning-roadmap.md)

### 路线 2：先把 router 微架构学透

1. [Router 微架构首页](./02-router-microarchitecture/README.md)
2. [Packet / Flit / Wormhole](./02-router-microarchitecture/packet-flit-wormhole.md)
3. [Credit / Backpressure](./02-router-microarchitecture/credit-backpressure.md)
4. [VC / Deadlock](./02-router-microarchitecture/virtual-channel-deadlock.md)
5. [QoS、公平性与 Stall Taxonomy](./05-modeling-evaluation/qos-fairness-stall-taxonomy.md)

### 路线 3：开始做建模与仿真

1. [建模层次](./05-modeling-evaluation/modeling-layers.md)
2. [流量模式](./04-ai-dataflow-system/traffic-patterns.md)
3. [指标与实验设计](./05-modeling-evaluation/metrics-experiments.md)
4. [架构探索方法](./05-modeling-evaluation/architecture-exploration.md)
5. [Source Routing 与 Compiler-Driven NoC](./03-topology-routing/source-routing-compiler-driven-noc.md)
6. [Collective Communication](./04-ai-dataflow-system/collective-communication.md)
7. [Simulator 设计规格](./05-modeling-evaluation/simulator-design-spec.md)
8. [Memory-Centric NoC](./04-ai-dataflow-system/memory-centric-noc.md)
9. [实验模板与结果模板](./05-modeling-evaluation/experiment-result-templates.md)
10. [Simulator 最小实现路线](./05-modeling-evaluation/simulator-implementation-roadmap.md)
11. [CPU/Cache Coherent NoC 对照专题](./04-ai-dataflow-system/cpu-cache-coherent-noc-reference.md)
12. [Collective Implementation 深化](./04-ai-dataflow-system/collective-implementation-deep-dive.md)
13. [Physical Realization 与 Floorplan-Aware NoC](./04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)
14. [Simulator 数据结构与伪代码](./05-modeling-evaluation/simulator-data-structures-pseudocode.md)
15. [KV Cache / Decode Memory Path 深化](./04-ai-dataflow-system/kv-cache-decode-memory-path.md)
16. [Hierarchical NoC 深化](./03-topology-routing/hierarchical-noc-deep-dive.md)
17. [SRAM Bank Conflict / Local Memory System](./04-ai-dataflow-system/sram-bank-conflict-local-memory-system.md)
18. [DMA Engine / Request-Response Scheduling](./04-ai-dataflow-system/dma-engine-request-response-scheduling.md)
19. [AI Accelerator NoC Case Cards 与论文卡模板](./05-modeling-evaluation/ai-accelerator-noc-case-cards-templates.md)
20. [Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./03-topology-routing/topology-family-deep-dive.md)
21. [Buffer Depth / Credit Sizing / Allocator Policy](./02-router-microarchitecture/buffer-depth-credit-sizing-allocator-policy.md)
22. [第一批真实 NoC / Accelerator Case Cards](./05-modeling-evaluation/first-batch-real-noc-accelerator-case-cards.md)
23. [Mesh 专题](./03-topology-routing/mesh-deep-dive.md)
24. [Torus 与 Ring 专题](./03-topology-routing/torus-ring-deep-dive.md)
25. [Tree / Fat-Tree 专题](./03-topology-routing/tree-fat-tree-deep-dive.md)
26. [第一批具体论文卡与架构实例卡](./05-modeling-evaluation/first-batch-concrete-paper-architecture-cards.md)
27. [实验结果沉淀模板与状态页](./05-modeling-evaluation/experiment-results-log-and-status.md)
28. [从 Workload 到 Traffic Trace 操作手册](./05-modeling-evaluation/from-workload-to-traffic-trace.md)
29. [架构分析题库 / 决策模板 / 自测清单](./05-modeling-evaluation/architecture-analysis-playbook.md)
30. [推荐阅读顺序：面向 Workload-Based NoC 架构分析](./05-modeling-evaluation/recommended-reading-path-for-workload-based-analysis.md)

## 工作台

### 学习

- [概览与问题定义](./01-overview/README.md)
- [Router 微架构](./02-router-microarchitecture/README.md)
- [Topology 与 Routing](./03-topology-routing/README.md)
- [AI Dataflow 系统视角](./04-ai-dataflow-system/README.md)

### 建模

- [建模与评估](./05-modeling-evaluation/README.md)
- [建模层次](./05-modeling-evaluation/modeling-layers.md)
- [指标与实验设计](./05-modeling-evaluation/metrics-experiments.md)
- [架构探索方法](./05-modeling-evaluation/architecture-exploration.md)
- [QoS、公平性与 Stall Taxonomy](./05-modeling-evaluation/qos-fairness-stall-taxonomy.md)
- [Simulator 设计规格](./05-modeling-evaluation/simulator-design-spec.md)
- [实验模板与结果模板](./05-modeling-evaluation/experiment-result-templates.md)
- [Simulator 最小实现路线](./05-modeling-evaluation/simulator-implementation-roadmap.md)

### 查阅

- [术语表](./06-reference/glossary.md)
- [检查清单](./06-reference/checklists.md)
- [知识地图](./SUMMARY.md)

## 这套 Wiki 的边界

这套 wiki 的主线不是通用 SoC 互连，也不是一致性协议本身，而是：

- 面向 `AI accelerator / tile-based architecture` 的 NoC
- 面向 `workload-driven architecture exploration` 的建模与分析
- 面向 `router microarchitecture -> traffic -> system bottleneck` 的工程判断

CPU/cache coherent NoC 会保留，但作为对照案例，而不是主学习对象。

## 维护原则

- 每页尽量只回答一个核心问题
- 优先区分 `router / topology / protocol / workload / evaluation`
- 优先保留可建模、可比较、可实验的内容
- 把“会不会成为系统瓶颈”作为统一评价标准
- 原始素材来自 `/mnt/e/noc/raw/chat_0.md` 到 `/mnt/e/noc/raw/chat_4.md`
