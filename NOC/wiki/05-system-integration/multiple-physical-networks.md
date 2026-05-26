# Multiple Physical Networks

上级：[05 System Integration](./README.md)

相关：[QoS And Priority Classes](../04-routing-and-flow-control/qos-and-priority-classes.md)、[NoC Vs Bus Revisited](./noc-vs-bus-revisited.md)、[Reduction And Collective Networks](../06-ai-noc-specifics/reduction-and-collective-networks.md)

## 这页在回答什么问题

这页回答：为什么很多真实 AI 芯片不是“一张大 NoC 搞定所有流量”，而是会拆成多张物理网络或多平面。

## 根因不是“设计者喜欢复杂”

多网络的根因是不同 traffic class 的需求差异太大。

典型差异包括：

- bulk tensor stream：高带宽、中等延迟敏感
- control / descriptor：低带宽、极高延迟敏感
- completion / sync：包很小，但经常在依赖链关键位置
- reduce / collective：空间模式与普通 point-to-point 很不一样

如果所有这些都共享同一张物理网络，那么你必须在一套 router / link 资源里同时满足完全不同的目标，通常会变得又贵又难验证。

## 物理隔离和 VC 隔离不是一回事

逻辑隔离常见做法是：

- 同一物理网络里分多个 VC
- 再叠加 priority / weighted arbitration

物理隔离则更激进：

- 不同 traffic class 直接走不同链路、不同 router、甚至不同 topology

物理隔离的好处：

- 干扰边界最清楚
- 死锁域天然隔离
- 每张网可以按自身目标独立优化

代价：

- 面积和布线成本更高
- 某些低利用率时间段会资源浪费

## 常见的拆法

工程上最常见的分法通常不是“每类流量一张网”，而是按系统价值分层：

- `control network`
- `data network`
- 可选的 `memory / DMA fabric`
- 可选的 `collective / reduction fabric`

其中最常见、也最值得优先分离的是 `control` 和 `bulk data`。

原因很直接：

- control 很小，但一旦被拖慢，代价可能是整条 pipeline stall
- bulk data 很大，天然会吞噬共享资源窗口

## 为什么 AI 芯片比通用 SoC 更常见多网络

因为 AI 芯片的数据面和控制面差距更极端：

- 数据面要吃非常高的持续带宽
- 控制面本身流量不大，但对时序和可观测性更敏感

通用 SoC 里很多时候 BUS + NoC 分层已经足够；AI 芯片里即便进入 NoC 体系后，NoC 内部往往还要继续分层。

## 它和 QoS 的关系

多网络本身就是最强的一种粗粒度 QoS。

相比“在同一张网上继续堆规则”，物理分离的优势在于：

- 行为更稳定
- debug 更直接
- latency bound 更容易解释

这也是为什么当某类流量必须拿到强保证时，工程上经常优先考虑物理分离，而不是继续增加优先级状态机复杂度。

## 什么时候 VC 隔离还不够

下面这些信号通常说明该认真考虑物理分离了：

- control latency 对系统 forward progress 极敏感
- bulk data 持续时间长，VC 只能排队，无法真正隔离带宽
- 不同流量模式差异很大，需要不同 topology
- debug / verification 需要很清楚的因果边界

此时继续在单网里堆 VC 和 QoS 规则，收益会越来越差。

## 它不是永远越多越好

多网络同样有边际成本：

- 更多链路与 router 面积
- 更高布线压力
- NI 端口与协议更复杂
- traffic 在多张网之间切分时更难做容量平衡

所以常见最优点不是“越多越好”，而是“先把最危险的语义冲突隔离开”。对多数系统，第一优先级仍是 control/data 分离。

## 一句话理解

多物理网络的价值在于：当不同流量的目标函数差得太大时，与其在同一张网上互相妥协，不如直接把它们拆开。

## 建模启示

仿真器第一版至少应支持：

- 多张独立网络
- 每张网独立的 topology / width / latency 参数
- traffic class 到网络的映射
- per-network utilization / latency / stall 统计

如果模型只支持单网络，你至少也要显式估计：

- control/data 是否应物理分离
- 当前结果里哪些 QoS 问题其实是“缺一张独立网”带来的

否则会系统性低估物理隔离的收益。
