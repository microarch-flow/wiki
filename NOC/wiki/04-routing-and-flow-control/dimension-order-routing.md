# Dimension-Order Routing

上级：[04 Routing And Flow Control](./README.md)

相关：[Mesh And Torus](../03-topology/mesh-and-torus.md)、[Routing Algorithm Classes](./routing-algorithm-classes.md)、[Deadlock Avoidance Turn Model](./deadlock-avoidance-turn-model.md)

## 这页在回答什么问题

这页回答：为什么 `dimension-order routing` 会成为 mesh NoC 的默认基线，它到底牺牲了什么，又为什么这种牺牲经常是值得的。

## 定义

`dimension-order routing` 的核心规则是：packet 必须按照固定维度顺序依次走完路径，不能在维度之间来回切换。

在 2D mesh 里最常见的是：

- `XY routing`：先走 `X`，再走 `Y`
- `YX routing`：先走 `Y`，再走 `X`

这两者的共同点是：

- 都只走最短路径
- 对同一 `src-dst` 对，路径唯一
- 都通过限制资源获取顺序来避免某类 deadlock

## 一个最小例子

从 `(0,0)` 到 `(3,2)`：

```text
XY: (0,0) -> (1,0) -> (2,0) -> (3,0) -> (3,1) -> (3,2)
YX: (0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2) -> (3,2)
```

两条路径 hop 数相同，差异不在最短性，而在于中间占用的链路不同。这已经足够改变热点分布。

## 为什么它常被当作 baseline

原因不是它“理论最优”，而是它在几个目标上非常稳：

- router 本地逻辑简单
- 路径完全可预测
- 容易做静态链路负载分析
- 容易推导死锁自由性
- 对验证、trace、性能归因都很友好

对 deterministic NPU，主流量的 producer-consumer 关系通常已知。此时最常见的问题不是“完全不知道包会怎么跑”，而是“已知会跑哪里，能否保证它一直稳定地跑”。XY 这类规则正好提供这种稳定性。

## 为什么它能避免一类 routing deadlock

理解关键在“资源获取顺序”。

在 XY routing 中，packet 只能先占用 `X` 方向相关资源，再占用 `Y` 方向相关资源，不能从 `Y` 再回到 `X`。这等价于给通道资源加了一种偏序关系：

```text
all X-channel dependencies < all Y-channel dependencies
```

如果每个 packet 都只能沿着这个顺序申请资源，就不能形成“拿了高序资源又回头等低序资源”的环。因此一大类 channel dependency cycle 被消掉了。

这里要非常小心边界：

- 它避免的是由路径方向顺序导致的 routing deadlock
- 它不自动避免 request/response/control 之间的 protocol deadlock
- 它也不自动避免注入口、弹出口、终端 buffer 带来的系统级卡死

## 它真正牺牲了什么

最大代价是 path diversity 被人为压缩。

以 mesh 为例，从左上到右下通常有多条等长最短路径。XY 只选其中一条，结果是：

- 某些链路长期偏热
- 某些局部热点无法绕开
- 同方向流量更容易在固定区域叠加

如果 mapping 不好，这种固定性会把问题放大。换句话说，XY 不会制造热点，但会把已有的空间映射问题清楚地暴露出来。

## 为什么很多系统仍然接受这个代价

因为在很多 AI 芯片里，热点的根因不是“router 当场决策太死”，而是：

- tensor placement 本身把大量流量压到同一条通路
- memory bank / SRAM cluster / HBM port 的位置不均衡
- reduce、broadcast、gather 的模式天然集中

此时把 routing 从 XY 换成更灵活的算法，未必能根治问题。反过来，先靠更好的 placement、traffic class 分离、多网络隔离和 topology 选型，往往更有效。

## XY 和 YX 不是随便挑一个

两者都简单，但它们会把压力推到不同维度上。

如果 floorplan 表现为：

- 横向链路短、纵向链路长
- 或横向更容易布线、纵向更容易成为时序瓶颈

那么优先走哪个维度就不只是逻辑问题，还会影响：

- 平均链路能耗
- 关键路径上的拥塞
- 哪些物理通道更容易成为热点

因此 `XY 还是 YX` 应该结合 floorplan 和 traffic map 决定，而不是把 XY 当成唯一标准答案。

## 和 source routing 的边界

很多静态 NPU 会出现一个中间态：

- 整体仍然遵守 dimension-order 或某种受限路径规则
- 但具体某个 flow 是 XY、YX，或走哪条 segment，由编译器决定

这其实是一种“受约束的 source routing”。它保留了：

- 静态规划能力
- 易验证的路径空间

同时避免完全开放的 per-hop adaptive 复杂度。

## 什么时候应该考虑跳出纯 DOR

当下面几件事同时出现时，纯 XY 可能开始不够：

- topology 提供了明显多路径
- 流量模式动态且难以静态规划
- 固定热点已经成为主要瓶颈
- 系统能接受更复杂的验证和 QoS 处理

这时才值得认真考虑 turn-model adaptive 或 escape-VC adaptive，而不是一上来就把复杂性堆到 router 上。

## 常见误区

- 认为 XY routing 等于“老旧保守”
- 认为 hop 数相同就说明 XY 和 YX 没区别
- 认为 DOR 保证了整个系统不会 deadlock

更准确的说法是：

- DOR 是用路径空间换验证和稳定性
- XY 和 YX 会改变链路热分布
- DOR 只解决路径依赖的一部分问题，message class 和 endpoint 依赖仍要单独设计

## 一句话理解

dimension-order routing 的价值不在“更聪明”，而在“把路径选择压缩成一个容易验证、容易分析、容易建模的固定空间”。

## 建模启示

建模 DOR 时，可以把每个 `src-dst` 对直接映射成唯一路径，然后重点统计：

- 每条链路承载了多少流
- 哪些 router 的输入/输出冲突最频繁
- 哪些方向上的 credit stall 和 switch stall 聚集

如果要比较 `XY` 和 `YX`，不要只比平均 hop 数，而要比：

- per-link utilization
- hotspot concentration
- 99th percentile latency
- 与 floorplan 的物理方向耦合

这才是 DOR 在工程上真正决定的东西。
