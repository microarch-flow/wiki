# 同步、一致性与常见错误

上级：[04 软件栈与编程模型](./README.md)

相关：[缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)、[指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)

## 这页在回答什么问题

为什么 DMA 问题里最难定位的一类，不是“搬不动”，而是“偶发错、偶发慢、偶发脏数据”。

## 最常见的四类错误

- cache flush / invalidate 时机错误
- buffer ownership 交接不清
- completion 被过早消费
- queue / descriptor 复用过快

## 软件上最容易忽略的时序

- descriptor 写完后是否需要 memory barrier
- doorbell 触发前数据是否真正可见
- completion 到来时 CPU cache 是否还是旧数据
- consumer 是否在 producer 真正完成前抢跑

## 一个典型错法

软件看见“DMA done”就立刻读 buffer，结果读到旧数据。  
根因可能是：

- 当前所谓 `done` 其实只表示 descriptor 已被接收
- 或数据已写到内存但还没对 CPU 正确可见
- 或软件虽然收到了 completion 事件，但 cache / ownership 还没完成切换

更稳妥的区分方式是：

- `提交完成 / descriptor consumed`
- `DMA 写回完成到 memory-visible 点`
- `软件 completion event delivered`

真正安全读 buffer 或复用 buffer 前，driver/runtime 应该等到自己语义里要求的那个阶段，而不是看到任意一个 “done” 就继续。

## 排查顺序建议

1. 先看语义定义是否一致
2. 再看 barrier / cache 维护
3. 再看 descriptor 生命周期
4. 最后才怀疑随机硬件故障

## 一句话理解

很多 DMA bug 本质不是带宽问题，而是“完成语义、一致性语义和软件时序”没有对齐。
