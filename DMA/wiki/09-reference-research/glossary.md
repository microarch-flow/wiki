# 术语表

上级：[09 参考资料与研究模板](./README.md)

相关：[传输对象与基本语义](../02-fundamentals/transfer-basics.md)、[队列、Doorbell 与 Completion](../04-programming-model/queues-doorbells-completions.md)

## 这页在回答什么问题

当前这套 wiki 里，哪些 DMA 术语需要统一口径；以及为什么很多术语如果不先限定上下文，就会在不同系统里被错误混用。

## 核心术语

- `DMA`：系统级数据移动执行层，不等于单个硬件块
- `DMA engine`：执行具体数据搬运、事务调度和完成跟踪的硬件单元
- `DMA controller`：更偏控制、编排、多通道管理和接口暴露的 DMA 硬件单元
- `DMA IP`：可作为产品/IP 集成和评估对象的一类 DMA 实现
- `descriptor`：描述一次或一组 DMA 任务的数据结构，属于任务描述层
- `logical transfer`：软件眼里的一笔搬运任务，不等于单笔总线事务
- `transaction`：真正落到 AXI/PCIe/NoC 上的 read/write/burst/TLP
- `scatter-gather`：把多个离散段组织成一条逻辑传输任务的方式
- `burst`：总线或互连上的连续事务粒度
- `outstanding`：已发出但尚未完成闭环的 in-flight 事务数量
- `completion`：必须结合上下文看，可能指 descriptor consumed、data visible 或 software-visible completion event
- `doorbell`：软件通知硬件“可以去看新任务”的触发机制，不等于任务内容一定已可见
- `queue / ring`：软件或硬件用于组织任务提交的顺序容器
- `linked list descriptor`：通过 next pointer 串起多个 descriptor 的线性任务组织方式
- `cyclic / circular mode`：适合流式场景的循环提交/循环缓冲模式
- `coherent DMA`：与 CPU cache 共享更一致数据视图的 DMA 模式
- `non-coherent DMA`：需要软件显式管理 cache 可见性和 ownership 的 DMA 模式
- `IOMMU / SMMU`：为设备提供地址翻译和隔离的单元
- `completion visibility latency`：数据完成后，到软件真正能观察到 completion 的延迟
- `consumer-ready latency`：软件或下游计算真正可以继续推进的延迟
- `double buffering`：用至少两块 buffer 让搬运和消费形成可重叠节拍
- `observability`：通过计数器、状态快照、trace 或直方图观察 DMA 内部行为的能力
- `steady-state`：系统进入持续推进后，各阶段长期重复的稳定工作区间

## 最容易被混掉的三组词

第一组是 `descriptor / logical transfer / transaction`。descriptor 是任务描述层，logical transfer 是软件语义层，transaction 是协议事务层。三者不该混成“一条 DMA 命令”。

第二组是 `transfer done / completion visible / consumer ready`。数据搬完、completion 对软件可见、下游真的可以继续，往往不是同一时刻。

第三组是 `channel / queue / context / stream`。channel 偏硬件调度/隔离单元，queue 偏提交容器，context 偏地址空间或虚拟化语义，stream 偏 workload 视角的一路逻辑流量。

## 一条统一口径

本 wiki 里凡是说到 `completion`，默认都应先追问：“这里指的是哪一层完成？”  
凡是说到 `performance`，默认都应再追问：“量的是 throughput、completion visible latency，还是 consumer-ready latency？”  
凡是说到 `DMA type`，默认都应再追问：“它服务哪条路径，处在哪种系统画像里？”

## 常见误解

常见误解：`descriptor 就是一笔 burst`。实际上 descriptor 在上层，burst 在下层，中间隔着事务展开和边界拆分。

常见误解：`completion 就是 done`。实际上不先限定上下文，这个词几乎没有足够精度。

常见误解：`channel 和 queue 是一回事`。实际上它们在很多 DMA 里并不一一对应。

## 一句话理解

DMA 的术语体系，核心围绕 `任务描述、事务并发、完成语义、系统可见性` 四组概念展开，任何一个词脱离上下文都可能失真。
