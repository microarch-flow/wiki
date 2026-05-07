# 学习路线图

上级：[01 概览与问题定义](./README.md)

相关：[知识地图](../SUMMARY.md)

## 这页在回答什么问题

如果你的目标不是背概念，而是系统掌握 DMA，该按什么顺序学。

## 路线 1：建立最小判断力

1. [DMA 在解决什么问题](./problem-statement.md)
2. [DMA 分类框架](./taxonomy.md)
3. [传输对象与基本语义](../02-fundamentals/transfer-basics.md)
4. [地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)
5. [DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)

## 路线 2：学会从系统角度看 DMA

1. [软件栈与编程模型](../04-programming-model/software-stack.md)
2. [同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)
3. [DMA 与 NoC](../05-system-integration/dma-and-noc.md)
4. [DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)
5. [指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)

## 路线 3：面向 AI / 高性能系统深化

1. [调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)
2. [Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)
3. [AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)
4. [从抽象模型到系统诊断](../06-performance-modeling/modeling-method.md)
5. [优化与调参手册](../06-performance-modeling/optimization-playbook.md)

## 学完以后你应该能回答

- 为什么某些系统里 DMA 比 compute 更像真正瓶颈
- 为什么带宽看着够，系统还是会 stall
- 为什么同一个 DMA IP 放到不同系统里效果差异很大
- 如何把 DMA 问题分解到 software、engine、NoC、memory endpoint

## 一句话理解

学 DMA 的正确顺序不是“先记接口”，而是 `先懂角色，再懂对象，再懂引擎，再懂系统，再懂性能`。
