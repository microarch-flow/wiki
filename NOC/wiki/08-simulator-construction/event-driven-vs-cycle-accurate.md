# Event Driven Vs Cycle Accurate

上级：[08 Simulator Construction](./README.md)

相关：[Modeling Layers Analytical Event Cycle](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)、[Verification And Calibration](./verification-and-calibration.md)

## 这页在回答什么问题

这页回答：NoC simulator 应该做成 event-driven 还是 cycle-accurate，这两种路线分别适合什么问题，第一版该怎么取舍。

## 先把问题问对

真正的问题通常不是“哪种更高级”，而是：

- 当前要解释的现象是否依赖 per-cycle 资源竞争
- 是否需要精确表达到达次序和 backpressure 传播
- 是否更看重速度，还是更看重微观可解释性

如果问题本身不要求细粒度时序，过早进入 cycle-accurate 往往只是拖慢开发。

## event-driven 的优势

event-driven 更适合：

- flow / phase 级问题
- request / response 粗粒度时序
- 快速参数探索

优点：

- 状态较少
- 运行更快
- 更容易承载大批量 sweep

局限：

- 很难自然表达细粒度 VC / credit / switch 冲突
- 对 tail latency 和 stall taxonomy 的解释力有限

## cycle-accurate 的优势

cycle-accurate 更适合：

- credit 回传
- wormhole path 占用
- ejection blocked
- class / VC / arbitration 的真实交互

优点：

- 可以稳定解释细粒度 stall
- 对 backpressure 链更有解释力

代价：

- 实现复杂度更高
- 性能更低
- 更容易因为状态更新顺序出错

## 对 AI NoC 的现实建议

对 AI NoC，一个务实的路线通常不是二选一，而是分层共存：

- 上层：event-driven / flow-level 做 trace 和 phase 分析
- 下层：cycle/flit-level 解释关键场景和热点

这样可以同时得到：

- 足够快的探索速度
- 足够强的现象解释力

## 第一版为什么常常还是建议按周期推进

因为一旦你想稳定回答下面这些问题：

- `NO_CREDIT` 到底是不是主因
- ejection blocked 怎样传播回 source
- QoS / priority 是否真的在冲突点改变结果

就很难绕开明确的 per-cycle 状态推进。

所以即使整体工作流有 event-driven 层，第一版核心 NoC 内核通常仍然值得按 cycle/flit 组织。

## 什么时候 event-driven 就够

如果当前只在回答：

- topology / placement 一阶差异
- workload phase overlap
- HBM port 大致是否过热

那 event-driven 层可能已经够了。

## 一句话理解

event-driven 擅长快，cycle-accurate 擅长解释细节；AI NoC 常常需要两层并存，而不是盲目二选一。

## 建模启示

实现上建议尽量把：

- traffic source / trace engine
- NoC core timing engine

解耦。

这样未来可以：

- 用同一批 trace 驱动不同层级模型
- 用 event 层筛选，再用 cycle 层深挖

这会显著提高 simulator 体系的可扩展性。
