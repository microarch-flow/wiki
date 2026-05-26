# Deadlock Livelock Starvation

上级：[04 Routing And Flow Control](./README.md)

相关：[Deadlock Avoidance Turn Model](./deadlock-avoidance-turn-model.md)、[Arbitration Policies](./arbitration-policies.md)、[Credit Based Flow Control](../02-router-microarchitecture/credit-based-flow-control.md)

## 这页在回答什么问题

这页回答：NoC 里最容易混淆的三个“不前进”问题到底有什么区别，为什么它们不能用同一套手段处理。

## 1. Deadlock

`deadlock` 是最严格的“不前进”状态。

定义是：

- 一组 packet 或消息各自占有部分资源
- 同时等待别人释放下一部分资源
- 依赖关系形成闭环
- 没有任何一方能先前进一步

关键点在于：它不是“很慢”，而是“如果没有外部干预，系统理论上可以永远停在那里”。

在 NoC 里，deadlock 常见来源包括：

- routing-level channel dependency cycle
- request/response/control 间的 message dependency cycle
- endpoint buffer / ejection path 与上游请求链交织成环

## 2. Livelock

`livelock` 指的是系统一直在活动，但某个 packet 长期无法真正接近目的地。

典型特征：

- packet 在移动
- 资源在变化
- 系统看起来“没死”
- 但目标 packet 一直被绕开、重试或不断改道，长期无法完成

它更容易出现在：

- 过度灵活的 adaptive routing
- 缺少收敛规则的重试机制
- 某些只追求“别堵住当前”而不保证最终到达的局部策略

所以 livelock 是“忙着动但没结果”，deadlock 是“谁都动不了”。

## 3. Starvation

`starvation` 指的是：某个 packet 或某类流量理论上有路可走，也不一定存在闭环，但因为调度长期偏向别人，自己一直得不到服务。

最典型来源是：

- fixed-priority arbitration
- 某类流量持续低优
- 没有 aging 或份额保底

starvation 关注的是服务公平性，而不是通道依赖闭环。

它可能只影响一类低优流量，但系统级后果并不一定小，因为被饿死的那类流量可能恰好是 completion、descriptor 或 sync。

## 为什么这三者常被混淆

因为用户看到的现象都可能是：

- timeout
- 延迟非常长
- 某条链路上一直没完成

但它们的结构不同：

- deadlock：依赖闭环
- livelock：持续活动但不收敛
- starvation：调度一直不轮到你

如果把 starvation 误判成 deadlock，你会去改 routing 规则，结果没用。
如果把 deadlock 误判成拥塞，你会去加 buffer，结果只是把死锁位置推远。

## Credit 为什么不能解决这三者

credit-based flow control 解决的是：

- 不要把下游 buffer 发爆

它不自动解决：

- deadlock 的循环等待
- livelock 的路径不收敛
- starvation 的调度不公平

这点必须非常清楚。`credit == 0` 只是一个症状，不是根因分类。

## 对应的典型处理手段

### 对 deadlock

常见手段：

- dimension-order routing
- turn restriction
- escape VC
- request/response/control 分 VC 或分网络

核心思想是打断资源依赖环。

### 对 livelock

常见手段：

- 限制重路由次数
- 保证每次选择都朝着某种收敛目标推进
- 保留 deterministic escape path

核心思想是保证 packet 最终会朝目的地逼近，而不是无限兜圈。

### 对 starvation

常见手段：

- round-robin
- aging
- 最长等待优先
- 保底带宽或保底服务窗口

核心思想是给每个候选某种服务上界保证。

## 对 deterministic NPU 的实际优先级

对于很多 deterministic NPU，真正第一优先级通常是：

1. 先确保不会 deadlock
2. 再确保关键 class 不会 starvation
3. 最后才讨论 adaptive 下的 livelock 风险

原因是：

- 主路径多半不做极强 adaptive
- 静态映射和 message dependency 更可能是真实风险源
- control/response 被饿死的系统代价很高

## 观测和归因上的差异

如果要区分这三者，观测点应关注不同信号：

- `deadlock`：一组资源长期互相等待，拓扑上能画出环
- `livelock`：packet 持续移动或重选路径，但 progress metric 不增长
- `starvation`：某候选长期请求，但 grant count 极低或为零

这就是为什么调试时不能只看“某包很久没到”，而要看它到底是在等、在绕，还是根本抢不到。

## 常见误区

- 认为所有“超时”都是死锁
- 认为加深 buffer 一定能改善 forward progress
- 认为 fixed-priority 只会让平均性能变差一点

更准确的说法是：

- 超时可能来自 deadlock、starvation、长尾拥塞或软件等待链
- buffer 可以吸收瞬时抖动，但不消除闭环依赖
- 低优流量被长期压制时，可能拖垮整个软件/硬件依赖链

## 一句话理解

deadlock 是“互相卡死”，livelock 是“忙着兜圈”，starvation 是“你一直抢不到机会”；三者都表现为不前进，但根因完全不同。

## 建模启示

如果仿真器要正确区分这三者，不能只统计 packet latency。至少还要额外统计：

- wait-for graph 或 channel dependency graph
- packet progress metric：是否更接近目的地、route 是否反复变化
- request-to-grant wait time 与 grant fairness

一个实用做法是：

- 对 deadlock：检测一段时间内是否存在闭合等待环且无释放事件
- 对 livelock：检测 packet 虽多次转发但距离目标或阶段编号长期不下降
- 对 starvation：检测持续请求但 grant 长时间缺失，且系统其他流量仍在前进

这样模型才能把“没完成”细分成真正有操作价值的类别。
