# Router Pipeline 与 Allocator

上级：[Router 微架构](./README.md)

相关：[Packet / Flit / Wormhole](./packet-flit-wormhole.md)、[VC / Deadlock](./virtual-channel-deadlock.md)

## 为什么这一页重要

很多人能理解 wormhole 和 credit，但一到真正实现 router，就会卡在：

- 每周期到底先做什么
- header 和 body 的处理为什么不同
- VC allocation 与 switch arbitration 的边界在哪里
- 哪些 stall 属于 allocator，而不是属于 link 或 buffer

这一页的目标就是把 router 从“概念图”推进到“可实现模型”。

## 一个典型的五阶段 pipeline

最常见的抽象是：

- `RC`：Route Computation
- `VA`：Virtual Channel Allocation
- `SA`：Switch Allocation
- `ST`：Switch Traversal
- `LT`：Link Traversal

并不是所有实现都严格分成五拍，但这个分解足够适合作为 simulator 和架构分析的主心骨。

## RC：Route Computation

作用：

- 读取 header
- 决定候选输出端口
- 生成下一跳路由信息

对 deterministic routing 来说，RC 往往很简单。  
对 source routing 来说，RC 甚至可能退化为“从 route info 里读下一跳”。

关键点：

- RC 通常主要对 header 生效
- body/tail 通常沿用 header 已经建立好的路径与状态

## VA：Virtual Channel Allocation

作用：

- 为 header 在目标输出端口的下游分配一个可用 VC

这是 wormhole + VC 体系的核心步骤之一，因为 packet 不是简单过一个 crossbar 就结束，而是要持续占用一条逻辑通路。

关键点：

- VA 一般只发生在 header
- body/tail 复用已分配 VC
- 如果没有空闲下游 VC，packet 会停在这里

这类 stall 通常应归到：

- `ROUTE_BLOCKED`
- 或更细的 `VC_UNAVAILABLE`

## SA：Switch Allocation

作用：

- 多个输入争同一个输出时，决定本周期谁可以通过

这是 router 局部竞争最直接的地方。

常见仲裁对象：

- input VC -> output port
- 或 input VC -> output VC / output port 组合

这类 stall 通常归到：

- `SWITCH_CONFLICT`

## ST：Switch Traversal

作用：

- 获胜 flit 穿过 router 内部 crossbar

对高层模型来说，ST 可以看作本 router 内部的一次移动。  
第一版 simulator 不必把 crossbar 内部再拆细，但应保留这一阶段在时序上的存在感。

## LT：Link Traversal

作用：

- flit 从当前 router 输出到下一个 router 输入

第一版通常可以假设：

- 每条链路每周期最多传 1 flit

如果以后要做更细粒度建模，再引入：

- 多周期长链路
- phit
- pipeline link

## Header、Body、Tail 为什么不能混着看

### Header

- 决定路径
- 决定 VC
- 决定 message class 资源归属

### Body

- 跟随 header 已建立的通路前进
- 主要消耗的是带宽和 buffer

### Tail

- 表示 packet 结束
- 触发 VC / 通路状态释放

如果把三者混成一个统一 flit 行为模型，很多资源释放时机会建错。

## Allocator 至少包含哪两类

### VC Allocator

解决“我能不能拿到下游逻辑通道”的问题。

### Switch Allocator

解决“本周期多个候选里谁先通过物理 crossbar / output port”的问题。

二者经常被混淆，但实际上：

- VC allocator 更偏长期资源占用
- switch allocator 更偏每周期瞬时竞争

## 你在 simulator 里至少要建哪些状态

- input buffer occupancy
- 每个 input VC 当前 packet 状态
- output credit table
- output VC availability
- per-cycle switch request / grant
- tail release 事件

## 一个推荐的 router tick 顺序

第一版可以按下面顺序实现：

1. 处理到达的 flit 和 credit
2. 更新 input buffer 与 VC 状态
3. 对 header 做 RC
4. 执行 VA
5. 执行 SA
6. 执行 ST / LT
7. 对被 pop 的上游 buffer 发送 credit
8. 处理 ejection

关键不是唯一顺序，而是你要在整套 simulator 中保持一致。

## 常见实现误区

- 把 credit 在 flit 到达下游时立即返还
- 不区分 header 与 body 的资源申请行为
- tail 不显式释放 VC
- 只做 switch arbitration，不做 VC allocation
- 只统计总延迟，不统计 allocator stall

## 第一版不必过早建得太细的部分

- 复杂 speculative allocator
- 多级 allocator pipeline
- 极细的 crossbar timing
- 物理实现级优化

## 架构分析里应该问什么

- allocator stall 在总 stall 里占比多大
- 是 VC 不够，还是 switch 冲突太多
- 不同 traffic class 是否在 allocator 处互相压制
- hierarchical NoC 是否减少了全局 allocator 压力

## 本页结论

router pipeline 与 allocator 是把 NoC 从“链路网络”变成“资源竞争系统”的关键。  
如果你不把 `RC / VA / SA / ST / LT` 和 `VC allocator / switch allocator` 分开建模，就很难把 stall 根因拆清楚。
