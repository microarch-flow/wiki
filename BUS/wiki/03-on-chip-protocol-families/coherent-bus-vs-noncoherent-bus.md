# Coherent Bus vs Non-Coherent Bus

上级：[03 片上总线协议族](./README.md)

相关：[DMA 与 NoC](../../../DMA/wiki/05-system-integration/dma-and-noc.md)、[缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)

## 这页在回答什么问题

什么时候总线只负责事务搬运，什么时候还要承担 cache coherence 相关语义。

## Non-Coherent Interconnect 更常见

它更核心的特征是：

- 负责事务搬运和基本返回语义
- 不额外提供 cache coherence 语义

它不天然保证：

- CPU cache 和 DMA 看到的数据一致
- 多个缓存副本自动失效

这时需要软件、cache maintenance、barrier 或额外硬件配合。

## Coherent Interconnect 增加了什么

它会额外处理：

- snoop
- cache line 状态协同
- 一致性请求与数据请求的协调

收益是软件模型更自然，代价是：

- 协议更复杂
- 互连与缓存耦合更深
- 时序和验证成本更高

## 一个重要边界

很多系统里真正 coherent 的是 CPU cluster 附近的互连。  
而普通 peripheral、低速寄存器路径仍然走 non-coherent interconnect。

## 一句话理解

non-coherent interconnect 负责把事务送到位，coherent interconnect 还要负责让多个缓存视图保持一致。
