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

下游没有空 buffer slot。

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

### LINK_BUSY

链路被长期占用。

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

路径受限、VC 不可用、合法出口暂不可用。

它更接近 routing / class / path restriction 问题。

### WAITING_FOR_OTHER_STREAM

这类 stall 很关键，因为它提醒你：

- 不是所有“算力没打满”都是 NoC 自己的问题
- 很多等待来自上层依赖链或跨 stream 同步

## attribution 的核心规则

一个可用的 simulator 最好满足：

- 每个周期只归一个主 stall reason
- stall 可以按 packet、class、router、endpoint 聚合
- 网络 stall 和系统依赖 stall 明确区分

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
- 看到 WAITING_FOR_OTHER_STREAM 还只盯着 router

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
