# Modeling Layers Analytical Event Cycle

上级：[07 Evaluation Methodology](./README.md)

相关：[Metrics Latency Throughput Saturation](./metrics-latency-throughput-saturation.md)、[Simulator Construction](../08-simulator-construction/README.md)

## 这页在回答什么问题

这页回答：NoC 模型应该怎样按层升级，什么时候停在 analytical / event-level 就够，什么时候必须进入 flit-level / cycle-level。

## 不要从最复杂模型开始

最有效的方法不是一上来就追求“工业级精确”，而是从能回答当前问题的最小模型开始。

核心不是精度崇拜，而是问题-模型匹配：

- 当前问题是什么
- 这个层级能不能回答
- 升级会多解释哪些现象

## Layer 0: Analytical Upper Bound

这一层通常忽略大部分微观冲突，只保留：

- hop / distance
- bandwidth upper bound
- rough bisection reasoning

它适合回答：

- compute / memory / network 谁更可能是一阶瓶颈
- 某个 topology 是否明显不对路

不适合回答：

- QoS 是否有效
- stall 类型是什么
- endpoint backpressure 如何传播

## Layer 1: Bandwidth-Aware / Topology-Aware

这一层开始引入：

- 具体拓扑
- 端点位置
- per-link / per-port bandwidth
- 粗粒度 contention

它适合回答：

- hotspot 大概在哪
- placement 与 topology 哪个更有影响
- cluster / hierarchy 值不值得

依然不擅长回答：

- flit-level stall
- VC / credit 细节
- per-cycle arbitration 行为

## Layer 2: Event-Level / Flow-Level

这一层开始显式引入：

- flow release
- dependency
- traffic class
- request-response pairing
- phase timing

它特别适合 AI workload，因为很多关键问题首先是：

- 哪个 phase 和哪个 phase 重叠
- response 回来时有没有挡住下一步
- control / bulk 是否冲突

这类问题在进入 flit 之前，其实已经能分析出很大一部分。

## Layer 3: Flit-Level / Credit-Level

这一层开始引入：

- packet / flit
- wormhole / VC
- credit
- input buffering
- arbitration
- ejection blocking

它适合回答：

- NO_CREDIT 和 SWITCH_CONFLICT 谁主导
- tail latency 为什么变差
- QoS / VC policy 是否真的起作用

这通常是“解释现象”的关键层。

## Layer 4: Cycle-Accurate

这一层要求更严格的时间推进和内部状态一致性。

它更适合：

- 实现级验证
- 更精细的 pipeline / event ordering
- 对 simulator 自身正确性的更强约束

但不一定意味着所有架构问题都必须做到这里。

## 什么时候该升级

一个实用判断标准是：

- 如果当前层已经能稳定解释现象，就先别急着升级
- 如果关键现象只能被“猜测”，说明该加真实度

典型升级触发：

- average throughput 解释不了 workload completion
- topology-aware 解释不了 tail latency
- flow-level 解释不了 credit / ejection 问题

## 常见误区

- 认为越细的模型一定更有价值
- 认为 analytical 层只是玩具
- 认为 flit-level 一上来就必须做完所有细节

更准确的看法是：

- 价值来自回答问题，不来自状态变量数量
- analytical / event 层对快速排除错误方案非常有价值
- flit-level 应该在真正需要解释细粒度现象时再引入

## 一句话理解

好的建模层次不是从简到繁的仪式，而是“每加一层真实度，都明确多回答了什么问题”。

## 建模启示

每一层模型都建议显式记录：

- supported questions
- supported metrics
- unsupported phenomena
- simplification assumptions

这样后续比较不同结果时，才不会把不同层级模型的结论混成一个口径。
