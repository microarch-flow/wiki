# Attention Decode Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[NI / DMA / 存储接口](./ni-dma-memory-interface.md)、[QoS、公平性与 Stall Taxonomy](../05-modeling-evaluation/qos-fairness-stall-taxonomy.md)

## 读这页前先统一几个词

- `decode`：每次生成一个 token 的自回归阶段
- `control / sync`：不是大数据块，但决定执行顺序的小控制消息和同步消息
- `tail latency`：最慢那部分请求的延迟，常用 P99 之类百分位表示
- `WAITING_FOR_OTHER_STREAM`：本地还在等其他依赖流完成，因而暂时不能继续
- `response-sensitive`：总带宽未必大，但对响应返回时间极其敏感

## 为什么 decode 必须和 prefill 分开

decode（逐token解码）的典型特点是：

- 每一步只新增 1 个 token，下一步必须等待上一步结果
- batch（批次）更小
- step-by-step 生成
- latency（延迟）更敏感
- KV cache（键值缓存）访问路径更重要

所以 decode 的核心常常不是”总搬运量大不大”，而是”关键小消息和关键返回路径能否及时走通”。

## 典型 NoC 压力来源

- KV cache 相关读请求与返回
- 小粒度 control / sync（同步）
- compute stage 之间较细粒度的数据依赖
- 多用户推理下的动态流量叠加

## 它更像什么类型的问题

decode 更像：

- memory-centric
- response-sensitive
- latency-sensitive

这和 prefill 的 bulk throughput 主导很不一样。

## 你最该观察的点

- read response 是否被 bulk traffic 压住
- control / barrier（同步屏障）是否被延迟
- QoS（服务质量）是否显著改善 end-to-end latency
- KV cache placement 是否改变热点分布

## 常见 stall

- `NO_CREDIT`
- `EJECTION_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`

decode 场景下，`WAITING_FOR_OTHER_STREAM` 特别值得小心，因为系统级等待很容易被误判成纯 NoC 问题。

## 一个关键实验

比较：

- 所有 traffic 同优先级
- control / response 高优先级

观察：

- tail latency（尾部延迟）
- response return latency
- barrier latency（屏障延迟）
- workload completion time

## 本页结论

decode case 的关键不是追求最大带宽，而是保护关键响应路径和前进所需的小消息。如果这部分做不好，NoC 可能在链路并不高利用的情况下仍然显著拖慢系统。
