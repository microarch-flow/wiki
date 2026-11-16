# Workload Attention Decode KV Cache

上级：[06 AI NOC Specifics](./README.md)

相关：[Memory Centric NOC](./memory-centric-noc.md)、[QoS And Priority Classes](../04-routing-and-flow-control/qos-and-priority-classes.md)

## 这页在回答什么问题

这页回答：为什么 decode with KV cache 是 AI NoC 里最典型的 memory-centric、response-sensitive 场景之一。

## decode 同时受流量和依赖链约束

decode 的典型特点是：

- 常见逐 token decode 的每一步为每个序列生成一个 token；批处理和投机解码可改变调度
- 同一序列的后续步骤依赖先前结果
- KV cache 读取频繁
- 小量 control / sync 很关键

总 KV/权重字节数及实际服务带宽会决定搬运时间，逐 token 依赖也会使关键路径延迟影响下一步。context、batch、缓存命中和映射不同，主导因素可能不同。除测量服务带宽外，还需观察：

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

## KV 带宽和依赖延迟都可能主导

若每个 decode step 对每层读取完整历史 K/V，忽略新 token、自身缓存命中、压缩和额外元数据，读取字节约为：

`2 × batch × layers × context × KV_heads × head_dim × dtype_bytes`。

例如 batch=1、layers=32、context=4096、KV_heads=8、head_dim=128、FP16=2 B，约 536,870,912 B = 512 MiB/step。GQA 使用 KV head 数而不是 query head 数；分片只改变各端口负载，不自动减少总字节。若大 context 或 batch 使 KV 流量占据关键路径，持续带宽很重要；小 batch/短 context 也可能被单次返回、同步和依赖延迟主导。应同时测 KV payload 服务率、关键 response 延迟和 token time，再判断 QoS 与带宽的价值。

## placement 在这里特别值钱

如果 KV cache、memory port、compute tile 的空间关系不合理，那么：

- response 路径变长
- 局部热点更集中
- static schedule 的收益下降

因此 decode 常常会把 memory placement 的重要性放大到和 routing 同级。

## 它和 prefill 的最关键区别

prefill 更像 bulk distribution；
decode 有逐 token 依赖，KV 返回也可能是大数据流。

这就是为什么同一个芯片上，适合 prefill 的设计不一定天然适合 decode。

## 一句话理解

decode 同时依赖 KV/权重数据供给与关键路径响应；两者的相对重要性由 context、batch、缓存和映射决定。

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
- KV payload bytes 和各瓶颈端口的有效服务率
- completion-to-next-step gap
- workload token time

否则模型会错把 decode 当成普通低吞吐 workload，而忽略其真正的系统敏感点。
