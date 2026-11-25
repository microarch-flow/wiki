# DMA 的基础学习顺序

<span class="micro-legacy-anchor" id="学习路线图"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>
<span class="micro-legacy-anchor" id="先学角色再学对象再学节奏"></span>
<span class="micro-legacy-anchor" id="路线-1建立最小判断力"></span>
<span class="micro-legacy-anchor" id="路线-2学会从系统角度看-dma"></span>
<span class="micro-legacy-anchor" id="路线-3面向-ai-高性能系统深化"></span>
<span class="micro-legacy-anchor" id="学完以后你应该能回答"></span>
<span class="micro-legacy-anchor" id="常见误解"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>
<span class="micro-legacy-anchor" id="建模启示"></span>


上级：[概览与问题定义](./README.md)

初读可以直接[沿一项 DMA 搬运读四篇](../README.md#dma-first-reads)。本页按前置知识组织。若已经掌握这些对象，直接使用[工程目标导航](./goal-oriented-navigation.md)，无需重复通读。

## 先建立对象与地址边界

先读[问题定义](./problem-statement.md)和[传输对象](../02-fundamentals/transfer-basics.md)，再读[一条 DMA 描述符，为什么会变成多笔读写请求？](../02-fundamentals/address-descriptor-burst.md)。应能区分一次软件任务、一个描述符、若干总线事务与多个数据 beat。

随后读[地址空间与一致性](../02-fundamentals/consistency-cache-coherency.md)。能回答 CPU 地址与 DMA 地址是否相同、谁拥有 buffer、消费者何时可以读取，才适合进入软件接口。

## 再理解引擎如何推进

[引擎组成](../03-dma-microarchitecture/engine-components.md)介绍队列、地址生成、数据缓冲和完成路径。[后发的 DMA 请求先回来，数据怎样放回正确的位置？](../03-dma-microarchitecture/scheduling-outstanding.md)解释如何覆盖等待，以及有限槽位怎样限制在途工作。

自查问题是：一笔请求占用了哪些槽；每个槽由哪个事件释放；下游拒收时数据由谁保存。

## 最后连接软件与系统

读[软件栈](../04-programming-model/software-stack.md)与[DMA 已经取走描述符，软件现在能复用缓冲区吗？](../04-programming-model/queues-doorbells-completions.md)，再进入[分块与双缓冲](../04-programming-model/tiling-double-buffering.md)。此时应能分别写出提交、搬运、消费者就绪和 buffer 释放的条件。

性能分析从[指标与实验设计](../06-performance-modeling/metrics-bottlenecks.md)开始。逐步加入真实资源争用，并用[模型事件规范](../06-performance-modeling/model-schema.md)统一时间戳和延迟名。是否需要详细 NoC、DRAM 或完成中断模型，由目标问题和验证证据决定。
