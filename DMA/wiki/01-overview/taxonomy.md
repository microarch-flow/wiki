# DMA 分类框架

上级：[01 概览与问题定义](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[软件栈与编程模型](../04-programming-model/software-stack.md)

## 这页在回答什么问题

DMA 不是单一对象。要避免把不同系统里的 DMA 混为一谈，需要先建立分类框架。

## 按传输路径分类

- `memory-to-memory`
- `peripheral-to-memory`
- `memory-to-peripheral`
- `peripheral-to-peripheral`
- `local-memory-to-local-memory`
- `host-to-device / device-to-host / device-to-device`

## 按控制模式分类

- `single-shot`：一次配置，一次完成
- `linked-list / scatter-gather`：由描述符链驱动多段传输
- `cyclic / ring-buffer`：适合音频、网络、视频这类流式场景
- `command-queue based`：更接近 accelerator 或高性能 I/O 引擎

## 按系统位置分类

- SoC 通用 DMA controller
- 专用外设 DMA
- GPU copy engine
- NIC / SSD device DMA
- AI accelerator tile / cluster DMA

## 按一致性与地址翻译能力分类

- non-coherent DMA
- cache-coherent DMA
- 带 IOMMU / SMMU 的 DMA
- 支持虚拟地址工作流的 DMA

## 按性能组织方式分类

- 单通道 vs 多通道
- 单队列 vs 多队列
- 固定优先级 vs 可编程 QoS
- 小窗口低复杂度 vs 大窗口高并发

## 一个实用分类视角

从工程上看，最有用的不是背术语，而是先问五个问题：

1. 数据在谁和谁之间搬
2. 谁来描述任务
3. 地址是否需要翻译或保护
4. 回包和完成语义如何定义
5. 该 DMA 最终受谁限制：端口、NoC、memory、cache 还是软件

## 一句话理解

DMA 的分类核心，不是名字，而是 `传输路径 + 控制模式 + 系统一致性语义 + 并发组织方式` 的组合。
