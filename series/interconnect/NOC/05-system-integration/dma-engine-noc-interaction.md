# DMA Engine NOC Interaction

上级：[05 System Integration](./README.md)

相关：[NI Network Interface Design](./ni-network-interface-design.md)、[Traffic Patterns And Characterization](./traffic-patterns-and-characterization.md)、[QoS And Priority Classes](../04-routing-and-flow-control/qos-and-priority-classes.md)

## 这页在回答什么问题

这页回答：为什么 DMA 不该被看成“只会搬数据的机械手”，而应该被看成塑造 NoC traffic 形状的主动调度器。

## DMA 真正在决定什么

对 NoC 来说，DMA 至少决定五件事：

- request 何时发
- 一次发多大 burst
- 允许多少 outstanding request 同时在飞
- response 回来后如何重组和回写
- control、descriptor、bulk data 的交错方式

这些因素会直接决定网络看到的是：

- 平滑、持续的流
- 还是成团、周期性爆发的流

## outstanding window 不是越大越好

如果 outstanding 太小：

- memory latency 隐藏不住
- NI 常常等 response，注入口空转

如果 outstanding 太大：

- memory port 更容易被瞬时打满
- response 返回峰值更高
- ejection / local memory 压力被集中放大
- 其他 class 更容易被 bulk data 拖慢

所以 outstanding window 的本质不是“能力上限”，而是把吞吐和可控性做平衡的系统参数。

## burst size 也不是越大越好

大 burst 的好处：

- header 开销低
- 链路利用率高
- 对 HBM 或大块 SRAM 搬运更高效

代价：

- 占用链路和端口的时间更长
- 更容易压住 control / response 小消息
- return path 上的峰值更尖锐

小 burst 的好处是更灵活、更利于混流，但效率会下降。

因此 DMA 调度的核心不是把 burst 拉到最大，而是把 burst 组织成符合系统目标的形状。

## request 和 response 必须一起看

很多人只看 DMA 发请求的能力，却忽略：

- response 会不会挤回同一路径
- response 到达后目的端能不能及时接住
- writeback 是否和 compute / refill 冲突

对 memory-centric 场景尤其如此。真正限制 forward progress 的，经常不是 request 发不出去，而是 response 回不来。

## DMA 为什么会制造“假网络问题”

一个典型现象是：网络热点呈周期性波峰，而不是持续饱和。

这常见于：

- DMA 在阶段边界集中发 burst
- 多个 stream 同步推进，形成同相请求风暴
- descriptor / data / completion 没做足够隔离

这时如果只盯着 topology 或 routing，很容易误诊。真实根因是 DMA 的节奏把网络打成了脉冲流。

## 它和 QoS 的关系

bulk DMA 如果和以下流量完全同权混跑，风险很高：

- descriptor
- completion / response
- control / sync

因为这些小消息虽然流量小，却处在依赖链前端。被拖慢后，系统级损失可能远大于 bulk data 少一点吞吐。

因此 deterministic NPU 的常见思路是：

- DMA bulk traffic 用中等优先级或独立 data fabric
- descriptor / response / completion 放高优或独立 class

## 它和 local memory 的关系

DMA 并不是只和 NoC 打交道，它还会直接冲击终点本地存储系统。

典型冲突包括：

- refill 写 local SRAM 与 compute 读冲突
- writeback 与 reduce 结果回写争同一 bank / port
- response 到达时 ejection FIFO 已经被本地消费节奏拖慢

这就是为什么 DMA 调度既是 NoC 问题，也是 local memory arbitration 问题。

## 一个工程上更实用的判断方式

看到系统慢时，先分清是下面哪一类：

- request 发不满：outstanding 不足或 descriptor 路径太慢
- request 发太猛：memory port / return path / ejection 顶不住
- burst 粒度不对：bulk 效率和 tail latency 之间失衡
- class 隔离不足：小消息被大搬运淹没

这比先争论 mesh 还是 tree 更接近根因。

## 一句话理解

DMA 决定的不是“有没有数据在动”，而是数据以什么节奏、什么粒度、什么并发度冲进 NoC 和 memory system。

## 建模启示

建模 DMA 时，第一版至少要有：

- request queue
- response queue
- outstanding limit
- burst size
- descriptor / command accept 延迟

如果要做更真实的系统分析，还应加入：

- per-stream DMA channel
- throttle / pacing 机制
- response reassembly
- completion visible 到 runtime 的边界

实验上最少应扫描：

- outstanding window
- burst size
- QoS / class mapping
- 与 local memory service rate 的耦合

否则你会高估理论链路价值，低估 DMA 自身塑造流量的能力。
