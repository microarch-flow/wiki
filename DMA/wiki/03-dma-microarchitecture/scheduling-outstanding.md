# 调度、Outstanding 与回包组织

上级：[03 DMA 引擎微架构](./README.md)

相关：[DMA 与 NoC](../05-system-integration/dma-and-noc.md)、[指标、瓶颈与实验设计](../06-performance-modeling/metrics-bottlenecks.md)、[NOC：DMA Engine / Request-Response Scheduling](../../NOC/wiki/04-ai-dataflow-system/dma-engine-request-response-scheduling.md)

## 这页在回答什么问题

为什么很多 DMA 的上限不是由理论带宽决定，而是由请求节奏、outstanding 窗口和回包组织方式决定。

## Outstanding Window 是最关键的调度旋钮之一

这里先约定几个词：

- `outstanding`：已经发出、但还没闭环完成的 in-flight 事务
- `request injection`：DMA 把请求持续送进互连/内存系统的节奏
- `forward progress`：系统虽然可能很慢，但仍持续有事务在真正完成

另外，本页里的 `writeback` 更偏 DMA 写回/完成写回语义，不是默认在说 CPU cache writeback；`refill` 只有在明确讨论 cache 或片上 buffer 补数时才按那个语境理解。

窗口太小：

- 无法隐藏 memory latency
- overlap 不足
- 带宽打不满

窗口太大：

- 回包集中
- endpoint 更容易拥塞
- 系统更容易出现周期性波峰

## Request 和 Response 必须一起看

很多分析只看 request injection，这是不够的。  
真正决定 forward progress 的往往是：

- response 是否回得来
- writeback 是否挤压 refill
- completion 是否因为目的端拥塞而拖延

## 调度器至少要决定三件事

- 先发谁
- 发多猛
- 什么时候收敛

典型机制包括：

- round-robin
- fixed priority
- age-based
- credit / token throttle

## 回包组织为什么经常被低估

如果系统允许乱序返回，就需要考虑：

- completion table
- data reassembly
- partial completion
- head-of-line blocking

## 一个实用判断

如果系统表现出“平均带宽不低，但尾延迟很差、热点周期性出现”，优先怀疑 DMA 调度和回包组织，而不是先怀疑链路规格。

## 一句话理解

DMA 的性能不是把请求尽量发满，而是把请求和回包组织成能持续维持系统前进的并发形状。
