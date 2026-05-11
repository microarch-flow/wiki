# DMA Wiki

> `DMA 不是“免 CPU 搬数据”这么简单，而是系统里负责把带宽、时序、并发和数据依赖组织起来的一层执行机制。要真正理解 DMA，必须同时看传输对象、描述符、burst、outstanding、缓存一致性、NoC、local memory、driver/runtime 以及 workload。`

## Dashboard

| 你现在要做什么 | 直接入口 |
| --- | --- |
| 5 分钟快速建立判断力 | [DMA 在解决什么问题](./01-overview/problem-statement.md) |
| 第一次系统学习 DMA | [学习路线图](./01-overview/learning-roadmap.md) |
| 按目标选阅读路径 | [按目标学习 DMA](./01-overview/goal-oriented-navigation.md) |
| 先把 DMA 基础对象学清楚 | [传输对象与基本语义](./02-fundamentals/transfer-basics.md) |
| 先理解 burst / descriptor / scatter-gather | [地址、描述符与 Burst](./02-fundamentals/address-descriptor-burst.md) |
| 搞懂 coherent DMA 和 IOMMU | [缓存一致性、IOMMU 与地址空间](./02-fundamentals/consistency-cache-coherency.md) |
| 直接进入 DMA engine 设计 | [DMA 引擎的组成](./03-dma-microarchitecture/engine-components.md) |
| 抓住最关键的性能主线 | [调度、Outstanding 与回包组织](./03-dma-microarchitecture/scheduling-outstanding.md) |
| 细看 2D/3D/stride 搬运 | [多维 DMA 与 Stride 地址生成](./03-dma-microarchitecture/multidimensional-stride-dma.md) |
| 从软件视角理解 DMA | [软件栈与编程模型](./04-programming-model/software-stack.md) |
| 少踩同步和 cache 坑 | [同步、一致性与常见错误](./04-programming-model/synchronization-errors.md) |
| 把软件接口落到 ring/doorbell/completion | [队列、Doorbell 与 Completion](./04-programming-model/queues-doorbells-completions.md) |
| 看 DMA 如何嵌入 SoC / AI 系统 | [DMA 与 NoC / Memory System](./05-system-integration/dma-and-noc.md) |
| 从总线协议理解 DMA 约束 | [AXI / PCIe 视角下的 DMA](./05-system-integration/axi-pcie-view.md) |
| 开始做性能分析或建模 | [指标、瓶颈与实验设计](./06-performance-modeling/metrics-bottlenecks.md) |
| 开始做调试定位 | [观测、计数器与调试路径](./06-performance-modeling/debug-observability.md) |
| 直接看场景化案例 | [AI 加速器里的 DMA](./07-workloads-case-studies/ai-accelerator-dma.md) |
| 直接走一遍 AI 芯片完整数据路径 | [HBM 到 Tile 的数据供给链](./07-workloads-case-studies/hbm-to-tile-data-supply-chain.md) |
| 对照典型 DMA 案例 | [AXI DMA 案例卡](./07-workloads-case-studies/axi-dma-case-card.md) / [PCIe NIC DMA 案例卡](./07-workloads-case-studies/pcie-nic-dma-case-card.md) |
| 评估 DMA IP 或做方案选型 | [DMA IP 评估清单](./08-industry-ip/dma-ip-checklist.md) |
| 快速横向比较 DMA 类型 | [DMA 对照矩阵](./08-industry-ip/dma-comparison-matrix.md) |
| 沉淀论文/IP 研究卡片 | [论文卡模板](./09-reference-research/paper-card-template.md) / [IP 分析模板](./09-reference-research/ip-analysis-template.md) |
| 统一术语与记录模板 | [术语表](./09-reference-research/glossary.md) / [研究模板](./09-reference-research/study-template.md) |

## 快速开始

### 路线 1：第一次学 DMA

1. [DMA 在解决什么问题](./01-overview/problem-statement.md)
2. [DMA 分类框架](./01-overview/taxonomy.md)
3. [传输对象与基本语义](./02-fundamentals/transfer-basics.md)
4. [地址、描述符与 Burst](./02-fundamentals/address-descriptor-burst.md)
5. [学习路线图](./01-overview/learning-roadmap.md)

### 路线 2：想把 DMA engine 学透

1. [DMA 引擎的组成](./03-dma-microarchitecture/engine-components.md)
2. [调度、Outstanding 与回包组织](./03-dma-microarchitecture/scheduling-outstanding.md)
3. [多通道、虚拟化与隔离](./03-dma-microarchitecture/channels-virtualization.md)
4. [DMA 与 NoC](./05-system-integration/dma-and-noc.md)
5. [DMA 与 Local Memory / DDR / HBM](./05-system-integration/dma-and-memory-system.md)
6. [多维 DMA 与 Stride 地址生成](./03-dma-microarchitecture/multidimensional-stride-dma.md)
7. [AXI / PCIe 视角下的 DMA](./05-system-integration/axi-pcie-view.md)
8. [AXI DMA 案例卡](./07-workloads-case-studies/axi-dma-case-card.md)
9. [PCIe NIC DMA 案例卡](./07-workloads-case-studies/pcie-nic-dma-case-card.md)

### 路线 3：想从软件和系统角度建立判断

1. [软件栈与编程模型](./04-programming-model/software-stack.md)
2. [同步、一致性与常见错误](./04-programming-model/synchronization-errors.md)
3. [Tiling、Double Buffer 与 Overlap](./04-programming-model/tiling-double-buffering.md)
4. [指标、瓶颈与实验设计](./06-performance-modeling/metrics-bottlenecks.md)
5. [优化与调参手册](./06-performance-modeling/optimization-playbook.md)
6. [观测、计数器与调试路径](./06-performance-modeling/debug-observability.md)
7. [HBM 到 Tile 的数据供给链](./07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)
8. [NVMe / 存储路径中的 DMA](./07-workloads-case-studies/nvme-storage-dma-case-card.md)
9. [GPU Copy Engine 案例卡](./07-workloads-case-studies/gpu-copy-engine-case-card.md)

## 工作台

### 学习

- [概览与问题定义](./01-overview/README.md)
- [按目标学习 DMA](./01-overview/goal-oriented-navigation.md)
- [基础对象与传输语义](./02-fundamentals/README.md)
- [DMA 引擎微架构](./03-dma-microarchitecture/README.md)
- [软件栈与编程模型](./04-programming-model/README.md)
- [系统集成](./05-system-integration/README.md)
- [AI 芯片 DMA 主线案例](./07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)

### 分析

- [性能建模与调优](./06-performance-modeling/README.md)
- [工作负载与案例](./07-workloads-case-studies/README.md)
- [DMA IP 与产业视角](./08-industry-ip/README.md)
- [观测、计数器与调试路径](./06-performance-modeling/debug-observability.md)
- [DMA 对照矩阵](./08-industry-ip/dma-comparison-matrix.md)

### 查阅

- [参考资料与研究模板](./09-reference-research/README.md)
- [知识地图](./SUMMARY.md)
- [论文卡模板](./09-reference-research/paper-card-template.md)
- [IP 分析模板](./09-reference-research/ip-analysis-template.md)
- [案例索引](./09-reference-research/case-index.md)

## 这套 Wiki 的边界

这套 wiki 的主线不是：

- 泛泛介绍“DMA 是什么”
- 只讲 MCU 外设搬运
- 只讲 Linux 驱动 API

这套 wiki 的主线是：

- 把 DMA 作为 `系统数据移动层` 来理解
- 同时覆盖 `SoC / accelerator / NoC / DDR-HBM / driver-runtime`
- 建立 `能解释性能、能解释 stall、能支持方案判断` 的知识结构

## 维护原则

- 每页尽量只回答一个核心问题
- 优先区分 `传输语义 / 引擎实现 / 软件编排 / 系统瓶颈`
- 优先保留能转化成工程判断和实验设计的内容
- 与 `NOC`、`CIM` 等相邻主题保持可互相链接的术语体系
