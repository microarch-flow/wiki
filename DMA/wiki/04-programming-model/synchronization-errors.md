# 同步、一致性与常见错误

上级：[04 软件栈与编程模型](./README.md)

相关：[缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)、[队列、Doorbell 与 Completion](./queues-doorbells-completions.md)、[指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)

## 这页在回答什么问题

为什么 DMA 问题里最难定位的一类，不是“搬不动”，而是“偶发错、偶发慢、偶发脏数据”；以及这些问题通常是哪些时序边界没有对齐。

## DMA 最难的 bug 通常不是数据路径坏了，而是边界没对齐

如果 DMA 完全不工作，bring-up 往往反而容易，因为问题会快速暴露成地址错、时钟没开、寄存器没配或中断没连上。真正麻烦的是那类“多数时候能跑，偶尔错一次”的问题。这类 bug 最典型的特征是：

- 数据大多数时候正确，偶尔读到旧值
- 性能大多数时候正常，偶尔 completion 极晚
- queue 平时可用，压力一上来就乱

这种问题的根因往往不是物理搬运坏了，而是“谁在什么时候拥有 buffer，谁在什么时候看到数据，谁在什么时候认为任务已经结束”这三件事没有统一。

## 最常见的四类错误

第一类是 descriptor 或 payload 还没真正对 DMA 可见，软件就提前敲了 doorbell。DMA 此时可能看到半写好的 queue entry，或者看到地址对了但内容还是旧数据。

第二类是 completion 被过早消费。软件看到某个 done 位或 completion record 就立刻复用 buffer，但这时 cache 可见性、ownership 切换或下游消费可能还没完成。

第三类是 queue / descriptor 复用过快。producer 觉得硬件“应该差不多读走了”，就把槽位覆盖；而 DMA 可能还在 fetch、还在处理、或者 completion 路径尚未真正释放该 slot。

第四类是 cache 维护时机错误。特别是 non-coherent DMA，clean / invalidate 做早了或做晚了，都会让 CPU 和 DMA 看到不同版本的数据。

## 先问清楚“done”到底是哪种 done

这一点必须反复强调。DMA 路径里至少可能同时存在这些“完成”：

- `descriptor consumed`
- `data transfer complete`
- `memory visible`
- `software completion event delivered`

它们不一定相同，也不一定按你想象的间隔出现。很多 bug 的本质就是软件把前一个阶段误当成后一个阶段。例如 polling 命中的是 descriptor 已消费，但软件把它当成 buffer 可复用；或者 interrupt 先到了，但 completion record 还没对 CPU 可见。

## 一个最典型的错法

软件写完 descriptor，立刻敲 doorbell；DMA 很快接单并返回 done；软件收到 done 后立刻读 buffer。这个流程在纸面上很顺，但中间至少有三处可能错：

- descriptor 写入顺序未被 barrier 固化，DMA 读到半成品
- DMA 写回的数据对 CPU cache 还不可见
- 当前所谓 done 只代表 descriptor 被接收，而不是数据已经安全消费

所以 DMA 同步问题不能只画一条“CPU -> DMA -> CPU”的箭头，必须把 memory visibility、ownership 和 completion source 一起标出来。

## 排查顺序为什么很重要

这类问题一上来就抓波形，通常效率不高。更合理的顺序是：

1. 先确认文档中的完成语义定义是否一致。
2. 再确认 barrier、flush/invalidate、doorbell 顺序是否匹配。
3. 再确认 queue/descriptor 生命周期是否有过早复用。
4. 最后才去怀疑随机硬件故障或偶发协议错误。

因为大多数 DMA 偶发错误，本质上都能在前三步里找到解释。

## 常见误解

常见误解：`看到 done 就能立刻读或复用 buffer`。实际上 done 必须先被映射到具体完成阶段，不能一概而论。

常见误解：`coherent DMA 就不会有同步 bug`。实际上 coherent 只减少副本不一致问题，不会自动修复 barrier、ownership 和 completion 契约。

常见误解：`偶发慢一定是链路拥塞`。实际上 completion 可见性延迟、interrupt 路径抖动或队列复用冲突也会表现成“偶发慢”。

## 一句话理解

很多 DMA bug 本质不是带宽问题，而是 `完成语义、一致性语义和软件时序` 没有对齐。

## 建模启示

若模型里只有 `transfer_done`，这页描述的大部分问题都无法表达。至少要显式区分 `descriptor_visible`、`doorbell_seen`、`data_visible_to_cpu`、`completion_consumed` 四个事件。

一个最小同步状态机可以写成：

```text
BufferLifecycle {
  state: cpu_owned | dma_owned | done_not_visible | visible_to_cpu | reusable
}
```

如果只关心纯吞吐，可以把中间状态折叠；如果关心功能正确性、偶发错和软件 timeout，`done_not_visible` 这种中间态必须显式存在。
