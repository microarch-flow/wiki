# Architecture Exploration Loop

上级：[07 Evaluation Methodology](./README.md)

相关：[Metrics Latency Throughput Saturation](./metrics-latency-throughput-saturation.md)、[Case Card Template](./case-card-template.md)

## 这页在回答什么问题

这页回答：一轮 NoC architecture exploration 应该怎样组织成可复用的闭环，而不是每次都临时扫一堆参数、最后得不到稳定结论。

## 目标不是“找最优参数”

更现实的目标通常是：

- 快速排除明显不合适的方向
- 找出一阶敏感参数
- 识别设计 trade-off 的转折点
- 形成下一轮更细模型需要验证的假设

这比一开始就声称“找到最终最优架构”更可靠。

## 推荐闭环

一个稳定的探索闭环通常是：

1. 选 baseline
2. 定目标 workload / trace
3. 选变量与固定项
4. 跑 sweep
5. 做 stall / hotspot / workload-level 归因
6. 提炼结论与下一轮假设

这个闭环的关键是：每一步都必须可复用，而不是一次性分析。

## baseline 应该怎么选

baseline 的价值是让比较有锚点。

对 NoC，baseline 通常应尽量：

- 简单
- 可解释
- 已知在某些 workload 下可工作

例如：

- 4x4 mesh + DOR
- 2 VC
- 基本 control/data 分离

如果 baseline 本身就复杂难解释，后续 sweep 会非常混乱。

## sweep 不要所有变量一起动

推荐按组扫描：

- topology / hierarchy / memory port placement
- link width / buffer depth / VC count
- DMA outstanding / burst / endpoint rate
- placement / traffic class / route family

一次只让一组成为主要自变量，才能看出因果方向。

## 结果不只看“更快了多少”

每轮 sweep 至少应回答四件事：

- 变好的是 average、tail 还是 workload completion
- 热点有没有转移
- stall 主因有没有变化
- 代价是什么：面积、功耗、复杂度、可验证性

否则你只是看到一个数字变化，没看见它为什么变化、值不值得。

## 什么时候该停止当前层探索

当一轮探索已经能稳定说明：

- 哪个方向明显不行
- 哪个方向的收益已到边际递减
- 哪个问题当前模型解释不了

就该停止本层 sweep，进入：

- 更细模型验证
- 更换 workload
- 或换设计问题

这比无穷无尽地加参数更高效。

## 常见误区

- sweep 太多变量同时动
- 没有 baseline
- 只看平均值
- 没有“下一轮假设”输出

更好的做法是让每轮探索都有明确产物：

- 保留方案
- 淘汰方案
- 未决问题
- 下一层模型需要回答的问题

## 一句话理解

architecture exploration 的价值不在于多跑实验，而在于把每轮实验都变成一个可累积的筛选和归因闭环。

## 建模启示

建议给每轮实验固定模板：

- question
- baseline
- variables
- fixed assumptions
- metrics
- main findings
- unresolved issues
- next action

这会让探索过程更像工程资产，而不是零散 notebook。
