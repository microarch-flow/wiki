# 学习路线图

上级：[01 概览与问题定义](./README.md)

相关：[Router 微架构](../02-router-microarchitecture/README.md)、[建模层次](../05-modeling-evaluation/modeling-layers.md)

## 推荐学习顺序

### 第一阶段：建立最小心智模型

目标：

- 知道 packet、flit、phit 的关系
- 知道 wormhole 为什么能小 buffer 低延迟
- 知道 credit/backpressure 为什么会影响 compute stall

入口：

1. [AI Dataflow NoC vs CPU Coherent NoC](../04-ai-dataflow-system/ai-vs-cpu-noc.md)
2. [Packet / Flit / Wormhole](../02-router-microarchitecture/packet-flit-wormhole.md)
3. [Credit / Backpressure](../02-router-microarchitecture/credit-backpressure.md)

### 第二阶段：理解 router 不是黑盒

目标：

- 知道 router pipeline 的基本阶段
- 知道 switch stall 和 credit stall 的差别
- 知道为什么需要 VC 和资源隔离

入口：

1. [Router 微架构首页](../02-router-microarchitecture/README.md)
2. [VC / Deadlock](../02-router-microarchitecture/virtual-channel-deadlock.md)

### 第三阶段：补齐网络层

目标：

- 理解 topology、routing、arbitration、QoS
- 能比较 flat mesh 与 cluster-hierarchical 方案

入口：

1. [Topology 与物理布局](../03-topology-routing/topology-layout.md)
2. [Routing 与 Arbitration](../03-topology-routing/routing-arbitration.md)

### 第四阶段：把 NoC 放回系统

目标：

- 理解 NI、DMA、SRAM、HBM 接口
- 理解 traffic 是如何从 workload 和 mapping 里长出来的

入口：

1. [NI / DMA / 存储接口](../04-ai-dataflow-system/ni-dma-memory-interface.md)
2. [流量模式](../04-ai-dataflow-system/traffic-patterns.md)

### 第五阶段：开始做架构探索

目标：

- 从理想到 flit-level 逐级建模
- 用统一指标比较不同 NoC 方案
- 输出 first-order architectural insight

入口：

1. [建模层次](../05-modeling-evaluation/modeling-layers.md)
2. [指标与实验设计](../05-modeling-evaluation/metrics-experiments.md)
3. [架构探索方法](../05-modeling-evaluation/architecture-exploration.md)

## 当前知识够不够开始建模

结论：

可以开始，但只够第一版。

你已经可以做：

- 简化 mesh / XY routing / wormhole / credit 的 flit-level 模型
- synthetic traffic 和基础 AI-like traffic 的拥塞分析
- placement、packet size、buffer depth 的一阶对比

但如果要支撑更强的架构结论，还要补齐：

- VC / deadlock
- topology / routing 比较
- NI / DMA / destination buffering
- workload traffic 建模
- 指标体系与实验方法
