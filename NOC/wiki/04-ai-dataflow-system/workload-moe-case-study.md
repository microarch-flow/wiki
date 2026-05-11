# MoE Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[Collective Communication](./collective-communication.md)、[Source Routing 与 Compiler-Driven NoC](../03-topology-routing/source-routing-compiler-driven-noc.md)

## 读这页前先统一几个词

- `MoE`：每个 token 只激活部分 expert 的模型
- `dispatch`：把 token 或数据片段送到被选中的 expert
- `gather`：expert 算完后把结果收回来
- `dynamic traffic`：目的地和热点会随输入变化，不像 GEMM 那样规则
- `starvation`：某类流量长期得不到服务，虽然系统整体还在运转

## 为什么 MoE 对 NoC 很“狠”

MoE（混合专家模型）常常把 AI NoC 推向更动态、更不规则的区域，因为它引入了：

- gate（门控）为每个 token 选择少数 expert（专家模块）的分发
- expert 输出的 gather（收集）
- 可能高度不均衡的流量热点

关键不是“所有 token 发给所有 expert”，而是“每个 token 只发给少数被选中的 expert，但不同 token 的选择会随输入变化且可能高度偏斜”。

这使它成为评估 routing（路由）、QoS（服务质量）和 collective（集合通信）价值的高压案例。

## 典型通信形态

- 稀疏、偏斜的 all-to-all-like dispatch
- 稀疏、偏斜的 all-to-all-like gather
- 局部 fan-in / fan-out 突发

这比普通 GEMM（通用矩阵乘法）或规则 pipeline（流水线）更接近网络压力测试。

## 你最该观察的点

- traffic 是否严重偏斜到少数 expert
- source routing（源路由）在动态流量下是否失去优势
- adaptive routing（自适应路由）是否有明显收益
- all-to-all（全对全通信）是否需要单独 traffic class（流量类别）或 plane

## 常见热点

- 热门 expert 所在 cluster（簇）
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

- hotspot link（热点链路）分布
- 尾部延迟
- workload completion time（工作负载完成时间）
- starvation（饥饿）现象

## 为什么它也是 QoS 问题

如果 MoE dispatch / gather 与 control、memory response 完全混跑，系统很容易出现：

- 关键小消息饿死
- barrier（同步屏障）被异常放大
- 端到端时延严重抖动

所以 MoE 不只是 routing 问题，也是 QoS 与公平性问题。

## 本页结论

MoE case 的价值，在于它逼你面对 AI NoC 中最不规整、最容易失衡的流量形态。  
如果一套 NoC 方案只在规则 GEMM 下表现好，而在 MoE 下明显失稳，那它的系统适用性就是受限的。
