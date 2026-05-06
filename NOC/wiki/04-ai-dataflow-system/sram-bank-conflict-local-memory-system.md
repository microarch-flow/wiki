# SRAM Bank Conflict / Local Memory System

上级：[AI Dataflow 系统视角](./README.md)

相关：[NI / DMA / 存储接口](./ni-dma-memory-interface.md)、[Hierarchical NoC 深化](../03-topology-routing/hierarchical-noc-deep-dive.md)

## 为什么这页重要

很多 NoC 分析会默认端点“只要数据到了就能消费”。  
但真实 AI accelerator 里，tile、cluster SRAM、本地 scratchpad 往往有明确的 bank、port 和仲裁限制。

结果是：

- NoC 看起来没满
- 但 ejection 或本地读写已经堵住
- backpressure 最终又表现成 NoC stall

## Local Memory System 通常包含什么

在 tile 或 cluster 层，常见对象包括：

- local SRAM bank
- read / write port
- address generation / access scheduler
- load-store queue 或 scratchpad queue
- 与 DMA / compute / NoC 共享的访问入口

这些对象共同决定“本地能否及时吃下 NoC 送来的数据”。

## 什么是 bank conflict

当多个访问在同一时刻命中同一个 SRAM bank 或共享端口时，就会发生 bank conflict。

后果可能包括：

- 访问排队
- 读写互相等待
- ejection 变慢
- compute 等待数据

这本质上是局部 memory arbitration 问题，但会直接改变 NoC 观测到的 backpressure。

## 为什么 bank conflict 会被误判成 NoC 问题

因为从 router 视角看，表象常常只是：

- 下游 FIFO 不动
- credit 回不来
- source 被迫停发

但根因其实可能是：

- 本地 SRAM 正被 compute 占用
- write port 不够
- 多个 stream 同时写同一 bank

## 常见冲突来源

- compute 读和 NoC 写打架
- DMA refill 和 tile consume 打架
- 多个 ejection stream 同时落在相同 bank
- reduce / gather 结果集中写入单一局部区域

## 为什么 local memory system 对 hierarchical NoC 特别重要

hierarchical NoC 往往依赖：

- cluster 内共享 SRAM
- 局部复用
- 中间聚合

这会放大 local memory system 的重要性。  
如果 cluster SRAM 的 bank 组织设计不好，分层 NoC 的理论收益会被局部冲突吃掉。

## 在 simulator 里最少怎么建

第一版不一定要做 bit-accurate SRAM timing，但至少建议有：

- memory bank count
- 每 bank 每周期服务能力
- read / write 请求队列
- ejection 写入是否占 bank 资源

这样你至少能区分：

- 网络本体拥塞
- 局部 memory 争用

## 你至少要比较的实验

### 1. Bank 数量变化

比较：

- 少 bank
- 多 bank

观察：

- ejection blocked
- credit stall
- tile utilization

### 2. Compute / DMA / NoC 共用端口 vs 分离端口

观察：

- 局部冲突是否显著下降
- hierarchical NoC 收益是否变稳定

### 3. 数据落点映射策略

比较：

- 集中写入
- 分散写入

观察：

- bank hotspot
- reduce / gather 写回时延

## 最值得看的指标

- bank occupancy
- bank conflict count
- ejection blocked cycle
- local memory service latency
- 与 NoC stall 的关联

## 一个实用判断

如果你发现：

- link utilization 不高
- 但 credit stall 很高
- 且 ejection blocked 明显

优先检查 local memory system，而不是先改 NoC。

## 本页结论

SRAM bank conflict / local memory system 的关键意义，在于它把“端点是否真的能消费数据”这个问题显式化。  
很多看似 NoC 的瓶颈，最后其实是 local memory arbitration 没设计好。
