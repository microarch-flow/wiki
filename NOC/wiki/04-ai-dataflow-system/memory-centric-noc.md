# Memory-Centric NoC

上级：[AI Dataflow 系统视角](./README.md)

相关：[NI / DMA / 存储接口](./ni-dma-memory-interface.md)、[Attention Decode Case Study](./workload-attention-decode-case-study.md)

## 为什么要单独看 memory-centric NoC

不是所有 NoC 问题都由 tile-to-tile stream 主导。  
在很多 AI 推理场景里，尤其是：

- decode（逐token解码）
- KV cache（键值缓存）主导路径
- 高并发 DMA（直接内存访问）
- memory response 较敏感的 pipeline

系统更像是被 memory path 驱动，而不是被纯计算流驱动。

## 什么叫 memory-centric

不是说 NoC 只连 memory，而是说系统吞吐、尾延迟和 stall 的主因更集中在：

- HBM（高带宽存储器）/ memory controller 端口
- DMA request / response
- local SRAM（本地静态存储）refill / eviction（回填/驱逐）
- read response return path

这种情况下，NoC 的主要任务不是“搬运大块数据”，而是保证 memory 相关流量不过早放大成系统 stall。

## 典型路径

常见 memory-centric 事务链条包括：

- tile（计算单元）-> read request -> NoC -> memory port
- memory response -> NoC -> tile / DMA / SRAM
- spill / refill 流量
- KV cache read / update 路径

这里尤其要注意：

- request 慢不一定致命
- response 慢往往更致命

因为 response 常常处在 compute 是否能继续前进的关键路径上。

## 为什么 response path 比 request path 更危险

request 往往只是发起动作。  
response 则通常意味着：

- tile 在等数据
- DMA 在等完成
- barrier（同步屏障）或下游 stage 在等依赖满足

所以如果 response 被 bulk traffic 压住，系统即使总带宽看起来还行，也可能明显变慢。

## 这类 NoC 最怕什么

- request / response 共用资源池
- response 与 bulk DMA 混跑且无优先级
- HBM 端口位置导致长路径集中
- ejection（弹出）/ SRAM 写入口太弱
- KV cache placement（放置策略）把热点压在少数 memory node 附近

## HBM / memory port placement 为什么关键

同一套 router 参数，在不同 memory port placement 下可能出现完全不同的结果：

- 某些链路成为必经主干
- 某些 cluster 离 memory 端过远
- 多个高频 reader 共享同一侧端口

因此 memory placement 不是附属参数，而是 topology 评估的一部分。

## decode 场景为什么特别容易走向 memory-centric

decode 通常具有：

- 小 batch
- step latency（单步延迟）敏感
- KV cache 访问频繁
- 关键返回路径短而急

这意味着：

- 不需要非常高的总带宽，也可能被 response path 卡住
- 小消息、关键消息比 bulk path 更重要

## 在 simulator 里怎么建

第一版至少要有：

- request class
- response class
- memory port service rate
- DMA outstanding request（未完成请求）限制
- destination ejection / SRAM 写入口限制

如果没有这些，模型会高估 memory-centric 场景下的 NoC 表现。

## 你至少要比较的几件事

- request / response 是否分离
- response 是否有更高优先级
- memory port 放置位置变化的影响
- KV cache placement 对热点的影响
- decode 与 prefill（预填充）对同一 NoC 的敏感性差异

## 常见 stall 类型

- `NO_CREDIT`
- `EJECTION_BLOCKED`
- `WAITING_FOR_OTHER_STREAM`
- `SWITCH_CONFLICT`

这类场景里，`EJECTION_BLOCKED` 和 `WAITING_FOR_OTHER_STREAM` 尤其容易被低估。

## 一个高价值实验

同一 decode-like trace，比下面两组：

- request / response 同优先级同资源池
- response 高优先级或单独 class

观察：

- tail latency（尾部延迟）
- response latency
- tile utilization（计算单元利用率）
- workload completion time

## 本页结论

memory-centric NoC 的核心不是再造一套独立网络，而是识别”系统是不是已经由 memory path 主导”，并据此重新排序你对 QoS（服务质量）、response isolation（响应隔离）、memory placement 和 ejection 能力的关注优先级。
