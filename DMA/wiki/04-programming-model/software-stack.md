# 软件栈与编程模型

上级：[04 软件栈与编程模型](./README.md)

相关：[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[SoC 外设与 I/O DMA](../05-system-integration/soc-peripheral-io.md)

## 这页在回答什么问题

DMA 为什么既是硬件模块，也是 software contract；以及 driver、runtime、compiler 分别在负责什么。

## 最常见的软件栈分层

- 应用或 runtime 产生数据移动需求
- driver 申请/映射 buffer，填 descriptor
- OS / IOMMU 提供地址与权限管理
- DMA engine 执行传输并回报完成

这里最好补一个地址桥接：

- CPU/用户态最先看到的往往是虚拟地址
- descriptor 里真正写进去的，常常是物理地址、IOVA 或其他 device-visible 地址
- 这层地址是否有效，取决于映射、权限和 buffer 生命周期是否正确

## 编程模型的关键对象

- descriptor / command
- queue / ring
- doorbell
- completion record
- interrupt 或 polling

这套对象更典型地出现在 `queue-based DMA engine` 里。  
更简单的 peripheral DMA 也可能只有通道寄存器、状态位和传输完成中断，而不一定暴露完整 ring/queue 模型。

## 三种常见控制方式

- CPU 提交单次 DMA
- driver 维护环形队列
- runtime / compiler 批量生成搬运计划

越往后，DMA 越接近“数据移动执行引擎”。

## 软件对性能的真实影响

软件会决定：

- 任务切分粒度
- queue 深度
- 同步频率
- overlap 机会
- 是否形成可预测流量

## 一句话理解

DMA 的软件栈不是“给硬件下命令”而已，而是在定义数据移动任务如何被描述、提交、同步和消费。
