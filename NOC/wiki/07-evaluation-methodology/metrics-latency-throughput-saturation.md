# Metrics Latency Throughput Saturation

上级：[07 Evaluation Methodology](./README.md)

相关：[Stall Taxonomy And Attribution](./stall-taxonomy-and-attribution.md)、[Modeling Layers Analytical Event Cycle](./modeling-layers-analytical-event-cycle.md)

## 这页在回答什么问题

这页回答：NoC 评估里最基础的指标应该怎样分层理解，为什么 `latency / throughput / saturation` 不能只用一个平均数字来讲完。

## 指标不是越多越好

NoC 评估真正需要的是一组能形成因果链的指标，而不是一堆孤立数字。

最核心的链条通常是：

```text
injection / offered load
-> contention / occupancy / stall
-> latency distribution
-> throughput / completion
-> workload-level outcome
```

如果这个链条断了，指标就会变成“看起来很多，但解释不了问题”。

## latency 要看分布，不只看平均

平均 latency 的问题在于，它会掩盖：

- 少量极慢 packet
- 某一类关键流量被严重拖慢
- 某些 router / endpoint 上的局部长尾

对 AI NoC，至少要区分：

- average latency
- median latency
- tail latency，例如 P95 / P99
- per-class latency

因为很多系统真正怕的是：

- response tail 太长
- control / barrier 偶尔被淹没

而不是所有流量平均都慢一点。

## throughput 也分层

`throughput` 这个词很容易被混用。至少应区分：

- network throughput：单位时间送达多少 flit / packet / byte
- endpoint throughput：tile / DMA / HBM 实际吃下多少数据
- workload throughput：tokens/s、samples/s、job completion rate

如果只看 network throughput，很容易高估系统价值，因为网络忙并不等于 workload 前进得快。

## saturation point 是结构性拐点

`saturation` 的价值不在“这个数是多少”，而在它标记了一件事：

- offered load 再增加，系统不再线性响应
- latency 开始急剧上升
- queue / stall 开始持续积累

因此 saturation 应和下面这些一起看：

- 哪类流量先饱和
- 哪些链路 / 端点先成为热区
- 饱和后 workload 指标如何变化

## utilization 只是症状，不是结论

per-link / per-router utilization 很重要，但它只能告诉你：

- 哪些地方忙

不能单独告诉你：

- 为什么忙
- 忙是不是合理
- 忙是否真的伤害了 workload

所以 utilization 必须和：

- latency
- stall breakdown
- endpoint consumption

一起读。

## AI NoC 里特别重要的系统级指标

除了网络原生指标，还要关注：

- tile utilization
- producer stall ratio
- completion time
- token latency
- DMA overlap success
- barrier / sync amplification

这些指标的意义在于：它们直接回答“NoC 问题有没有真的伤到计算和工作负载”。

## metric 必须和模型层级绑定

不是每层模型都能产出同一套指标。

例如：

- analytical model 适合给粗粒度 throughput / hop / bisection proxy
- event-level model 适合给 flow-level latency 与 phase overlap
- flit-level / cycle model 才适合给 credit stall、switch conflict、per-router occupancy

如果把这些不加区分地并排比较，结论会很危险。

## 常见误区

- 只看 average latency
- 把 network throughput 当成 workload throughput
- 看到高 utilization 就认为设计高效
- 不区分 per-class 指标

更准确的做法是：

- 延迟看分布
- 吞吐看层级
- 饱和看拐点
- 指标看 class 与 workload 关联

## 一句话理解

latency、throughput、saturation 不是三个独立数字，而是同一条系统因果链上的三个观察面。

## 建模启示

评估表格至少应固定几列：

- modeling layer
- metric name
- metric scope：network / endpoint / workload
- aggregation：avg / median / P99 / per-class
- interpretation

这样后面的实验结果才不会因为指标口径漂移而无法横向对比。
