# 02 基础对象与传输语义

这一部分回答三个基础问题：

- DMA 到底在搬什么
- 地址、长度、描述符和 burst 分别代表什么
- 一致性与地址翻译为什么会改变 DMA 语义

## 推荐阅读顺序

1. [传输对象与基本语义](./transfer-basics.md)
2. [地址、描述符与 Burst](./address-descriptor-burst.md)
3. [缓存一致性、IOMMU 与地址空间](./consistency-cache-coherency.md)
4. [Non-Coherent vs Coherent DMA](./noncoherent-vs-coherent-dma.md)

说明：这里把 `地址、描述符与 Burst` 放在前面，是为了先把“descriptor 如何变成具体总线事务”的基本词汇立住，再进入一致性、IOMMU 和 cache 这些系统级语义。
