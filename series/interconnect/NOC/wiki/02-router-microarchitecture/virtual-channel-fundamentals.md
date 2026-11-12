# Virtual Channel Fundamentals

上级：[02 Router Microarchitecture](./README.md)
相关：[Input Buffer Organization](./input-buffer-organization.md), [../04-routing-and-flow-control/deadlock-avoidance-turn-model.md](../04-routing-and-flow-control/deadlock-avoidance-turn-model.md)

## 这页在回答什么问题

VC 看起来像“把一条物理通道多开几路逻辑队列”，但它为什么会成为 NoC 设计的枢纽机制：既缓解 HoL blocking，又参与 deadlock avoidance 和 traffic isolation。

如果只把 VC 理解成“多几个 queue”，你会严重低估它对 allocator 复杂度、QoS 策略和可分析性的影响。

## 没有 VC 时，错误耦合来得非常快

设想一个 input port 只有一个 FIFO。队首 packet 因 East 方向堵住了，后面本来要去 North 的 packet 也一起停。这就是 HoL blocking。

VC 的第一个动机，就是把这种错误耦合拆开。多个逻辑队列共享同一物理链路，但排队状态独立，于是“某个方向堵住”不会立刻把所有流量都拖死。

这个动机非常重要，但还不是 VC 最深的价值。因为如果只是为了缓解 HoL，你可能会以为“多开几个队列，越多越好”。真实系统里，VC 的第二个动机更强，也更约束数量选择。

## VC 的第二个动机：给资源依赖分层

wormhole packet 会沿路径持有一串资源：当前 input VC、下游 VC 绑定、buffer slot。死锁的根因，就是这些资源依赖形成环。

VC 提供的关键工具是：你可以把不同阶段、不同消息类型、或不同路由规则映射到不同 VC 层次上，从而打断“所有 packet 都在竞争同一圈资源”的局面。

Dateline 方法将跨环边前后的通道依赖分层，并限制回退，以消除所选路由的环形依赖。Escape VC 方法则提供一个可达目标、依赖无环的受限子网；仅有该子网还不够，必须证明允许进入 escape 的转移不会重新形成依赖环、所需 escape 资源可取得，且仲裁公平、端点最终服务。允许从 escape 任意回到 adaptive 网络可能重建环。两种方法的证明条件不能混为一句“有 VC 就无死锁”。

所以 VC 的真正价值，不是“有更多 lane”，而是“能把资源依赖拆层”。

## VC 不会增加物理带宽

这是最常见误解，必须单独说清。

一条物理链路每拍能传多少 flit，仍然只由 link width 和时钟决定。VC 数量增加之后：

- 逻辑队列更多
- credit 计数更多
- allocator 候选更多

但每拍能过的物理 flit 数没有变。VC 让共享更精细，不让链路变宽。

这点和 BUS 世界里“多 channel = 真正更多通路”很像但不相同。AXI 五通道分开后，地址和数据确实各有独立语义通道；VC 则是在同一条物理通路上做逻辑复用。

## VC 数量为什么不是越多越好

VC 多的好处：

- HoL blocking 更少
- traffic class 更容易隔离
- deadlock avoidance 手段更多

VC 多的代价：

- 若每 VC 深度和 flit 宽度固定，buffer bit 数随 VC 数增长；总容量固定时则每 VC 可能更浅
- VC allocator 规模变大
- switch allocator 候选增加
- credit state、binding state、调试复杂度都上升

更关键的是，对 deterministic NPU，这些额外自由度未必总是收益。静态调度系统本来就想减少动态不确定性；所需 VC 数由路由依赖、traffic class、隔离目标和负载决定。必须先证明死锁规避，再用目标流量评估吞吐与面积；不能仅由 NPU 类型推定数量。

## 一个简单状态图

每个 input VC 至少要维护：

```text
IDLE
  -> RC
  -> VA
  -> ACTIVE
  -> IDLE  // tail 成功离开本 input VC；仅释放本地上下文
```

并附带这些状态：

- `buffer occupancy`
- `downstream output port`
- `downstream vc binding`
- `credit count of bound downstream vc`

此图只描述本 input VC 的本地上下文。下游 slot credit 和 output VC 的再次分配许可是独立状态。采用严格策略时，即使本地 tail 已离开，上游也要等下游 tail 离开并返回 free 信号，才可把该 output VC 分给后包。具体事件和另一种 FIFO 复用策略见 [核心数据结构](../08-simulator-construction/core-data-structures.md#三种独立状态)。

## 一个定量直觉

假设每端口 4 个 VC，每 VC 深度 6，5-port router：

```text
total_slots = 5 * 4 * 6 = 120
```

如果改成 8 个 VC、每 VC 深度不变：

```text
total_slots = 5 * 8 * 6 = 240
```

buffer 容量直接翻倍。你也许缓解了更多 HoL blocking，但 allocator 候选数也接近翻倍。也就是说，VC 数量不是一个“只对性能负责”的参数，而是面积与控制复杂度的乘法器。

## AI NoC 和 CPU coherent NoC 的典型差别

AI NoC 常见的 traffic class 分法是：

- request
- response
- control
- bulk / stream

很多 deterministic NPU 会把 VC 主要用于：

- request/response 分离，避免 protocol-style blockage
- control 和 bulk 分离，保护低延迟小消息
- 适度切断资源依赖，便于死锁分析

CPU coherent NoC 往往需要更多 VC / VN，因为它有更多消息家族：request、response、snoop、ack、writeback 等，而且 ordering 和 protocol deadlock 约束更硬。这个对比很重要，因为它解释了为什么“别家 CPU NoC 用 8 个以上 VC”并不自动说明 AI NPU 也该如此。

## 常见误解

常见误解：VC 是物理 channel。  
实际上：VC 共享同一物理链路的带宽，只是逻辑队列和状态分离。

常见误解：VC 的唯一作用是缓解 HoL blocking。  
实际上：更关键的作用是做资源依赖分层和 traffic isolation，为 deadlock avoidance 和 QoS 提供抓手。

## 一句话理解

VC 不是给链路加带宽，而是给共享链路加秩序：把不同流量、不同依赖阶段和不同阻塞风险拆进独立逻辑队列。

## 建模启示

cycle-level 模型里，VC 必须是一等状态对象：

```text
VC {
  state
  flit_queue
  route_port
  downstream_vc
}
```

必须显式记录的事件：

- `vc_state_enter_rc`
- `vc_alloc_request`
- `vc_alloc_grant`
- `local_context_release_on_tail`
- `downstream_vc_permission_return`（严格策略下由 tail free 消息触发）

如果只关心 saturation throughput，不关心 worst-case latency 或 deadlock，可以把 `downstream_vc` 简化成静态映射，甚至只统计每个端口的活跃 VC 数。  
如果关心 deadlock-free 分析，`vc_class`、`dependency_edge` 和 `packet_holds_vc` 这些状态必须保留，因为你要追踪的是资源依赖图，而不只是流量计数。
