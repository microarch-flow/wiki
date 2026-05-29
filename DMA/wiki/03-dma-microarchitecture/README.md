# 03 DMA 引擎微架构

这一部分关注 DMA engine 自己是怎么被组织出来的。前两章回答的是“DMA 要做什么”，这一章回答的是“要把这些语义做成高性能硬件，需要哪些内部状态、队列和调度决策”。

## 推荐阅读顺序

1. [DMA 引擎的组成](./engine-components.md)
2. [调度、Outstanding 与回包组织](./scheduling-outstanding.md)
3. [多通道、虚拟化与隔离](./channels-virtualization.md)
4. [多维 DMA 与 Stride 地址生成](./multidimensional-stride-dma.md)

## 本章输出物

- 一张最小 DMA engine 结构图：descriptor fetch、issue、response、completion 各由谁负责
- 一条性能主线：为什么很多上限首先受 outstanding、return path 和回包组织限制
- 一组系统能力判断：channel、queue、context、stride 支持分别解决什么问题
