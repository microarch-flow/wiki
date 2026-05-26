# KV Cache / Decode Memory Path 深化

上级：[AI Dataflow 系统视角](./README.md)

相关：[Memory-Centric NoC](./memory-centric-noc.md)、[Attention Decode Case Study](./workload-attention-decode-case-study.md)

## 读这页前先统一几个词

- `KV cache`：存历史 token 的 key / value 张量，decode 每一步都要回头读它
- `decode step`：生成一个新 token 的一次迭代
- `step latency`：完成一个 decode step 的总时间
- `response isolation`：把关键响应流量和 bulk 流量隔离开，避免响应被长包压住
- `memory fragment`：一次逻辑读取被切成多个响应片段返回时的单个片段

## 为什么这页重要

decode（逐token解码）阶段最容易把人带偏的一点是：

- 看起来总流量不一定最大
- 但系统时延和 tokens/s（每秒生成token数）却很容易被拖慢

核心原因之一，就是 KV cache（键值缓存）和 decode memory path 往往处在更关键的前进路径上。

## Decode 的关键不是“流量大不大”

而是：

- 哪些访问在关键路径上
- 哪些返回必须及时到达
- 哪些数据依赖会让 tile 等待

在这类场景里，response 的及时性往往比总吞吐更重要。

## KV Cache 路径通常包括什么

一个简化路径通常是：

1. tile（计算单元）或 control 发起 KV 相关请求
2. request 经 NoC 到达 KV 所在 SRAM（片上静态存储）/ memory node
3. 数据被读出或聚合
4. response 经 NoC 返回 consumer tile
5. consumer tile 才能继续本轮 decode

这里任意一段抖动，都可能被放大成 step latency（单步延迟）波动。

## 为什么 KV 路径比普通 DMA 更敏感

普通 bulk DMA（大块直接内存访问）更像：

- 吞吐问题
- overlap 问题

KV decode path 更像：

- 短而急的关键路径问题
- request / response 时延问题
- 依赖满足问题

这也是为什么 decode 往往比 prefill（预填充）更需要 QoS（服务质量）和 response isolation（响应隔离）。

## KV Cache Placement 为什么关键

KV 如果放置不合理，常见后果包括：

- 某些 tile 到 KV 路径过长
- 多个活跃 tile 共享同一 memory node
- 响应流量在少数主干链路聚集

所以 KV placement 不只是容量规划，而是 NoC 问题。

## 本地 SRAM 与远端 memory 的分界

不同架构里，KV 可能：

- 更靠近 tile，本地化更多
- 放在 cluster（簇）级共享 SRAM
- 放在更远的 memory node 或近 HBM（高带宽存储器）端

这三者对 NoC 的含义很不一样：

- 本地化越强，NoC 压力越小，但容量受限
- 远端化越强，NoC 与 response path 越敏感

## Decode 阶段最常见的风险

- request / response 混跑
- response 被 bulk stream 压住
- ejection（弹出）/ local write path 太弱
- 多用户 decode 叠加造成热点漂移
- tile 在等待多个 memory fragment 汇合

## 最值得观察的指标

- response latency
- tail latency
- memory node 附近 link utilization（链路利用率）
- ejection blocked cycle
- waiting_for_other_stream cycle

如果只看平均 bandwidth，通常抓不到真正问题。

## 你至少要比较的实验

### 1. KV 放置位置变化

比较：

- 更本地化
- 更集中化
- 更分散化

观察：

- response latency
- hotspot 分布
- decode completion time

### 2. Response Priority on/off

比较：

- response 与其他流量同优先级
- response 更高优先级

观察：

- tail latency
- tile stall
- tokens/s

### 3. 多用户并发 decode

比较：

- 单流 decode
- 多流 decode

观察：

- 热点是否漂移
- QoS 是否开始显著重要

## 一条非常实用的判断

如果某个设计在 prefill 下很好，但 decode 下 tail latency 很差，优先怀疑：

- response path
- KV placement
- ejection / endpoint

而不是先怀疑“总带宽不够”。

## 本页结论

KV cache / decode memory path 的核心，不是把它看成普通 memory traffic，而是把它识别为 decode forward progress（前进保证）的关键依赖路径。  
只要这个路径不稳，NoC 就可能在链路并不满的情况下显著拖慢系统。
