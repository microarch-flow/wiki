# Simulator Design Spec

上级：[08 Simulator Construction](./README.md)

相关：[Modeling Layers Analytical Event Cycle](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)、[Traffic Injection And Tracing](./traffic-injection-and-tracing.md)

## 这页在回答什么问题

这页回答：第一版 workload-driven NoC simulator 的功能边界、核心对象、时序规则和必须回答的问题应该怎样写成一份稳定规格。

## 目标边界

这份规格默认面向：

- workload-driven architecture exploration
- flit-level / wormhole
- credit-based flow control
- deterministic routing baseline
- 可扩展到 VC、class、hierarchy 和 AI-like trace

它不追求：

- RTL 等价
- bit-accurate header 编码
- 物理版图与时钟实现

也就是说，它的目标是解释和比较，不是签核。

## 第一版必须回答的问题

第一版 simulator 至少应能稳定回答：

- 哪些 link / port / endpoint 最先饱和
- stall 主要来自 credit、switch、ejection 还是 workload dependency
- topology、buffer、VC、placement、class policy 的相对差异
- NoC 是否真的影响到 tile utilization 和 workload completion

如果这些问题都答不了，simulator 就还没进入有效区间。

## 核心对象

规格层面建议固定这些一等对象：

- `Packet`
- `Flit`
- `Router`
- `Link`
- `Endpoint / NI`
- `Topology`
- `Routing policy`
- `Stats`

第一版不要让这些对象相互混叠。尤其不要把：

- link 状态塞进 router
- endpoint 行为塞进 traffic generator
- stall 统计散落在调试日志里

## 必须固定的时序语义

仿真器写乱的根因往往不是对象少，而是时间语义不清。

至少要先固定这些规则：

- flit 占用下游 buffer slot 时 credit 立即减少
- buffer slot 真正释放时 credit 才返回
- tail 释放 packet 占用的 path / VC
- packet 到达目的 router 不等于任务完成，还要经过 ejection / NI / local consumer
- 当周期的读状态和写状态边界要清楚

这几条如果不早定，后续结果会非常不稳定。

## 推荐的主循环语义

推荐统一为两阶段或双缓冲语义：

1. 收集本周期输入：arriving flit、returning credit、new injection event
2. 基于旧状态做分配、转发、ejection、credit generation，再写入新状态

核心目的是避免“同一周期既读又写同一状态”导致的隐式抢跑。

## traffic class 的最低要求

第一版至少建议固定一组 canonical class：

- `CONTROL`
- `MEMORY_REQUEST`
- `MEMORY_RESPONSE`
- `STREAM`
- `BULK_DMA`

哪怕第一版调度还不复杂，也应先把 class 作为稳定字段保留。因为后面很多 AI 场景结论都依赖这层分化。

## 输出接口

simulator 不应只吐一堆文本。至少应支持结构化输出：

- packet latency distribution
- per-link utilization
- per-class throughput
- per-node / per-class stall
- workload completion cycle

这样 sweep 和 case card 才能自动化。

## 第一版明确不做什么

建议在规格里直接写死第一版不做：

- 复杂 adaptive routing
- speculative pipeline
- full physical timing
- coherence protocol semantics

这能避免实现阶段不断失控。

## 一句话理解

simulator spec 的任务不是把未来功能都列满，而是把第一版的对象边界、时间规则和回答范围钉死。

## 建模启示

这份 spec 最好直接伴随三类附录：

- object definitions
- per-cycle state transition rules
- minimum validation scenarios

这样实现阶段才不会变成“靠记忆补规格”。
