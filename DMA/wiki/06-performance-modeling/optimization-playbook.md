# 优化与调参手册

上级：[06 性能建模与调优](./README.md)

相关：[指标、瓶颈与实验设计](./metrics-bottlenecks.md)、[Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)、[DMA 与 NoC](../05-system-integration/dma-and-noc.md)

## 这页在回答什么问题

当 DMA 表现不佳时，应该优先调哪些旋钮，按什么顺序调；以及如何避免“所有参数都试一遍”这种低效做法。

## 调优前先分清是哪一类坏

DMA 的“性能不好”至少可能是四类完全不同的问题：

- 吞吐上不去
- 尾延迟太差
- overlap 不成立
- 偶发错或偶发抖动

这四类问题常常共享表象，但最优调参方向完全不同。吞吐问题更可能落在粒度、burst、outstanding；尾延迟问题更可能落在 return path、priority、completion backlog；overlap 问题更可能落在 tile/buffer 状态机；偶发错则先别调优，先回去看同步与可见性定义。

## 再分清你面对的是哪类 DMA

即使问题标签一样，不同 DMA 对应的有效旋钮也不同。至少可以先分三类：

- `queue-based / host-managed DMA`
- `device DMA to host memory`
- `pipeline-coupled local DMA`

前两类更常受 queue depth、mapping、interrupt moderation、host software 路径影响；第三类更常受 local SRAM、double buffering、NoC traffic pattern 和 consumer-ready 条件影响。调参前如果没有先做这个分类，很容易扫了很多与问题无关的参数。

## 最值得优先调的几类旋钮

第一类是粒度旋钮：transfer size、tile size、burst size。它们最常决定 header 开销、row locality、buffer 占用和 overlap 成立条件。

第二类是并发旋钮：outstanding limit、queue depth、channel 数、预取深度。它们决定 latency hiding 能否成立，也决定热点和尾延迟会不会被放大。

第三类是调度旋钮：priority、QoS、rate limit、credit/token throttle。它们更适合解决多流公平性和 completion 尾延迟问题，不适合拿来弥补明显的粒度或资源错配。

第四类是完成路径旋钮：interrupt vs polling、moderation、completion batch size。这类旋钮常常决定软件可见尾延迟，而不是纯数据路径带宽。

## 一个更稳的调参顺序

1. 先确认功能正确性和完成语义，没有这个前提一切调优结论都不可信。
2. 再扫粒度：先让任务大小和 tile 进入合理区间。
3. 再扫并发：让 queue/outstanding 到达 latency hiding 拐点，但不要盲目拉满。
4. 再看系统冲突：NoC return path、DDR/HBM row locality、SRAM port。
5. 最后才碰复杂 QoS、priority 和 moderation 策略。

这个顺序的好处是，你先解决低维、大收益问题，再解决高维、细调问题。反过来做通常只会把噪声放大。

## 为什么“把所有值都往大拧”经常适得其反

DMA 调优里一个很常见的错觉是：burst 更大、queue 更深、outstanding 更多，总该更快吧。实际系统里这经常会把问题从一处搬到另一处。burst 过大可能压住控制流，queue 过深可能放大 completion backlog，outstanding 过多可能在 NoC return path 或 MC 处形成周期性堆积。

所以 DMA 旋钮大多不是“越大越强”，而是“过了某个点以后收益递减甚至反噬”。调优的目标不是把单项指标做极限，而是让 `吞吐、尾延迟、稳定性、可诊断性` 同时过关。

## 常见误解

常见误解：`调优就是多扫几个参数`。实际上没有先做问题分类和指标拆分，扫参只会制造更多噪声。

常见误解：`queue/outstanding 越大越安全`。实际上它们常常会把局部排队和 completion 尾延迟一起放大。

常见误解：`QoS 是最后的锦上添花`。实际上在多流系统里，QoS 有时是避免关键小流量被 bulk DMA 压死的必要条件。

## 一句话理解

DMA 调优不是把所有旋钮都往大拧，而是先找出主导瓶颈，再让 `粒度、并发、调度、完成路径` 在同一个工作点上平衡。

## 建模启示

这一页适合把可调旋钮显式参数化。event-driven 仿真中，至少应把 `burst_len`、`queue_depth`、`max_outstanding`、`priority_mode`、`completion_mode` 暴露成模型输入。

例如：

```text
DMATuningKnobs {
  burst_len
  queue_depth
  max_outstanding
  priority_mode
  completion_mode
  tile_bytes
}
```

在 `06-performance-modeling` 与 `07-workloads-case-studies` 里，这类参数最适合映射到 `Capability` 配置。若模型不能直接扫这些旋钮，就很难把它真正用在架构调优上。
