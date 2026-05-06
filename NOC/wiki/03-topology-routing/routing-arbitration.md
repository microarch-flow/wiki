# Routing 与 Arbitration

上级：[Topology 与 Routing](./README.md)

相关：[VC / Deadlock](../02-router-microarchitecture/virtual-channel-deadlock.md)

## Routing 决定 packet 走哪条路

架构探索里，routing 的价值不只是把包送到终点，而是决定：

- 哪些链路成为热点
- 延迟分布是否可预测
- 是否容易验证
- 是否容易和编译器配合

## 三类你必须掌握的 routing

### Deterministic routing

例如 XY、YX、dimension-order。

优点：

- 简单
- 可预测
- 易验证

缺点：

- 遇到热点时缺乏绕行能力

### Source routing

路径由编译器或 runtime 预先决定，header 携带路由信息。

它对 AI tile dataflow 很重要，因为：

- 流量往往更规整
- 编译器更容易提前规划通路
- router 本地逻辑可以更轻

### Adaptive routing

根据拥塞情况动态选路。

优点：

- 某些不规则 traffic 下更灵活

代价：

- 验证更复杂
- 乱序与死锁处理更难
- 不一定适合高度编排的数据流主路径

## Arbitration 决定谁先过

即使 routing 已经确定，多个输入争同一输出时仍需要仲裁。

常见策略：

- round-robin
- fixed priority
- age-based
- QoS-aware arbitration

## 为什么必须区分 stall 类型

一个 packet 没过，并不都叫“拥塞”。

至少要区分：

- credit stall：下游没空位
- switch stall：仲裁没赢
- routing restriction：路径本身受限

不同 stall 类型对应完全不同的优化手段。

## AI NoC 的实用建议

- 主数据流优先保持简单、可预测、可静态规划
- control / sync 不要与 bulk data 共用同一低优先级路径
- 动态流量场景再评估 adaptive routing 的价值

## 本页结论

routing 决定全局路径分布，arbitration 决定局部竞争结果。  
做 NoC 架构探索时，如果你只改 link width 却不分析 routing 与仲裁，通常只能看到表面现象。
