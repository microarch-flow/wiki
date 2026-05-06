# Simulator 最小实现路线

上级：[建模与评估](./README.md)

相关：[Simulator 设计规格](./simulator-design-spec.md)、[检查清单](../06-reference/checklists.md)

## 这页解决什么问题

你已经有了知识框架，也有了 simulator 规格。  
接下来真正会卡住的问题通常是：

- 第一版到底先写什么
- 哪些模块必须先有
- 每一步做到什么程度就可以往下走

这页给的是最小可执行实现路线。

## Phase 0：固定边界

先明确第一版不做什么：

- 不做复杂 adaptive routing
- 不做 bit-accurate header encoding
- 不做物理时序细节
- 不做完整 coherence

只做：

- flit-level
- wormhole
- credit-based flow control
- 至少一种 topology
- 至少一种 workload trace

## Phase 1：最小拓扑与传输骨架

先实现：

- router node
- link
- packet / flit
- simple topology graph
- fixed routing

完成标准：

- packet 能沿固定路径逐跳走到终点
- 支持 header / body / tail

## Phase 2：input buffer 与 credit

加入：

- per-input buffer
- credit counter
- credit return
- injection / ejection queue

完成标准：

- buffer 满时发送方会停
- destination FIFO 满时反压能一路传回 source

## Phase 3：wormhole 资源占用

加入：

- header 建立通路
- body 跟随
- tail 释放资源

完成标准：

- packet 不再是独立 flit 随机走动
- 长 packet 会真实占用路径资源

## Phase 4：allocator

加入：

- RC
- VC allocation 或最小逻辑通路分配
- switch arbitration

完成标准：

- 可以区分 `NO_CREDIT` 和 `SWITCH_CONFLICT`
- 多 packet 共享输出时行为合理

## Phase 5：traffic class 与基本 QoS

加入：

- control
- memory_response
- stream
- bulk_dma

完成标准：

- control / response 不会被 bulk traffic 完全淹没
- 能统计不同 class 的 stall 与 latency

## Phase 6：workload trace

先加入 2 类：

- GEMM-like
- attention decode-like

完成标准：

- synthetic traffic 之外，能跑真实 AI-like 模式
- 能观察 compute-facing 指标变化

## Phase 7：统计与实验接口

加入：

- per-link utilization
- latency 分布
- stall breakdown
- tile utilization
- workload completion time

完成标准：

- 能输出一份完整实验报告

## Phase 8：结构对比实验

优先做这几组：

1. flat mesh vs hierarchical NoC
2. packet size / buffer depth 扫描
3. QoS on/off
4. forwarding on/off
5. memory port placement 变化

完成标准：

- 能得到稳定的一阶架构洞察

## 一个实用的代码落地顺序

如果你现在开始写代码，建议顺序是：

1. `packet_flit`
2. `topology`
3. `routing`
4. `router`
5. `link`
6. `endpoint`
7. `credit_flow`
8. `allocator`
9. `stats`
10. `traffic_generators`
11. `experiments`

## 每个阶段都要有小验收

例如：

- Phase 1：3-hop 单 packet 手算能对上
- Phase 2：buffer 满会停发
- Phase 3：tail 释放前资源不会被错误复用
- Phase 4：两 packet 抢同一输出时仲裁合理
- Phase 5：control 高优先级能改善 tail latency

## 最容易犯的路线错误

- 一开始就想实现完整多拓扑多协议
- 先写复杂 workload，再补基础 router 规则
- 没有统一统计接口就开始大扫参数
- 没有小验收点，导致模型越来越难 debug

## 当前阶段的成功标准

不是“做出工业级 NoC simulator”，而是：

- 能稳定跑通
- 能解释结果
- 能支持相对比较
- 能告诉你下一步该补哪类真实度

## 本页结论

最小实现路线的核心，不是尽快把所有功能堆完，而是先搭一条每一步都可验证、可解释、可继续扩展的实现主线。
