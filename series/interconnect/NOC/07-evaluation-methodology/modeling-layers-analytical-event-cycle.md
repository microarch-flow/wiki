# Modeling Layers Analytical Event Cycle

上级：[07 Evaluation Methodology](./README.md)

相关：[Metrics Latency Throughput Saturation](./metrics-latency-throughput-saturation.md)、[Simulator Construction](../08-simulator-construction/README.md)

## 这页在回答什么问题

这页回答：NoC 模型何时采用解析估算，何时在仿真中引入 flow 或 flit 状态粒度，以及何时需要逐周期精度。仿真的时间推进可以使用离散事件或逐拍 tick；时间推进、状态粒度和时间保真度是分别选择的维度。

## 不要从最复杂模型开始

最有效的方法不是一上来就追求“工业级精确”，而是从能回答当前问题的最小模型开始。

核心不是精度崇拜，而是问题-模型匹配：

- 当前问题是什么
- 这个层级能不能回答
- 升级会多解释哪些现象

## Layer 0: Analytical Estimate / Bound

这一层可用解析估算或界，通常忽略部分微观冲突。只有说明哪些约束被放松、为何所得值必然不低于真实可达吞吐时，才能称吞吐上界；未经证明的近似应称 estimate/proxy。常见输入包括：

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

## Layer 2: Flow 状态粒度

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

## Cycle-Accurate 是时间保真度，不是引擎类别

周期精确要求指定观察边界上每拍状态和规则与目标模型一致；它可用逐拍 tick，也可用按 `(time, phase, stable_id)` 排序的离散事件引擎实现。反过来，tick 推进若只用固定 flow 延迟，也不自动具有 flit/credit 精度。这是与上面状态粒度正交的一条轴。

这种精度要求更严格的事件顺序和内部状态一致性。

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
- 解析或粗 flow 粒度模型对快速筛选方案有价值
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
