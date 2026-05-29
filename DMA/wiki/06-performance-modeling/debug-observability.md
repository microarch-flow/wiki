# 观测、计数器与调试路径

上级：[06 性能建模与调优](./README.md)

相关：[指标、瓶颈与实验设计](./metrics-bottlenecks.md)、[DMA IP 评估清单](../08-industry-ip/dma-ip-checklist.md)

## 这页在回答什么问题

如果系统里的 DMA “偶发慢、偶发抖、偶发错”，需要哪些观测点才能把问题定位到可行动的层次；以及为什么 observability 本身就是 DMA IP 能力的一部分。

## 没有观测点的 DMA，本质上是黑盒

DMA 的难点在于问题跨越软件、互连、memory 和 completion 路径。没有足够观测点时，系统只能看到“任务提了、好像慢了、偶尔 done 很晚”，根本不知道卡在哪一层。于是调试会退化成猜测：猜是 NoC，猜是 DDR，猜是 IOMMU，猜是中断。

所以 observability 不是“debug 方便一点”的附属项，而是 DMA 是否可被工程化使用的基本能力。没有它，bring-up 和调优成本都会急剧上升。

## 最值得有的计数器

一组真正高价值的计数器，通常至少包括：

- descriptor submitted / accepted / completed
- outstanding occupancy 直方图或高水位
- queue full / empty cycles
- read/write bytes 与 burst 分布
- response latency histogram
- completion backlog 或 completion visible delay
- error / retry / timeout count

这组计数器的价值在于，它们把“提交不够、发不出去、回不来、完成不见”四类问题拆开了。

## 最值得有的状态观测

除了累积计数器，DMA 还应该暴露一些时刻状态，否则很难做快照式定位：

- 当前通道是否阻塞
- 阻塞在 submit、issue、response、ejection 还是 completion
- 哪个 queue 或 context 正在积压
- 哪个 memory port / stream 最拥塞
- 当前最老 inflight 事务年龄是多少

这些状态对偶发抖动尤其重要。因为很多问题不是总平均慢，而是某个时刻局部爆了，没有快照状态你根本看不到。

## 一条更实用的调试路径

调 DMA 时，最稳的路径通常不是“先抓波形”，而是：

1. 先判断这是正确性问题还是纯性能问题。
2. 再判断卡在 submit、issue、network、memory、completion 的哪一段。
3. 然后才去细看单个 queue、burst、page crossing 或 interrupt。

这条路径的好处是把大问题先压缩到一个阶段，再展开局部细节。否则你很容易在大量低层事件里迷失方向。

## 不同 DMA 类型需要盯的观测点并不一样

`host-managed / queue-based DMA` 更要盯 submit、queue、completion visible 和 interrupt/polling 路径。`device DMA to host memory` 更要盯 mapping、moderation、host-visible completion。`pipeline-coupled local DMA` 更要盯 buffer ready、NoC injection、SRAM port 和 consumer stall。

也就是说，观测点不是越多越好，而是要与 DMA 类型和系统目标匹配。一个非常全面但不分层的 counter set，实战价值常常不如少量但边界清晰的阶段观测。

## 为什么 observability 本身是 IP 评估项

很多 DMA IP 文档里，功能和峰值参数写得很详细，counter 和状态暴露却很敷衍。这在实验室 demo 阶段可能还能接受，但在真正商用系统里会立刻变成维护成本。没有足够 observability，任何性能尾巴、偶发断供或 completion 丢失都会变成高代价排查。

所以评估 DMA IP 时，observability 不该被当成“debug 附件”，而应和 queue、outstanding、stride、QoS 一样被视为核心 capability。

## 常见误解

常见误解：`多打点日志就够了`。实际上 DMA 问题更需要分阶段计数器和状态快照，而不是大量文本日志。

常见误解：`只看总吞吐和总中断数就能定位问题`。实际上没有阶段性观测，submit、response、completion 三类问题会被混成一类。

常见误解：`observability 是 bring-up 阶段才有用`。实际上 tail latency、steady-state 抖动和多流公平性问题在量产阶段同样依赖它。

## 一句话理解

DMA 调试最怕“黑盒搬运器”；最有价值的不是更多日志，而是能把阻塞阶段、并发状态和完成路径直接暴露出来的观测点。

## 建模启示

这页适合把模型里的内部状态同步映射成可观测 counter。event-driven 仿真中，建议让每一类关键事件都能投影成 counter 或 histogram，而不是只在最终输出时给一个总成绩。

一个最小观测结构可以是：

```text
DMAObservability {
  counters
  histograms
  phase_state
  oldest_inflight_age
}
```

在 `06-performance-modeling` 与 `08-industry-ip` 中，这类结构很适合映射到 `Capability` 和 `Interaction` 的可诊断性层。若模型自身都没有这些状态，后面很难判断真实硬件到底缺了什么计数器。
