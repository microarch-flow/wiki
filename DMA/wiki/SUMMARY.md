# 知识地图

这页只保留章节级入口。

如果你要：

- 快速开始：看 [首页](./README.md)
- 系统学习：看 [学习路线图](./01-overview/learning-roadmap.md)
- 做性能分析：看 [性能建模与调优](./06-performance-modeling/README.md)

## 01 概览与问题定义

- [首页](./01-overview/README.md)
- [DMA 在解决什么问题](./01-overview/problem-statement.md)
- [DMA 分类框架](./01-overview/taxonomy.md)
- [学习路线图](./01-overview/learning-roadmap.md)
- [按目标学习 DMA](./01-overview/goal-oriented-navigation.md)

## 02 基础对象与传输语义

- [首页](./02-fundamentals/README.md)
- [传输对象与基本语义](./02-fundamentals/transfer-basics.md)
- [缓存一致性、IOMMU 与地址空间](./02-fundamentals/consistency-cache-coherency.md)
- [地址、描述符与 Burst](./02-fundamentals/address-descriptor-burst.md)
- [Non-Coherent vs Coherent DMA](./02-fundamentals/noncoherent-vs-coherent-dma.md)

## 03 DMA 引擎微架构

- [首页](./03-dma-microarchitecture/README.md)
- [DMA 引擎的组成](./03-dma-microarchitecture/engine-components.md)
- [调度、Outstanding 与回包组织](./03-dma-microarchitecture/scheduling-outstanding.md)
- [多通道、虚拟化与隔离](./03-dma-microarchitecture/channels-virtualization.md)
- [多维 DMA 与 Stride 地址生成](./03-dma-microarchitecture/multidimensional-stride-dma.md)

## 04 软件栈与编程模型

- [首页](./04-programming-model/README.md)
- [软件栈与编程模型](./04-programming-model/software-stack.md)
- [同步、一致性与常见错误](./04-programming-model/synchronization-errors.md)
- [Tiling、Double Buffer 与 Overlap](./04-programming-model/tiling-double-buffering.md)
- [队列、Doorbell 与 Completion](./04-programming-model/queues-doorbells-completions.md)

## 05 系统集成

- [首页](./05-system-integration/README.md)
- [DMA 与 NoC](./05-system-integration/dma-and-noc.md)
- [DMA 与 Local Memory / DDR / HBM](./05-system-integration/dma-and-memory-system.md)
- [SoC 外设与 I/O DMA](./05-system-integration/soc-peripheral-io.md)
- [AXI / PCIe 视角下的 DMA](./05-system-integration/axi-pcie-view.md)

## 06 性能建模与调优

- [首页](./06-performance-modeling/README.md)
- [指标、瓶颈与实验设计](./06-performance-modeling/metrics-bottlenecks.md)
- [从抽象模型到系统诊断](./06-performance-modeling/modeling-method.md)
- [参数与公式速查](./06-performance-modeling/parameter-reference.md)
- [模型数据结构与事件规范](./06-performance-modeling/model-schema.md)
- [校准与验证](./06-performance-modeling/calibration-validation.md)
- [旋钮敏感度与耦合](./06-performance-modeling/sensitivity-coupling.md)
- [优化与调参手册](./06-performance-modeling/optimization-playbook.md)
- [观测、计数器与调试路径](./06-performance-modeling/debug-observability.md)

## 07 工作负载与案例

- [首页](./07-workloads-case-studies/README.md)
- [AI 加速器里的 DMA](./07-workloads-case-studies/ai-accelerator-dma.md)
- [CPU / GPU / NPU 系统中的 DMA 分工](./07-workloads-case-studies/cpu-gpu-npu-comparison.md)
- [嵌入式多媒体与存储/网络路径](./07-workloads-case-studies/embedded-storage-network.md)
- [HBM 到 Tile 的数据供给链](./07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)
- [AXI DMA 案例卡](./07-workloads-case-studies/axi-dma-case-card.md)
- [PCIe NIC DMA 案例卡](./07-workloads-case-studies/pcie-nic-dma-case-card.md)
- [NVMe / 存储路径中的 DMA](./07-workloads-case-studies/nvme-storage-dma-case-card.md)
- [GPU Copy Engine 案例卡](./07-workloads-case-studies/gpu-copy-engine-case-card.md)
- [AI Local DMA 案例卡](./07-workloads-case-studies/ai-local-dma-case-card.md)

## 08 DMA IP 与产业视角

- [首页](./08-industry-ip/README.md)
- [DMA IP 与厂商图谱](./08-industry-ip/vendor-landscape.md)
- [DMA IP 评估清单](./08-industry-ip/dma-ip-checklist.md)
- [DMA 对照矩阵](./08-industry-ip/dma-comparison-matrix.md)

## 09 参考资料与研究模板

- [首页](./09-reference-research/README.md)
- [术语表](./09-reference-research/glossary.md)
- [研究模板](./09-reference-research/study-template.md)
- [阅读问题清单](./09-reference-research/reading-questions.md)
- [论文卡模板](./09-reference-research/paper-card-template.md)
- [IP 分析模板](./09-reference-research/ip-analysis-template.md)
- [案例索引](./09-reference-research/case-index.md)
