# 地址、描述符与 Burst

上级：[02 基础对象与传输语义](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)

## 这页在回答什么问题

为什么很多 DMA 的性能、灵活性和复杂度，最终都收敛到 descriptor、burst 和分段组织上。

## Descriptor 是 DMA 的“任务格式”

一个 descriptor 往往至少包含：

- source address
- destination address
- length
- control flags
- next pointer 或 queue index

更复杂的系统还会加：

- stride
- 2D / 3D shape
- priority
- completion token

## Scatter-Gather 为什么重要

现实系统的数据常常并不连续。  
scatter-gather 让 DMA 可以：

- 把多段离散 buffer 视作一个逻辑任务
- 避免 CPU 逐段介入
- 更好配合 IOMMU/page-based 映射

## Burst 在定义什么

burst 决定单次总线或互连占用的粒度。  
它影响：

- header 开销
- 占路时间
- 回包峰值
- 对小消息和高优先级流量的干扰

## 对齐与边界问题

常见限制包括：

- 地址对齐要求
- 4KB 或 page 边界拆分
- memory controller 的 burst 边界
- local SRAM bank 映射边界

这些边界会让“逻辑上一段传输”在硬件里变成多段子事务。

## 一句话理解

descriptor 决定 DMA 知道要做什么，burst 决定 DMA 以什么粒度做，而边界规则决定它最终能否高效地做。
