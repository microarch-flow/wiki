# 02 基础对象与传输语义

这一部分回答 DMA 最容易被说得“像懂了又没真懂”的几件事：DMA 到底在搬什么，descriptor 和 burst 分别站在哪一层语义上，为什么 cache coherence、IOMMU 和 completion 可见性会把看似简单的搬运问题变成系统问题。

## 推荐阅读顺序

1. [传输对象与基本语义](./transfer-basics.md)
2. [地址、描述符与 Burst](./address-descriptor-burst.md)
3. [缓存一致性、IOMMU 与地址空间](./consistency-cache-coherency.md)
4. [Non-Coherent vs Coherent DMA](./noncoherent-vs-coherent-dma.md)

## 本章输出物

- 一套统一口径：logical transfer、descriptor、transaction、completion 各指什么
- 一条关键边界：数据搬完不等于软件可安全消费
- 一个系统判断：DMA 从来不只是在地址之间复制字节，它还服从一致性、翻译与隔离语义
