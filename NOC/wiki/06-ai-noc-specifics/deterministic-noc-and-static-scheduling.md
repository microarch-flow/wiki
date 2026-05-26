# Deterministic NOC And Static Scheduling

上级：[06 AI NOC Specifics](./README.md)

相关：[Source Routing For Deterministic Systems](../04-routing-and-flow-control/source-routing-for-deterministic-systems.md)、[Compiler NOC Co-Design](./compiler-noc-co-design.md)

## 这页在回答什么问题

这页回答：为什么很多 NPU 设计会主动追求 deterministic NoC 与 static scheduling 的组合，以及这套组合究竟在换什么。

## 为什么它有吸引力

如果工作负载具有：

- 较稳定的 producer-consumer 图
- 可控 placement
- 明显阶段边界

那么系统就有机会把很多通信决策前移：

- 哪些流什么时候发
- 走哪条路
- 走哪个 class / VC / network
- 哪些 flow 需要双缓冲或预留窗口

这样换来的好处通常是：

- 更容易预测延迟
- 更容易推导不会互相踩爆
- 更容易 debug 和复现

## 它换走了什么

代价也同样真实：

- 对 workload 变化更敏感
- 对 compiler 和 runtime 要求更高
- 对意外热点、稀疏动态行为和故障绕行更不灵活

因此 static scheduling 不是通用答案，而是对“稳定性优先于最大灵活性”的一种偏好。

## 为什么这和 AI 很匹配

很多 AI 计算天生就有：

- 可重复的阶段结构
- 大块、规则的数据搬运
- 相对稳定的邻接依赖

这使 static scheduling 往往比在每跳 router 做很多临时决策更划算。

## 但不是所有 AI workload 都适合

更偏动态的场景，例如：

- MoE
- 不规则 sparse routing
- 某些运行时才显现的 imbalance

会显著削弱完全静态方案的收益。

因此更现实的工程姿态通常是：

- 主流量静态
- 边缘流量保留一定动态性
- 必要时准备 escape path 或保底网络

## static scheduling 真正依赖什么

这套方法要成立，前提不只是“编译器很强”，还包括：

- 地址映射清晰
- tile / memory hierarchy 已知
- route plan 可表达
- completion / dependency 边界可观察

少了这些，所谓 deterministic 往往只是“写死很多参数”，不是可验证的 deterministic。

## 一句话理解

deterministic NoC + static scheduling 的本质，是用更强的前期规划换取更稳的运行时行为。

## 建模启示

模型里应显式支持：

- time-phased injection
- fixed route or route_id
- class / network assignment
- preplanned overlap

然后拿它和更动态方案比较：

- latency variance
- hotspot repeatability
- workload completion stability

这比只比平均吞吐更能看出 deterministic 方案的价值。
