# Case Card Template

上级：[07 Evaluation Methodology](./README.md)

相关：[Architecture Exploration Loop](./architecture-exploration-loop.md)、[From Workload To Traffic Trace](./from-workload-to-traffic-trace.md)

## 这页在回答什么问题

这页回答：如何把一次 NoC case study 或实验结果沉淀成可复用资产，而不是只留下一次性图表和印象。

## 为什么需要 case card

NoC 探索里最容易丢的是上下文。几周之后再回看，很常见的情况是：

- 还记得“某方案更好”
- 但不记得对什么 workload、更好在哪、为什么更好

case card 的作用，就是把一次实验压缩成最小但完整的决策记录。

## 推荐模板

```md
# Case Card

## Question
这次实验想回答什么问题？

## Workload
逻辑 workload 是什么？

## Placement / Memory Placement
放在哪里？有哪些关键映射假设？

## Traffic Abstraction
用了什么 trace / flow 抽象？保留了哪些 class？

## Model Layer
analytical / event / flit / cycle 哪一层？

## Baseline
对照方案是什么？

## Variables
扫了哪些参数？

## Metrics
看了哪些网络、端点、workload 指标？

## Findings
最重要的观察是什么？

## Root Cause
现象背后的主因是什么？

## Tradeoff
收益换来了什么代价？

## Limits
这次实验没覆盖什么？哪些结论不能外推？

## Next Step
下一轮最值得做什么？
```

## 为什么这个模板有用

它强迫你把一次实验说清楚四件事：

- 问题是什么
- 假设是什么
- 结果是什么
- 结果边界是什么

这会显著减少“图很多，但资产很少”的情况。

## 特别要避免漏掉的字段

最常被遗漏、但最关键的字段通常是：

- model layer
- placement / memory placement
- traffic abstraction
- limits

因为很多 NoC 结论恰恰最依赖这些上下文。

## 一句话理解

case card 的任务不是复述所有图，而是把一次实验最关键的问题、假设、结论和边界锁定下来。

## 建模启示

如果后续要批量管理 case study，建议让 case card 字段结构化，便于做：

- workload 维度索引
- topology 维度索引
- model-layer 维度索引
- finding / trade-off 回查

这样 case card 就不仅是笔记，而是探索知识库的最小单元。
