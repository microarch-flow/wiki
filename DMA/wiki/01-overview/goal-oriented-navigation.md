# 按目标学习 DMA

上级：[01 概览与问题定义](./README.md)

相关：[学习路线图](./learning-roadmap.md)、[知识地图](../SUMMARY.md)

## 这页在回答什么问题

如果你的目标不同，DMA 的最短学习路径也应该不同。这页不追求“覆盖最全”，而追求“以最少页面建立能立刻用于工程判断的知识骨架”。

## 目标 1：先建立系统判断力

1. [DMA 在解决什么问题](./problem-statement.md)
2. [DMA 分类框架](./taxonomy.md)
3. [传输对象与基本语义](../02-fundamentals/transfer-basics.md)
4. [调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)
5. [DMA 与 NoC](../05-system-integration/dma-and-noc.md)
6. [DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)
7. [指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)

这条路径的重点不是学会写 driver，而是快速建立“DMA 为什么会主导系统行为”的判断。读完后，你应该能把一个 DMA 问题拆成 request 注入、response 返回、memory 端点和 software-visible completion 四段。

## 目标 2：做驱动、系统软件或 bring-up

1. [缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)
2. [Non-Coherent vs Coherent DMA](../02-fundamentals/noncoherent-vs-coherent-dma.md)
3. [软件栈与编程模型](../04-programming-model/software-stack.md)
4. [队列、Doorbell 与 Completion](../04-programming-model/queues-doorbells-completions.md)
5. [同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)
6. [AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md)

这条路径的真实目标，是把“写完 descriptor 为什么还不能马上敲 doorbell”“completion 到底意味着哪一层完成”“coherent DMA 为什么仍然会出错”这些 bring-up 常见坑讲透。它比单纯背 API 更有用，因为它直接对应 bug 根因。

## 目标 3：做 AI 芯片架构或数据流设计

1. [调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)
2. [Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)
3. [DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)
4. [DMA 与 NoC](../05-system-integration/dma-and-noc.md)
5. [AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)
6. [HBM 到 Tile 的数据供给链](../07-workloads-case-studies/hbm-to-tile-data-supply-chain.md)
7. [AI Local DMA 案例卡](../07-workloads-case-studies/ai-local-dma-case-card.md)

这条路径优先回答“为什么 deterministic NPU 里 DMA 常常比算子本身更难调”。重点在于供数链、buffering、outstanding、NoC traffic shaping 和 local memory 端口冲突，而不是通用 I/O 语义。

## 目标 4：做性能分析和定位

1. [指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)
2. [从抽象模型到系统诊断](../06-performance-modeling/modeling-method.md)
3. [调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)
4. [优化与调参手册](../06-performance-modeling/optimization-playbook.md)
5. [观测、计数器与调试路径](../06-performance-modeling/debug-observability.md)
6. [DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)

这条路径适合“系统已经能跑，但跑不满、抖得厉害或尾延迟差”的场景。真正要建立的是实验分解能力，而不是一上来就盲扫所有旋钮。

## 目标 5：做论文和 IP 研究沉淀

1. [DMA 分类框架](./taxonomy.md)
2. [阅读问题清单](../09-reference-research/reading-questions.md)
3. [研究模板](../09-reference-research/study-template.md)
4. [论文卡模板](../09-reference-research/paper-card-template.md)
5. [IP 分析模板](../09-reference-research/ip-analysis-template.md)
6. [案例索引](../09-reference-research/case-index.md)

这条路径的目的是把外部材料重新投影到统一分析框架里，否则每读一个新 IP、新论文、新产品文档，都只会多记一套新名词。

## 常见误解

常见误解：`所有人都应该从 01 一路顺序读到 09`。实际上如果当前工作是 bring-up 或性能定位，按目标切路径更有效，因为你需要的是最短闭环，不是最完整覆盖。

常见误解：`性能分析路线可以跳过软件语义`。实际上很多“性能问题”最终会落到 queue 深度、doorbell 频率、completion 策略或 cache visibility 上，软件语义跳不过去。

## 一句话理解

学 DMA 最怕平均用力；按目标切路径，才能更快形成真正可落地的系统判断。

## 建模启示

目标导向阅读可以直接转成目标导向模型。做 bring-up 的模型应优先保留 `address_visibility`、`doorbell_order`、`completion_semantics`；做 AI 供数建模的模型应优先保留 `buffer_state`、`noc_injection`、`mem_port_conflict`；做性能定位的模型则优先保留 `outstanding_histogram`、`response_latency_histogram` 和 `consumer_ready_latency`。

一个实用做法是先定义 `analysis_goal`，再决定状态集合：

```text
analysis_goal = bringup | throughput | tail_latency | ai_supply
```

然后让模型按目标启用不同事件集。否则模型会同时保留太多无关细节，既慢又难解释。
