# Implementation Roadmap

上级：[08 Simulator Construction](./README.md)

相关：[Simulator Design Spec](./simulator-design-spec.md)、[Verification And Calibration](./verification-and-calibration.md)

## 这页在回答什么问题

这页回答：如果现在开始真正写 simulator，第一版最小实现应该按什么顺序推进，每一步的验收标准是什么。

## 核心原则

路线图的目标不是尽快把功能堆满，而是：

- 每一步都能运行
- 每一步都能验证
- 每一步都给下一步打基础

这样 simulator 会稳步长大，而不是中途变成一团难以 debug 的状态机。

## Phase 0: 固定边界

先明确第一版不做什么：

- 复杂 adaptive routing
- bit-accurate header encoding
- 物理电气细节
- coherence protocol

只做：

- flit-level
- wormhole
- credit-based flow control
- 至少一种 topology
- 至少一种 workload trace

## Phase 1: 最小传输骨架

先实现：

- Packet / Flit
- Topology
- Link
- 固定 deterministic routing

验收标准：

- packet 能沿固定路径逐跳到达
- 3-hop 单 packet 延迟与手算一致

## Phase 2: Buffer 与 Credit

加入：

- input buffer
- credit counter
- injection / ejection queue

验收标准：

- buffer 满会停发
- credit 不会提前返回
- destination FIFO 满时 backpressure 能传回 source

## Phase 3: Wormhole Path State

加入：

- header 建路
- body 跟随
- tail 释放路径和 VC 状态

验收标准：

- packet 不再被简化成独立 flit
- tail 之前资源不会被错误复用

## Phase 4: Allocation And Contention

加入：

- route compute
- VC allocation
- switch arbitration

验收标准：

- 两个输入抢一个输出时行为稳定
- 能区分 `NO_CREDIT` 和 `SWITCH_CONFLICT`

## Phase 5: Traffic Class

加入：

- CONTROL
- MEMORY_REQUEST
- MEMORY_RESPONSE
- STREAM
- BULK_DMA

验收标准：

- per-class latency / stall 可统计
- control / response 不会在最简单场景里被 bulk 完全淹没

## Phase 6: Workload Trace

先接入两类：

- GEMM-like
- decode-like

验收标准：

- 能跑 synthetic 之外的 AI-like 输入
- workload completion、tile utilization 可输出

## Phase 7: Stats And Experiment Harness

加入：

- per-link utilization
- latency distribution
- stall breakdown
- workload completion
- structured result output

验收标准：

- 一组 sweep 能自动产出结构化结果

## Phase 8: 对比实验

优先跑：

1. flat mesh vs hierarchy
2. buffer depth sweep
3. packet / flit size sweep
4. QoS on/off
5. placement / memory-port variation

验收标准：

- 能稳定得到一阶架构洞察
- case card 能完整记录结果和边界

## 一句话理解

最小实现路线的关键，不是先做最全，而是先做一条每一步都可验证、可解释、可累积的主线。

## 建模启示

建议每个 phase 都伴随：

- minimal unit test
- one sanity workload
- one structured output sample

这样你的 simulator 会自然形成“实现 + 验证 + 实验”三位一体的工程骨架。
