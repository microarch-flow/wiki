# Workload MOE Routing

上级：[06 AI NOC Specifics](./README.md)

相关：[Routing Algorithm Classes](../04-routing-and-flow-control/routing-algorithm-classes.md)、[Adaptive Routing Tradeoffs](../04-routing-and-flow-control/adaptive-routing-tradeoffs.md)

## 这页在回答什么问题

这页回答：为什么 MoE 是 AI NoC 中最容易把 routing、fairness 和 dynamic hotspot 问题逼出来的 workload 之一。

## MoE 最狠的地方不在总量

MoE 典型特征是：

- dispatch / gather 类 all-to-all-like 模式
- 热门 expert 可能高度偏斜
- 目的地选择更依赖输入

因此它的压力主要来自：

- 动态热点
- 空间不均匀
- gather / response 与下一轮 dispatch 的交叠

而不只是总字节数大。

## 从 gating 到网络流量

MoE gating 根据 token 选择 top-k expert；这是模型层目的地选择，不是 NoC 的逐跳 routing。假设 100 个 token、hidden=1024、FP16=2 B、top-k=2，且每个选择都接受、不压缩，dispatch 逻辑 payload 为 `100×1024×2×2 = 409,600 B`；若两个 expert 各返回同尺寸结果，combine 回传同量。实际容量限制可能丢弃、重路由或排队 token；本地 expert 的数据不一定经过 NoC。expert 放置和 gating 偏斜决定流向。

若某 expert 集中收到大量 token，其计算队列满会反压接收端；改变网络路径不能突破该 expert 的计算能力。网络链路竞争则表现为中途 queue/credit/SA stall。trace 应分别记录每 token 的 expert 选择、发送/到达、expert 入队和完成、回传及各段等待，才能区分两种热点。

## 为什么它会挑战 deterministic 方案

如果热点位置和 expert 负载分布会明显变化，那么纯静态 route plan 的优势会下降，因为：

- 同一套静态路径可能反复把流量压到热门 expert 周围
- 预先均衡的假设可能失效

这使 MoE 成为评估“有限 adaptive 是否值得”的高价值 workload。

## 但它不等于 fully adaptive 就一定赢

MoE 的确更适合用来测试 adaptive routing，但收益仍然取决于：

- topology 是否有真实多路径
- 热点是否真的可以被绕开
- fairness / starvation 机制是否足够

如果这些条件不满足，adaptive 可能只是把路径变得更难解释。

## QoS 和 traffic isolation 同样重要

MoE 不是纯 routing 问题，因为 dispatch / gather 很容易和：

- memory response
- control / barrier
- background traffic

互相干扰。

因此一个更现实的问题常常是：

- MoE 流是否需要独立 class 或独立 plane
- 是否需要对关键小消息做明确保护

## 一句话理解

MoE 的价值在于：它会把平时在规则 workload 下被掩盖的动态热点、fairness 和 path-diversity 问题逼出来。

## 建模启示

MoE 模型至少要显式参数化：

- expert load skew
- dispatch / gather overlap
- routing family
- fairness / aging
- class isolation strategy

评估时不要只看平均吞吐，至少还要看：

- max hotspot concentration
- tail latency
- starvation event
- workload completion stability

这样才能看出一套 NoC 方案在动态场景下是否真的站得住。
