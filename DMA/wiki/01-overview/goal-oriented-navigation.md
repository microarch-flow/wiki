# 按目标学习 DMA

上级：[01 概览与问题定义](./README.md)

相关：[学习路线图](./learning-roadmap.md)、[知识地图](../SUMMARY.md)

## 这页在回答什么问题

如果你的目标不同，DMA 的阅读顺序也应该不同。这页给出按目标切分的最短学习路径。

## 目标 1：先建立系统判断力

1. [DMA 在解决什么问题](./problem-statement.md)
2. [DMA 分类框架](./taxonomy.md)
3. [传输对象与基本语义](../02-fundamentals/transfer-basics.md)
4. [DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)
5. [DMA 与 NoC](../05-system-integration/dma-and-noc.md)
6. [指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)

## 目标 2：做驱动、系统软件或 bring-up

1. [缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)
2. [Non-Coherent vs Coherent DMA](../02-fundamentals/noncoherent-vs-coherent-dma.md)
3. [软件栈与编程模型](../04-programming-model/software-stack.md)
4. [队列、Doorbell 与 Completion](../04-programming-model/queues-doorbells-completions.md)
5. [同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)
6. [AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md)

## 目标 3：做 AI 芯片架构或数据流设计

1. [AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)
2. [Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)
3. [调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)
4. [DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)
5. [HBM 到 Tile 的数据供给链](../07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)
6. [AI Local DMA 案例卡](../07-workloads-case-studies/ai-local-dma-case-card.md)

## 目标 4：做性能分析和定位

1. [指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)
2. [从抽象模型到系统诊断](../06-performance-modeling/modeling-method.md)
3. [优化与调参手册](../06-performance-modeling/optimization-playbook.md)
4. [观测、计数器与调试路径](../06-performance-modeling/debug-observability.md)
5. [DMA IP 评估清单](../08-industry-ip/dma-ip-checklist.md)
6. [DMA 对照矩阵](../08-industry-ip/dma-comparison-matrix.md)

## 目标 5：做论文和 IP 研究沉淀

1. [阅读问题清单](../09-reference-research/reading-questions.md)
2. [研究模板](../09-reference-research/study-template.md)
3. [论文卡模板](../09-reference-research/paper-card-template.md)
4. [IP 分析模板](../09-reference-research/ip-analysis-template.md)
5. [案例索引](../09-reference-research/case-index.md)

## 一句话理解

学 DMA 最怕平均用力。先按目标选路径，能显著提高阅读效率，也更容易形成真正可用的判断。
