# 推荐阅读顺序：面向 Workload-Based NoC 架构分析

上级：[建模与评估](./README.md)

相关：[从 Workload 到 Traffic Trace 操作手册](./from-workload-to-traffic-trace.md)、[架构分析题库 / 决策模板 / 自测清单](./architecture-analysis-playbook.md)

## 这页给谁看

这页是给你这种目标很明确的读者：

- 不是想“泛泛了解 NoC”
- 而是想尽快达到”能基于 workload（工作负载）做架构建模和分析”

所以这里不给全量目录，而给最短有效主线。

## 一条最短主线

如果你时间有限，按下面 12 步读：

1. [NoC（片上网络）在解决什么问题](../01-overview/problem-statement.md)
2. [AI Dataflow NoC vs CPU Coherent NoC](../04-ai-dataflow-system/ai-vs-cpu-noc.md)
3. [Packet（数据包）/ Flit（流控单元）/ Wormhole（虫孔转发）](../02-router-microarchitecture/packet-flit-wormhole.md)
4. [Credit（信用计数）/ Backpressure（反压）](../02-router-microarchitecture/credit-backpressure.md)
5. [VC（虚通道）/ Deadlock（死锁）](../02-router-microarchitecture/virtual-channel-deadlock.md)
6. [Topology（拓扑）与物理布局](../03-topology-routing/topology-layout.md)
7. [Routing（路由）与 Arbitration（仲裁）](../03-topology-routing/routing-arbitration.md)
8. [Memory-Centric NoC（以存储为中心的片上网络）](../04-ai-dataflow-system/memory-centric-noc.md)
9. [流量模式](../04-ai-dataflow-system/traffic-patterns.md)
10. [从 Workload 到 Traffic Trace 操作手册](./from-workload-to-traffic-trace.md)
11. [架构探索方法](./architecture-exploration.md)
12. [架构分析题库 / 决策模板 / 自测清单](./architecture-analysis-playbook.md)

读完这 12 步，你已经具备开始做 first-order 建模分析的能力。

## 如果你要更稳一点，再补这 8 页

1. [Router Pipeline（路由器流水线）与 Allocator（分配器）](../02-router-microarchitecture/router-pipeline-allocator.md)
2. [QoS（服务质量）、公平性与 Stall Taxonomy（停顿分类体系）](./qos-fairness-stall-taxonomy.md)
3. [Source Routing（源路由）与 Compiler-Driven NoC（编译器驱动的片上网络）](../03-topology-routing/source-routing-compiler-driven-noc.md)
4. [Hierarchical NoC（层次化片上网络）深化](../03-topology-routing/hierarchical-noc-deep-dive.md)
5. [KV Cache（键值缓存）/ Decode Memory Path（解码存储路径）深化](../04-ai-dataflow-system/kv-cache-decode-memory-path.md)
6. [SRAM Bank Conflict（静态存储体冲突）/ Local Memory System](../04-ai-dataflow-system/sram-bank-conflict-local-memory-system.md)
7. [DMA Engine（直接内存访问引擎）/ Request-Response Scheduling](../04-ai-dataflow-system/dma-engine-request-response-scheduling.md)
8. [Buffer Depth（缓冲深度）/ Credit Sizing（信用值定量）/ Allocator Policy](../02-router-microarchitecture/buffer-depth-credit-sizing-allocator-policy.md)

这 8 页会把你的判断从“能开始”推到“更不容易误判”。

## 如果你要按 workload 来读

### 目标 1：做 GEMM / 规则数据流分析

优先读：

1. [GEMM（通用矩阵乘法）Case Study](../04-ai-dataflow-system/workload-gemm-case-study.md)
2. [Collective Communication（集合通信）](../04-ai-dataflow-system/collective-communication.md)
3. [Hierarchical NoC 深化](../03-topology-routing/hierarchical-noc-deep-dive.md)
4. [Mesh（网格拓扑）专题](../03-topology-routing/mesh-deep-dive.md)

### 目标 2：做 decode / KV 路径分析

优先读：

1. [Attention Decode（注意力解码）Case Study](../04-ai-dataflow-system/workload-attention-decode-case-study.md)
2. [Memory-Centric NoC](../04-ai-dataflow-system/memory-centric-noc.md)
3. [KV Cache / Decode Memory Path 深化](../04-ai-dataflow-system/kv-cache-decode-memory-path.md)
4. [QoS、公平性与 Stall Taxonomy](./qos-fairness-stall-taxonomy.md)
5. [DMA Engine / Request-Response Scheduling](../04-ai-dataflow-system/dma-engine-request-response-scheduling.md)

### 目标 3：做 MoE / dynamic traffic 分析

优先读：

1. [MoE（混合专家模型）Case Study](../04-ai-dataflow-system/workload-moe-case-study.md)
2. [Collective Communication](../04-ai-dataflow-system/collective-communication.md)
3. [Collective Implementation 深化](../04-ai-dataflow-system/collective-implementation-deep-dive.md)
4. [Topology Family 深化：Mesh / Torus（环面）/ Ring（环）/ Tree（树）/ Fat-Tree（胖树）](../03-topology-routing/topology-family-deep-dive.md)
5. [QoS、公平性与 Stall Taxonomy](./qos-fairness-stall-taxonomy.md)

## 如果你容易在概念里打转

读到这里就停下来做一次练习：

1. 随便选一个 workload
2. 用 [从 Workload 到 Traffic Trace（流量轨迹）操作手册](./from-workload-to-traffic-trace.md) 写出最小 trace
3. 用 [架构分析题库 / 决策模板 / 自测清单](./architecture-analysis-playbook.md) 回答 8 个主问题

只要你能完成这两步，说明你已经不是“只是在看文档”，而是在进入分析状态。

## 最后读哪些页

这些页更适合在你已经会分析之后再回来看：

- [CPU/Cache Coherent NoC 对照专题](../04-ai-dataflow-system/cpu-cache-coherent-noc-reference.md)
- [Physical Realization 与 Floorplan-Aware NoC（布局感知的片上网络）](../04-ai-dataflow-system/physical-realization-floorplan-aware-noc.md)
- [第一批真实 NoC / Accelerator Case Cards](./first-batch-real-noc-accelerator-case-cards.md)
- [第一批具体论文卡与架构实例卡](./first-batch-concrete-paper-architecture-cards.md)

它们更适合帮助你建立更高层的判断，不是最短入门路径的一部分。

## 一句话收尾

如果你的目标是“读完 wiki 后，足够支持我做基于 workload 的 NoC 架构建模和分析”，那最短有效路线不是把所有页面都看完，而是先按这页给出的主线读完，再立刻做一次 trace 提取和一次架构判断练习。
