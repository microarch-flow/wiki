# DMA 分类框架

上级：[01 概览与问题定义](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[软件栈与编程模型](../04-programming-model/software-stack.md)、[AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md)

## 这页在回答什么问题

为什么同样叫 DMA，不同系统里的实现、接口和瓶颈会差这么多；以及在读文档、看 IP、做建模时，应该先用哪几个维度把不同 DMA 分开。

## 不要按名字分类，要按约束组合分类

很多资料喜欢把 DMA 分成“外设 DMA、AXI DMA、PCIe DMA、2D DMA、copy engine”几类。这种叫法在交流里够用，但对架构判断不够，因为名字只告诉你“它大概长在哪”，没有告诉你“它为什么必须这样设计”。更稳的做法是把 DMA 视为四组约束的组合：传输路径、控制模式、系统语义、并发组织。只要这四组约束变了，同名 DMA 也可能表现完全不同。

## 第一维：它在谁和谁之间搬

传输路径决定 DMA 的第一性问题。`memory-to-memory` 更像片上搬运基础设施；`peripheral-to-memory` 和 `memory-to-peripheral` 更关注流式实时性与 backpressure；`host-to-device / device-to-host / device-to-device` 则会立刻引入 PCIe、IOMMU 和 completion path。

路径不同，任务的“完成”定义也会不同。把数据从 DDR 搬到 local SRAM，完成往往更接近“下游计算可消费”；把数据从 NIC 写入 host buffer，完成往往还要再加上 host 软件可见这一步。后面 `02-fundamentals/transfer-basics.md` 会把这些阶段拆开。

## 第二维：谁来描述任务，任务是一次性的还是长期流动的

最简单的 DMA 是 register-programmed 的 single-shot 模式：CPU 直接把源地址、目的地址、长度写进寄存器，DMA 做完一笔就停。这种模式简单、确定、适合低复杂度 SoC，但 CPU 对每次传输都要介入，软件开销会快速放大。

descriptor-based DMA 是为了压低这种重复控制成本才出现的。它像一串预先写好的施工任务单：CPU 一次把“从哪搬到哪、搬多少、搬完做什么”写进内存，DMA 自己顺着任务单执行。这个类比在 linked-list descriptor 上成立，因为任务天然按线性顺序消费；到 ring descriptor 时要补一句，ring 不是一张一次性用完的任务单，而是一个循环复用的任务槽位集合。

再往上，queue-based 或 command-queue DMA 更接近异步执行引擎。它们强调批量提交、多队列、doorbell、completion 和流量整形，常见于高吞吐设备和加速器。

## 第三维：它处在什么系统语义里

这一维最容易被忽略，但它会直接改变 DMA 的软件接口和硬件复杂度。一个只在裸物理地址空间里工作的 non-coherent 外设 DMA，与一个支持 IOMMU、虚拟化、coherent access 的设备 DMA，表面上都在“搬数据”，实际上服务的是完全不同的系统契约。

这里的关键不是给 DMA 贴上“高级”或“低级”的标签，而是明确谁承担复杂度。non-coherent DMA 把一致性劳动更多留给软件；coherent DMA 把一部分复杂度推给互连和缓存协议；带 IOMMU 的 DMA 又进一步引入地址翻译与隔离语义。后面 `02-fundamentals/noncoherent-vs-coherent-dma.md` 会把这个对比讲尖锐。

## 第四维：它如何组织并发

两个 DMA 都支持 100 GB/s 峰值，仍可能因为并发组织不同而体验天差地别。单通道、小 outstanding 窗口的 DMA 更容易验证，也更利于低功耗；多通道、多队列、大窗口、带 QoS 和重排能力的 DMA 能更好隐藏 latency，但会引入更复杂的回包组织和更高的系统扰动。

这里直接连到 [BUS wiki 的 AXI channel / ID / outstanding](../../BUS/wiki/03-on-chip-protocol-families/axi-channel-id-outstanding.md) 与 [NOC wiki 的流量模式](../../NOC/wiki/07-evaluation-methodology/from-workload-to-traffic-trace.md)。DMA 从来不是“独立吞吐器件”，而是请求注入器、返回流组织器和系统流量塑形器。

## 一个工程上更有用的分类问法

与其问“这是什么 DMA”，不如先问五个问题：

1. 数据在谁和谁之间搬，这条路径上最慢的端点是谁。
2. 任务是寄存器触发、descriptor 链、ring，还是 command queue。
3. 地址是物理地址、IOVA，还是更高层的虚拟工作流。
4. completion 指的是 descriptor 被取走、数据写完，还是软件可见。
5. 真正限制它的是 submit、interconnect、memory return path、destination ejection，还是软件消费节拍。

## 常见误解

常见误解：`2D DMA 比 1D DMA 更高级，所以一定更好`。实际上 2D/3D 地址生成是为了减少软件循环和 descriptor 膨胀，代价是更复杂的边界拆分与验证压力。

常见误解：`支持 queue 的 DMA 一定比寄存器 DMA 更先进`。实际上在固定功能、强实时、低复杂度外设里，寄存器 DMA 反而更合适，因为它减少了状态机和软件契约复杂度。

常见误解：`coherent DMA 是分类标签里唯一重要的那一维`。实际上 coherent 只描述系统语义的一部分，传输路径和并发组织同样会主导性能。

## 一句话理解

DMA 的分类关键不是名字，而是 `路径谁在搬、任务谁在描述、系统语义谁在约束、并发谁在组织` 这四件事的组合。

## 建模启示

分类页的建模价值在于先决定模型粒度。对 event-driven 仿真，至少要先给 DMA 贴上 `path_type`、`control_model`、`coherence_mode`、`queue_model` 四个标签，否则后面根本无法决定该保留哪些状态。

一个可直接落地的数据结构草图是：

```text
DMAClass {
  path_type: mem2mem | periph2mem | host2dev | local2local
  control_model: register | linked_list | ring | cmd_queue
  coherence_mode: noncoherent | coherent | iommu_backed
  concurrency_model: {channels, queues, max_outstanding}
}
```

如果只关心高层方案比较，这四个字段就足够把大多数 DMA 放进正确类别；如果关心功能正确性，就还要补 `completion_semantics` 和 `address_visibility_domain`，否则不同系统的“done”会被错误地当成同一种事件。
