# 软件栈与编程模型

上级：[04 软件栈与编程模型](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)、[SoC 外设与 I/O DMA](../05-system-integration/soc-peripheral-io.md)

## 这页在回答什么问题

DMA 为什么既是硬件模块，也是 software contract；以及应用、runtime、driver、OS 和 DMA engine 各自到底承担什么责任。

## DMA 的软件栈不是“给硬件下命令”，而是建立长期契约

很多人第一次接触 DMA 时，会把它看成“CPU 写几个寄存器，硬件去搬数据”。这种说法只适合最简单的 single-shot DMA。只要系统进入 descriptor、queue、IOMMU、completion record 或 runtime 调度这些语境，DMA 就不再只是命令接口，而是一套跨多层软件的长期契约。

这套契约至少要回答四个问题：

- 谁负责产生数据移动需求
- 谁把需求翻译成 descriptor 或 command
- 谁保证这些对象对 DMA 可见且地址合法
- 谁在完成后回收 buffer、映射和软件状态

如果这四件事没有说清楚，再优秀的 DMA 硬件也会被软件时序拖垮。

## 典型的软件分层各在做什么

最常见的一条路径是：

- 应用或 runtime 决定“下一步该搬什么”
- driver 负责准备 descriptor、管理 queue、处理 completion
- OS / IOMMU 提供地址映射、权限和中断基础设施
- DMA engine 负责执行真正的数据移动

在 AI 系统里，编译器和 runtime 的作用会更重，因为它们可能直接决定 tile 粒度、double buffer 节拍和预取顺序；在 NIC/NVMe 这类设备里，driver 和 OS 的作用更重，因为 ring、mapping、interrupt moderation 和用户态 buffer 生命周期都落在软件栈里。

## 地址桥接是软件栈里最容易被低估的一层

CPU、runtime 或用户态最先看到的往往是虚拟地址，但 DMA 真正使用的常常是物理地址、IOVA 或其他 device-visible 地址。这中间的桥接不是小细节，而是 DMA 契约的一部分。软件如果只把“数据内容”准备好了，却没有把“设备视角里的地址与生命周期”准备好，DMA 根本不可能正确工作。

这也是为什么很多问题会表现成“descriptor 看起来没错，但 DMA 仍然 fault”或者“completion 到了，但 buffer 复用后随机脏数据”。问题不在数据本身，而在软件没有把地址空间和所有权一起管理好。

## 三种常见控制模式，对应三种软件责任

寄存器触发的 single-shot DMA 最简单。软件每次显式配置一次，硬件做完一笔就停。优点是确定、薄、好 bring-up；缺点是 CPU 要频繁介入，无法支撑高提交率场景。

descriptor / ring 模式把责任改写成“软件持续维护任务池，硬件持续消费任务池”。软件的工作不再是发单次命令，而是维护 producer/consumer 边界、buffer 生命周期和 completion 回收。

runtime / compiler 计划驱动的 DMA 又更进一步。软件不一定逐笔 submit，而是提前把一批搬运计划编织进更大的执行图里。此时 DMA 已经不再只是 I/O 辅助块，而是程序执行图的一部分。

## 软件真正影响性能的地方在哪里

软件对 DMA 性能的影响，不主要体现在“调用哪个 API”，而体现在它如何塑造任务形状和时序：

- 任务切分粒度是否过碎
- queue 深度是否足以支撑 steady-state
- doorbell 是否敲得过频
- completion 是用 interrupt、polling 还是混合策略
- tile 与 buffer 设计是否为 overlap 留空间

也就是说，软件并不只是发起者，它还是流量形状的塑造者。很多系统里 DMA 的“硬件性能”其实高度依赖软件是否给了它一个可被高效执行的任务序列。

## 常见误解

常见误解：`DMA 软件栈就是 driver API`。实际上 runtime、compiler、OS、IOMMU 和 buffer 生命周期管理同样是软件契约的一部分。

常见误解：`地址映射只在 PCIe 设备里重要`。实际上只要系统里有 IOMMU、SMMU 或多地址空间，映射就直接决定 DMA 是否能工作。

常见误解：`性能问题主要发生在硬件`。实际上软件切分粒度、queue 维护和同步策略本身就会决定 DMA 能否进入高效 steady-state。

## 一句话理解

DMA 的软件栈本质上是在定义数据移动任务如何被描述、提交、同步、完成并回收，而不是单纯“把命令发给硬件”。

## 建模启示

如果模型没有软件前端，很多真实 DMA 现象会消失。event-driven 仿真里，至少应显式保留 `submit_batch_size`、`doorbell_interval`、`mapping_ready`、`completion_consume_rate` 这几类软件侧状态。

一个最小软件前端结构可以是：

```text
DMASoftwareFrontend {
  pending_tasks
  mapped_buffers
  submit_queue
  completion_handler_budget
}
```

只关心硬件峰值时，可以把 software front-end 折叠成固定 submit rate；只要关心 steady-state、interrupt 开销或 bring-up 问题，就必须把它显式放进模型。
