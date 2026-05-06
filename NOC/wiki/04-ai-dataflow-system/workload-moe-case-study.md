# MoE Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[Collective Communication](./collective-communication.md)、[Source Routing 与 Compiler-Driven NoC](../03-topology-routing/source-routing-compiler-driven-noc.md)

## 为什么 MoE 对 NoC 很“狠”

MoE 常常把 AI NoC 推向更动态、更不规则的区域，因为它引入了：

- token 到 expert 的分发
- expert 输出的 gather
- 可能高度不均衡的流量热点

这使它成为评估 routing、QoS 和 collective 价值的高压案例。

## 典型通信形态

- many-to-many dispatch
- many-to-many gather
- 局部 fan-in / fan-out 突发

这比普通 GEMM 或规则 pipeline 更接近网络压力测试。

## 你最该观察的点

- traffic 是否严重偏斜到少数 expert
- source routing 在动态流量下是否失去优势
- adaptive routing 是否有明显收益
- all-to-all 是否需要单独 traffic class 或 plane

## 常见热点

- 热门 expert 所在 cluster
- gather 回流路径
- memory response 与 dispatch 混行的共享链路

## 常见 stall

- `SWITCH_CONFLICT`
- `LINK_BUSY`
- `ROUTE_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`

## 一个关键实验

比较：

- deterministic / source routing
- 带有限局部自适应的 routing

观察：

- hotspot link 分布
- 尾部延迟
- workload completion time
- starvation 现象

## 为什么它也是 QoS 问题

如果 MoE dispatch / gather 与 control、memory response 完全混跑，系统很容易出现：

- 关键小消息饿死
- barrier 被异常放大
- 端到端时延严重抖动

所以 MoE 不只是 routing 问题，也是 QoS 与公平性问题。

## 本页结论

MoE case 的价值，在于它逼你面对 AI NoC 中最不规整、最容易失衡的流量形态。  
如果一套 NoC 方案只在规则 GEMM 下表现好，而在 MoE 下明显失稳，那它的系统适用性就是受限的。
