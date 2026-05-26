# Verification And Calibration

上级：[08 Simulator Construction](./README.md)

相关：[Stall Taxonomy And Attribution](../07-evaluation-methodology/stall-taxonomy-and-attribution.md)、[Case Card Template](../07-evaluation-methodology/case-card-template.md)

## 这页在回答什么问题

这页回答：第一版 NoC simulator 怎样验证“基础规则没写错”，以及怎样把结果校到至少不会明显离谱。

## verification 和 calibration 不是一回事

先要区分：

- `verification`：实现是否符合你定义的模型语义
- `calibration`：模型参数和趋势是否与更高保真参考或常识一致

第一版最优先的是 verification。没有规则正确性，calibration 没意义。

## 第一批必须手算对上的最小场景

至少建议有这些：

1. 单 packet 单链路 / 三跳延迟
2. buffer 满后 source 停发
3. tail 释放后后续 packet 才能复用路径
4. 两包抢同一输出时仲裁结果稳定
5. ejection queue 满后 backpressure 能一路传回

这些场景的价值在于：它们能最快暴露 credit、释放时机、状态更新顺序的错误。

## stall reason 也要被验证

不要只验证“包最终到了”，还要验证：

- 该慢的时候慢的是哪种原因

例如：

- 下游 buffer 满时应主要看到 `NO_CREDIT`
- 输出争抢时应主要看到 `SWITCH_CONFLICT`
- 目的端吃不动时应主要看到 `EJECTION_BLOCKED`

如果分类都不对，后续归因会整体失真。

## calibration 应该怎么做

第一版 calibration 不必追求工艺级绝对数值，更现实的目标是：

- 趋势对
- 拐点对
- 相对比较不离谱

典型参考可以是：

- 手算带宽 / hop 上界
- 已知拓扑常识
- 旧模型或更粗模型的趋势
- 小规模 sanity benchmark

## 建议的分层校准方式

可以按层校准：

- analytical vs event：大方向 throughput / hotspot 是否一致
- event vs flit：phase-level slowdown 是否方向一致
- flit vs cycle：stall / tail latency 是否量级一致

这样更容易定位问题到底出在：

- 抽象层次不够
- 还是实现本身有 bug

## 为什么 debug trace 仍然重要

即使有结构化 stats，第一版 simulator 仍建议支持可选的：

- flit move trace
- credit return trace
- ejection blocked trace

因为很多 timing bug 靠聚合统计不容易第一时间发现。

## 一句话理解

第一版 simulator 的验证重点，不是“和世界完全一致”，而是“规则语义稳定、最小场景手算可对、趋势不会明显错向”。

## 建模启示

建议把验证资产本身结构化：

- `unit_scenarios`
- `expected_behavior`
- `expected_stall_reason`
- `trend_checks`

这样验证就能成为 simulator 的持续约束，而不是开发早期做完一次就丢。
