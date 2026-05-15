<<<<<<< HEAD
# 知识地图

这页只保留章节级入口。

如果你要：

- 快速开始：看 [首页](./README.md)
- 学 router：看 [Router 微架构](./02-router-microarchitecture/README.md)
- 做建模：看 [建模与评估](./05-modeling-evaluation/README.md)

## 01 概览与问题定义

- [首页](./01-overview/README.md)

## 02 Router 微架构

- [首页](./02-router-microarchitecture/README.md)
- [Router Pipeline 与 Allocator](./02-router-microarchitecture/router-pipeline-allocator.md)
- [Buffer Depth / Credit Sizing / Allocator Policy](./02-router-microarchitecture/buffer-depth-credit-sizing-allocator-policy.md)

## 03 Topology 与 Routing

- [首页](./03-topology-routing/README.md)
- [Source Routing 与 Compiler-Driven NoC](./03-topology-routing/source-routing-compiler-driven-noc.md)
- [Hierarchical NoC 深化](./03-topology-routing/hierarchical-noc-deep-dive.md)
- [Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./03-topology-routing/topology-family-deep-dive.md)
- [Mesh 专题](./03-topology-routing/mesh-deep-dive.md)
- [Torus 与 Ring 专题](./03-topology-routing/torus-ring-deep-dive.md)
- [Tree / Fat-Tree 专题](./03-topology-routing/tree-fat-tree-deep-dive.md)
- [Crossbar 与 Concentrated Mesh](./03-topology-routing/crossbar-concentrated-mesh.md)

## 04 AI Dataflow 系统视角

- [首页](./04-ai-dataflow-system/README.md)
- [Collective Communication](./04-ai-dataflow-system/collective-communication.md)
- [Memory-Centric NoC](./04-ai-dataflow-system/memory-centric-noc.md)
- [KV Cache / Decode Memory Path 深化](./04-ai-dataflow-system/kv-cache-decode-memory-path.md)
- [SRAM Bank Conflict / Local Memory System](./04-ai-dataflow-system/sram-bank-conflict-local-memory-system.md)
- [DMA Engine / Request-Response Scheduling](./04-ai-dataflow-system/dma-engine-request-response-scheduling.md)
- [CPU/Cache Coherent NoC 对照专题](./04-ai-dataflow-system/cpu-cache-coherent-noc-reference.md)
- [Collective Implementation 深化](./04-ai-dataflow-system/collective-implementation-deep-dive.md)
- [多网络组织（Multi-Network NoC）](./04-ai-dataflow-system/multi-network-organization.md)
- [Broadcast / Multicast / Reduction 网络](./04-ai-dataflow-system/broadcast-multicast-reduction-network.md)
- [Physical Realization 与 Floorplan-Aware NoC](./04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)
- [GEMM Case Study](./04-ai-dataflow-system/workload-gemm-case-study.md)
- [Attention Prefill Case Study](./04-ai-dataflow-system/workload-attention-prefill-case-study.md)
- [Attention Decode Case Study](./04-ai-dataflow-system/workload-attention-decode-case-study.md)
- [MoE Case Study](./04-ai-dataflow-system/workload-moe-case-study.md)

## 05 建模与评估

- [首页](./05-modeling-evaluation/README.md)
- [QoS、公平性与 Stall Taxonomy](./05-modeling-evaluation/qos-fairness-stall-taxonomy.md)
- [Simulator 设计规格](./05-modeling-evaluation/simulator-design-spec.md)
- [Simulator 数据结构与伪代码](./05-modeling-evaluation/simulator-data-structures-pseudocode.md)
- [实验模板与结果模板](./05-modeling-evaluation/experiment-result-templates.md)
- [Simulator 最小实现路线](./05-modeling-evaluation/simulator-implementation-roadmap.md)
- [AI Accelerator NoC Case Cards 与论文卡模板](./05-modeling-evaluation/ai-accelerator-noc-case-cards-templates.md)
- [第一批真实 NoC / Accelerator Case Cards](./05-modeling-evaluation/first-batch-real-noc-accelerator-case-cards.md)
- [第一批具体论文卡与架构实例卡](./05-modeling-evaluation/first-batch-concrete-paper-architecture-cards.md)
- [实验结果沉淀模板与状态页](./05-modeling-evaluation/experiment-results-log-and-status.md)
- [从 Workload 到 Traffic Trace 操作手册](./05-modeling-evaluation/from-workload-to-traffic-trace.md)
- [架构分析题库 / 决策模板 / 自测清单](./05-modeling-evaluation/architecture-analysis-playbook.md)
- [推荐阅读顺序：面向 Workload-Based NoC 架构分析](./05-modeling-evaluation/recommended-reading-path-for-workload-based-analysis.md)

## 06 术语与检查清单

- [首页](./06-reference/README.md)
- [术语表](./06-reference/glossary.md)
- [检查清单](./06-reference/checklists.md)
- [从 NoC 知识到 DSL 设计](./06-reference/noc-to-dsl-bridge.md)
=======
# 知识地图

这页只保留章节级入口。

如果你要：

- 快速开始：看 [首页](./README.md)
- 学 router：看 [Router 微架构](./02-router-microarchitecture/README.md)
- 做建模：看 [建模与评估](./05-modeling-evaluation/README.md)

## 01 概览与问题定义

- [首页](./01-overview/README.md)

## 02 Router 微架构

- [首页](./02-router-microarchitecture/README.md)
- [Router Pipeline 与 Allocator](./02-router-microarchitecture/router-pipeline-allocator.md)
- [Buffer Depth / Credit Sizing / Allocator Policy](./02-router-microarchitecture/buffer-depth-credit-sizing-allocator-policy.md)

## 03 Topology 与 Routing

- [首页](./03-topology-routing/README.md)
- [Source Routing 与 Compiler-Driven NoC](./03-topology-routing/source-routing-compiler-driven-noc.md)
- [Hierarchical NoC 深化](./03-topology-routing/hierarchical-noc-deep-dive.md)
- [Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./03-topology-routing/topology-family-deep-dive.md)
- [Mesh 专题](./03-topology-routing/mesh-deep-dive.md)
- [Torus 与 Ring 专题](./03-topology-routing/torus-ring-deep-dive.md)
- [Tree / Fat-Tree 专题](./03-topology-routing/tree-fat-tree-deep-dive.md)

## 04 AI Dataflow 系统视角

- [首页](./04-ai-dataflow-system/README.md)
- [Collective Communication](./04-ai-dataflow-system/collective-communication.md)
- [Memory-Centric NoC](./04-ai-dataflow-system/memory-centric-noc.md)
- [KV Cache / Decode Memory Path 深化](./04-ai-dataflow-system/kv-cache-decode-memory-path.md)
- [SRAM Bank Conflict / Local Memory System](./04-ai-dataflow-system/sram-bank-conflict-local-memory-system.md)
- [DMA Engine / Request-Response Scheduling](./04-ai-dataflow-system/dma-engine-request-response-scheduling.md)
- [CPU/Cache Coherent NoC 对照专题](./04-ai-dataflow-system/cpu-cache-coherent-noc-reference.md)
- [Collective Implementation 深化](./04-ai-dataflow-system/collective-implementation-deep-dive.md)
- [Physical Realization 与 Floorplan-Aware NoC](./04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)
- [GEMM Case Study](./04-ai-dataflow-system/workload-gemm-case-study.md)
- [Attention Prefill Case Study](./04-ai-dataflow-system/workload-attention-prefill-case-study.md)
- [Attention Decode Case Study](./04-ai-dataflow-system/workload-attention-decode-case-study.md)
- [MoE Case Study](./04-ai-dataflow-system/workload-moe-case-study.md)

## 05 建模与评估

- [首页](./05-modeling-evaluation/README.md)
- [QoS、公平性与 Stall Taxonomy](./05-modeling-evaluation/qos-fairness-stall-taxonomy.md)
- [Simulator 设计规格](./05-modeling-evaluation/simulator-design-spec.md)
- [Simulator 数据结构与伪代码](./05-modeling-evaluation/simulator-data-structures-pseudocode.md)
- [实验模板与结果模板](./05-modeling-evaluation/experiment-result-templates.md)
- [Simulator 最小实现路线](./05-modeling-evaluation/simulator-implementation-roadmap.md)
- [AI Accelerator NoC Case Cards 与论文卡模板](./05-modeling-evaluation/ai-accelerator-noc-case-cards-templates.md)
- [第一批真实 NoC / Accelerator Case Cards](./05-modeling-evaluation/first-batch-real-noc-accelerator-case-cards.md)
- [第一批具体论文卡与架构实例卡](./05-modeling-evaluation/first-batch-concrete-paper-architecture-cards.md)
- [实验结果沉淀模板与状态页](./05-modeling-evaluation/experiment-results-log-and-status.md)
- [从 Workload 到 Traffic Trace 操作手册](./05-modeling-evaluation/from-workload-to-traffic-trace.md)
- [架构分析题库 / 决策模板 / 自测清单](./05-modeling-evaluation/architecture-analysis-playbook.md)
- [推荐阅读顺序：面向 Workload-Based NoC 架构分析](./05-modeling-evaluation/recommended-reading-path-for-workload-based-analysis.md)

## 06 术语与检查清单

- [首页](./06-reference/README.md)
- [术语表](./06-reference/glossary.md)
- [检查清单](./06-reference/checklists.md)
>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
