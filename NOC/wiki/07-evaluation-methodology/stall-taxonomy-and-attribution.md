# Stall Taxonomy And Attribution

上级：[07 Evaluation Methodology](./README.md)

相关：[Arbitration Policies](../04-routing-and-flow-control/arbitration-policies.md)、[NOC Meets Memory System](../05-system-integration/noc-meets-memory-system.md)

## 这页在回答什么问题

这页回答：性能下降时，到底应该怎样把“系统变慢”拆成可行动的 stall 原因，而不是只说一句“拥塞了”。

## 为什么 taxonomy 比平均 latency 更重要

平均 latency 只能告诉你结果，不告诉你根因。

真正有用的归因必须回答：

- 谁在等
- 在等什么资源
- 这个等待属于网络、端点还是系统依赖

如果没有 taxonomy，调参就会变成盲试：

- 遇到慢就加 buffer
- 遇到 tail 就加宽链路
- 遇到热点就怪 topology

这经常会南辕北辙。

## 一套实用的主 stall 类别

### NO_CREDIT

队首 flit 所需的下游 VC 在发送端记录的可用 credit 为 0，因而本拍不能按该 credit 契约发送。这不等于此刻下游物理 buffer 必然已满：下游可能已出队并腾出槽，但返回的 credit 仍在途；也可能有已发送 flit 正在前向链路上，占用了槽的预留额度。

例如单 VC 深度为 `B`，每个发送的 flit 恰好预留一个槽，且每次出队恰好返回一个 credit。在无丢失或重复的前提下，可核对 `发送端可用 credit + 前向在途 flit + 下游已占槽 + 返回在途 credit = B`。不同实现若有额外预留或批量返回，还须将相应状态计入守恒式。排查时应同时观察 buffer occupancy、前向在途和返回 credit 延迟。

它更接近：

- flow control 问题
- endpoint / ejection 消费问题
- buffer / round-trip sizing 问题

### SWITCH_CONFLICT

多个候选同时争同一个输出或分配资源，仲裁没赢。

它更接近：

- 局部资源竞争
- arbitration / class policy
- path 汇聚过强

### LINK_BLOCKED

队首已具备其他条件，但所需链路本拍不能接收，例如正在发送其他 flit 的 phit 或 serializer 尚未释放。该原因与仲裁失败分开计数。

它更接近：

- 带宽瓶颈
- 路径过度集中
- traffic pattern 本身的问题

### EJECTION_BLOCKED

packet 到了目的 router，但目的端 NI、FIFO、SRAM 或 local consumer 接不住。

这是最容易被误判成“网络堵了”的类别之一。

### INJECTION_BLOCKED

packet 还没真正进入网络，就在源端被卡住。

这往往提示：

- source queue 满
- 本地数据没准备好
- 本地端口速率不足

### ROUTE_BLOCKED

当前上下文没有合法或可选择的路由。合法输出已经确定但下游 VC 许可不可用时，使用独立的 `VC_ALLOC_FAIL`，不记为 route blocked。

它更接近 routing / class / path restriction 问题。

### WAITING_FOR_DEPENDENCY

这类 stall 很关键，因为它提醒你：

- 不是所有“算力没打满”都是 NoC 自己的问题
- 很多等待来自上层依赖链或跨 stream 同步

## attribution 的核心规则

一个可用的 simulator 最好满足：

- 统计对象定义为每个非空 input VC 队首的 `flit-router-cycle`，每对象每拍最多一个主因；无活动时不计 stall
- endpoint 的注入等待以 `endpoint-cycle` 单独计数，workload 依赖未满足记 `WAITING_FOR_DEPENDENCY`，不混进 router 分母
- 同一队首同时无 credit 且竞争输出时，按固定优先级例如 `ROUTE_BLOCKED → VC_ALLOC_FAIL → EJECTION_BLOCKED/NO_CREDIT → LINK_BLOCKED → SWITCH_CONFLICT` 只计一个主因；其他条件可存在次因 bitset
- 链路占用或 serialization 与输掉 SA 的竞争分别记录，避免对同一对象同一周期重复累加；分母与聚合方式随结果一起报告

这样你才能回答：

- 哪类消息最容易被压
- 最先出问题的是哪层
- 优化动作应该打在哪个层级

## QoS 和 fairness 为什么要一起看

如果只做 stall 分类，不看 per-class 与公平性，仍然不够。

例如：

- 控制流 latency 很好
- 但 bulk class 一直抢不到资源

这不一定是好设计。因为低优流量也可能在更长依赖链里反过来拖垮系统。

因此 stall attribution 应至少支持：

- per-class stall
- starvation indicator
- long-tail wait indicator

## 一个实用的归因顺序

看见系统变慢时，可以按这个顺序追：

1. 是 workload-level 等待还是网络-level 等待
2. 如果是网络级，先看 credit / ejection 还是 switch / link
3. 再看是 topology / arbitration / endpoint / memory 哪一侧在主导
4. 最后再决定优化动作

## 常见误区

- 把所有 stall 都叫 congestion
- 看到 NO_CREDIT 就只想加 buffer
- 看到 WAITING_FOR_DEPENDENCY 还只盯着 router

更准确的看法是：

- congestion 只是现象，不是完整分类
- buffer 只能解决部分 flow-control 问题
- 有些 stall 的根因在 workload 编排、memory path 或 endpoint

## 一句话理解

stall taxonomy 的价值，在于把“系统变慢”拆成能直接对应优化动作的等待结构。

## 建模启示

仿真器设计时，stall reason 应作为一等统计对象，而不是附加日志。至少应支持：

- per-cycle dominant reason
- per-class aggregation
- per-node / per-link attribution
- workload-level dependency wait

没有这套归因，后面的 architecture exploration 很难稳定地产出高置信度结论。
