# Deadlock Avoidance Turn Model

上级：[04 Routing And Flow Control](./README.md)

相关：[Dimension-Order Routing](./dimension-order-routing.md)、[Virtual Channel Fundamentals](../02-router-microarchitecture/virtual-channel-fundamentals.md)、[Deadlock Livelock Starvation](./deadlock-livelock-starvation.md)

## 这页在回答什么问题

这页回答：如果纯 `XY` 太死板，如何在保留无死锁保证的同时给 routing 一点绕行自由度。

## 背景

纯 dimension-order routing 的方法很硬：直接规定维度顺序，结果是路径空间最容易分析，但也最受限。

`turn model` 的思路更细：不是完全固定整条路径，而是只禁止一小部分“危险转弯”，让 packet 还能在剩余空间里选择路径。

这是一种折中：

- 比 XY 更灵活
- 比 fully adaptive 更容易做 deadlock 证明

## 为什么“转弯”是关键

在 2D mesh 里，形成 channel dependency cycle 通常需要 packet 围着某个环不断做方向转换。也就是说，危险不在“向东走”本身，而在“从某方向转到另一方向”的组合。

如果我们禁止一部分转弯，某些闭环就无法闭合。

这就是 turn model 的核心：通过删除一小组转向规则，打断可能的资源依赖环。

## 常见例子

### West-First

规则：如果路径需要向西，必须先把所有向西的移动走完，之后才能再做别的方向选择。

它意味着某些转弯被禁止，例如不能在已经向北或向南之后再转去西边。

效果：

- 保留了一部分最短路径选择
- 但消掉了某些依赖环

### North-Last

规则：如果最终需要向北，那么向北动作必须放到最后阶段。

效果和 West-First 类似，也是通过限制某类转弯来保持无死锁。

### Negative-First

规则：先完成所有负方向位移，再走正方向。

它看起来像 dimension-order 的变体，但思想仍然是：用方向阶段化限制危险转弯。

## 它和 DOR 的关系

`turn model` 不是完全不同的世界，更像是介于 DOR 和 adaptive 之间的中间层。

可以把它理解为：

- DOR：每个 `(src,dst)` 唯一路径
- turn model：每个 `(src,dst)` 有有限条合法路径
- fully adaptive：合法路径集合最大，但需要更强的安全机制

因此 turn model 常被用来回答这样的问题：

- 我不想被 XY 完全绑死
- 但我也不想把 deadlock 证明变得太难

## 它的收益边界

turn model 只有在 topology 真有多条可用短路径时才有价值。

如果是在：

- ring
- 几乎没有 path diversity 的小规模网络
- 已经由 floorplan 限定了主要走向的网络

那 turn model 给你的自由度其实很有限。

mesh、concentrated mesh、某些高基数局部网络里，它才更容易体现价值。

## 它不能自动解决什么

turn model 解决的是 routing-level channel dependency cycle，不自动解决：

- request/response 的 message dependency
- endpoint ejection buffer 被堵住
- control 和 bulk data 争用同一高优先级出口
- starvation 或 tail latency 波动

所以 turn model 不是完整系统安全方案，只是 routing 子问题的约束工具。

## 为什么很多 AI NPU 不把它当默认主线

因为很多 AI 芯片最关心的是：

- 编译器能否静态预测路径
- 延迟分布能否稳定复现
- debug 时能否快速定位热点

turn model 虽然没 fully adaptive 那么复杂，但已经引入了：

- 多条合法候选路径
- 局部状态驱动的选择
- 更复杂的 trace 解释空间

如果主流量本来就高度规则，这部分额外自由度不一定值回票价。

## 和 escape VC 的配合

在更灵活的 adaptive 设计里，一个常见套路是：

- 普通 VC 允许用更自由的 turn-constrained adaptive routing
- 保留一个 escape VC，只允许走确定无死锁的规则路径

这样即使局部决策空间较大，也有一个保底的 forward-progress 通道。

这说明一个很重要的工程事实：routing 的自由度越大，通常越需要额外的 VC 结构来兜底。

## 一个工程判断标准

如果你在设计阶段想知道要不要上 turn model，可以先问：

1. 热点是否来自固定映射，而不是局部瞬时拥塞？
2. 多路径是否真实存在且能显著分流？
3. 系统是否愿意承担更高的验证和观测复杂度？
4. 是否已经把 placement、VC 隔离、多网络分离做到了合理水平？

如果前两个答案都偏否，turn model 很可能不是优先级最高的改进项。

## 一句话理解

turn model 是一种“只删掉危险转弯，而不是锁死整条路径”的无死锁折中方案。

## 建模启示

建模 turn model 时，不要只记录 hop 数；要显式记录：

- 每个 router 允许的输入方向到输出方向转移集合
- 哪些 `src-dst` 对有多条合法最短路径
- 在这些路径之间如何 tie-break：随机、轮询、局部拥塞优先

如果模型还要评估死锁安全性，就必须把“允许的 turn graph”转成 channel dependency graph，检查是否存在可闭合环。对系统级模型，还要再叠加：

- VC class
- message class
- escape VC 是否存在

否则你只是在模拟“更灵活”，没有模拟“为什么还能安全地灵活”。
