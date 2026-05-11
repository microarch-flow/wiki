# AXI 属性、Cacheability 与 Barrier

上级：[04 微架构与系统集成](./README.md)

相关：[MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)、[缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)

## 这页在回答什么问题

为什么 AXI 上的访问属性、cacheability、shareability 和 barrier 不只是协议附加位，而是决定软件和硬件是否能正确协同的关键语义。

## AXI 属性在传什么

一笔访问除了地址和数据，通常还带着“该怎么被系统对待”的属性，例如：

- 是否可缓存
- 是否可缓冲
- 是否是普通 memory 还是 device/MMIO
- 是否需要更强顺序约束

这些属性会影响：

- cache 行为
- reorder 空间
- bridge / interconnect 的处理方式

## Cacheability 为什么影响 DMA

如果 descriptor、data buffer、completion buffer 的属性没设对，就会出现：

- 软件写了，但 DMA 看不到
- DMA 写回了，但 CPU 先看到旧缓存
- MMIO 被错误当成普通内存对待

所以 AXI 属性和软件内存属性必须匹配。

## Barrier 在解决什么

barrier 的价值不是“让系统变慢”，而是明确告诉互连和 CPU：

- 前面的访问必须先完成到某种可见状态
- 后面的访问不能越过这个点

在 DMA 提交链路里，典型用途是：

- 先保证 descriptor 可见
- 再写 doorbell

这里最容易误解的一点是：  
`barrier` 约束的是顺序，不会凭空把脏 cache line 变成 DMA 可见。对 non-coherent DMA 来说，真正建立可见性通常还需要 coherent fabric 或显式 clean/invalidate；barrier 是在此基础上保证“先让 descriptor 真可见，再让 doorbell 发生”。

## 继续阅读

- 如果你在追 `descriptor、data、writeback 三段为什么语义不同`：看 [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)
- 如果你在追 `MMIO 和普通内存的软件模型差别`：看 [MMIO、Cache 与 Interrupt 视角](./mmio-cache-interrupt-view.md)
- 如果你在追 `doorbell 前后为什么要小心顺序`：看 [Doorbell、Completion 与 Interrupt Flow](./doorbell-completion-interrupt-flow.md)
- 如果你在追 `coherent / non-coherent DMA 的系统前提`：看 [缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)

## 最常见的误区

- “coherent 系统就不需要 barrier”
- “cacheability 只影响性能，不影响正确性”
- “MMIO 访问天然保序，不需要额外考虑”

## 一句话理解

AXI 属性定义系统如何理解这笔访问，barrier 定义这些访问之间不能被怎样重排；两者共同决定 DMA 和软件契约能否成立。
