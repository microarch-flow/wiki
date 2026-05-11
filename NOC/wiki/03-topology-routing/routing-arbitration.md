# Routing 与 Arbitration

上级：[Topology 与 Routing](./README.md)

相关：[VC / Deadlock](../02-router-microarchitecture/virtual-channel-deadlock.md)

## 读这页前先统一几个词

- `routing`：决定 packet 该走哪条路径
- `arbitration`：决定多个竞争者里谁先拿到同一个资源
- `deterministic routing`：同一源和目的之间，总是走同一类固定路径
- `adaptive routing`：路径会根据实时拥塞情况变化
- `stall`：本周期本来想前进，但因为资源或约束没有前进成功

## Routing（路由）决定 packet（数据包）走哪条路

架构探索里，routing 的价值不只是把包送到终点，而是决定：

- 哪些链路成为热点
- 延迟分布是否可预测
- 是否容易验证
- 是否容易和编译器配合

## 三类你必须掌握的 routing

### Deterministic routing

例如 XY（先水平再垂直的维序路由）、YX、dimension-order（维序路由，按固定维度顺序转发）。

优点：

- 简单
- 可预测
- 易验证

缺点：

- 遇到热点时缺乏绕行能力

### Source routing

路径由编译器或 runtime 预先决定，header（头 flit，数据包的首个传输单元，携带路由等控制信息）携带路由信息。

它对 AI tile dataflow（数据流）很重要，因为：

- 流量往往更规整
- 编译器更容易提前规划通路
- router 本地逻辑可以更轻

### Adaptive routing

根据拥塞情况动态选路。

优点：

- 某些不规则 traffic 下更灵活

代价：

- 验证更复杂
- 乱序与 deadlock（死锁，多个数据包循环等待资源导致永久阻塞）处理更难
- 不一定适合高度编排的数据流主路径

## Arbitration（仲裁）决定谁先过

即使 routing 已经确定，多个输入争同一输出时仍需要仲裁。

而且仲裁不只发生在 switch output 上，也可能发生在 VC 分配、注入口接入、目的端 ejection（弹出）等共享资源上。

常见策略：

- round-robin（轮询）
- fixed priority（固定优先级）
- age-based（基于报文年龄）
- QoS-aware arbitration（服务质量感知仲裁）

## 为什么必须区分 stall 类型

一个 packet 没过，并不都叫“拥塞”。

至少要区分：

- credit stall（信用计数阻塞）：下游没空位
- switch stall（交换阻塞）：仲裁没赢
- routing restriction：路径本身受限

不同 stall 类型对应完全不同的优化手段。

## AI NoC 的实用建议

- 主数据流优先保持简单、可预测、可静态规划
- control / sync 不要与 bulk data（大块数据传输）共用同一低优先级路径
- 动态流量场景再评估 adaptive routing 的价值

## 本页结论

routing 决定全局路径分布，arbitration 决定局部竞争结果。  
做 NoC 架构探索时，如果你只改 link width（链路位宽）却不分析 routing 与仲裁，通常只能看到表面现象。
