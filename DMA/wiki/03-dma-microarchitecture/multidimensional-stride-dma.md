# 多维 DMA 与 Stride 地址生成

上级：[03 DMA 引擎微架构](./README.md)

相关：[地址、描述符与 Burst](../02-fundamentals/address-descriptor-burst.md)、[AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)

## 这页在回答什么问题

为什么很多高性能 DMA 不能只支持线性搬运，而必须支持 stride、2D、3D 甚至 tensor-like 地址生成。

## 什么时候线性 DMA 不够用

- 图像按行搬运
- tensor tile 带 padding
- feature map / KV cache 分块访问
- local SRAM 与外部内存布局不同

## Stride DMA 在硬件里解决什么

它把“软件循环里做地址递增”的工作下沉到 DMA engine。  
这样可以减少：

- descriptor 数量
- CPU 或 runtime 提交开销
- 小事务碎片化

## 设计时要看哪些点

- 支持几维
- 每维长度和 stride 如何表达
- 跨页/跨 bank/跨 burst 边界如何拆分
- 回包和完成是按整体还是按子块定义

## 典型风险

- 地址生成器复杂度升高
- 边界拆分逻辑更难验证
- 看似一个任务，实际被打碎成大量低效子事务

## 一句话理解

多维 DMA 的价值，不是让描述符更“花哨”，而是让数据布局不规则的系统仍能用接近连续搬运的方式高效供数。
