# Memory Centric NOC

上级：[06 AI NOC Specifics](./README.md)

相关：[NOC Meets Memory System](../05-system-integration/noc-meets-memory-system.md)、[Workload Attention Decode KV Cache](./workload-attention-decode-kv-cache.md)

## 这页在回答什么问题

这页回答：当系统主要瓶颈不再是 tile-to-tile forwarding，而是 memory request / response 路径时，NoC 的优先级应该怎样重排。

## 什么叫 memory-centric

`memory-centric` 不是说网络只连 memory，而是说系统表现更受这些路径支配：

- tile -> memory request
- memory -> tile response
- refill / spill / writeback
- memory-side endpoint 和 return path 的局部热点

在这种状态下，网络最重要的任务不是再提高一点理论注入率，而是保护关键返回路径和终点消费能力。

## request 和 response 的地位不对等

很多 memory-centric 场景里，真正处于关键路径上的往往是 response：

- request 发出去只是开始
- response 回来才决定 compute 是否能继续

因此如果 response 被 bulk DMA、background traffic 或不合理 QoS 拖慢，系统会表现得像“总带宽也许还行，但 token latency 很糟”。

## 哪些 workload 容易进入这种状态

典型场景包括：

- decode
- KV cache 主导路径
- 高并发 memory refill
- 某些 heavily memory-bound inference

这些场景下，NoC 的关注重点会从 `point-to-point throughput` 转向：

- response isolation
- memory port placement
- ejection / local SRAM write 能力
- request-response class 分离

## 为什么这不是单靠 HBM 带宽能解释完的

HBM 或 controller 当然常是主瓶颈，但 NoC 仍然重要，因为它决定：

- memory port 附近热点如何扩散
- response 是否会被不关键流量淹没
- 关键返回在最后几 hop 上会不会被拖慢

因此 memory-centric NoC 不是“网络不重要”，而是“网络要围绕 memory 路径重新组织优先级”。

## 常见系统策略

更有效的策略通常包括：

- request / response 分 class 或分网络
- response 提高优先级
- memory port 做更合理的空间分散
- decode / control / completion 与 bulk stream 隔离

这比单纯把 data router 继续做大，往往更符合收益。

## 一句话理解

memory-centric NoC 的关键不是让所有流量都更快，而是别让真正卡住 compute 的 memory response 在最后一段路上被拖死。

## 建模启示

模型至少要显式区分：

- request class
- response class
- memory port service point
- ejection blocked
- response-sensitive completion metric

如果模型把 memory traffic 只当成“更大一点的 point-to-point 流”，会严重低估 decode 类场景对 QoS 和 return-path 组织的敏感性。
