# Workload Attention Decode KV Cache

上级：[06 AI NOC Specifics](./README.md)

相关：[Memory Centric NOC](./memory-centric-noc.md)、[QoS And Priority Classes](../04-routing-and-flow-control/qos-and-priority-classes.md)

## 这页在回答什么问题

这页回答：为什么 decode with KV cache 是 AI NoC 里最典型的 memory-centric、response-sensitive 场景之一。

## decode 的核心不是总量，而是依赖链

decode 的典型特点是：

- 一步生成一个 token
- 下一步要等上一步
- KV cache 读取频繁
- 小量 control / sync 很关键

这意味着它最怕的不是“平均带宽略低”，而是：

- 关键 response 晚一点点就层层放大
- barrier / completion 被拖慢
- ejection 或 local consume 形成额外等待链

## KV cache 让它天然 memory-centric

KV cache 路径通常会带来：

- 高频 memory request
- 更关键的 response return
- 对 memory placement 的强依赖

因此 decode 更像在逼问：

- response 是否被隔离
- memory port 离 compute 多远
- local endpoint 能否及时接收返回

## QoS 在这里比纯吞吐更重要

对 decode 而言，一个非常典型的设计结论是：

- 给 response / control 更明确的保护
- 往往比再增加一点平均 data throughput 更有价值

因为 token latency 更取决于关键小流是否被准时交付，而不是整个 data plane 的平均吞吐数字。

## placement 在这里特别值钱

如果 KV cache、memory port、compute tile 的空间关系不合理，那么：

- response 路径变长
- 局部热点更集中
- static schedule 的收益下降

因此 decode 常常会把 memory placement 的重要性放大到和 routing 同级。

## 它和 prefill 的最关键区别

prefill 更像 bulk distribution；
decode 更像 critical response orchestration。

这就是为什么同一个芯片上，适合 prefill 的设计不一定天然适合 decode。

## 一句话理解

decode 的关键不是“流量大不大”，而是“卡住下一步的那条 memory response 能不能一直准时回来”。

## 建模启示

decode 模型至少要显式区分：

- request class
- response class
- control / barrier class
- per-step dependency
- KV placement

评估时要把重点放在：

- response latency
- tail latency
- completion-to-next-step gap
- workload token time

否则模型会错把 decode 当成普通低吞吐 workload，而忽略其真正的系统敏感点。
