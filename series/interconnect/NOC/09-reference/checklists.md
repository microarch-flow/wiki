# Checklists

上级：[09 Reference](./README.md)

相关：[Architecture Exploration Loop](../07-evaluation-methodology/architecture-exploration-loop.md)、[Implementation Roadmap](../08-simulator-construction/implementation-roadmap.md)

## 这页在回答什么问题

这页回答：在做 NoC 学习、分析、设计评估和 simulator 实现时，最容易漏掉哪些关键问题，应该怎样用 checklist 防止自己遗漏。

## 1. 读一章前的自检

开始分析或写文档前，先问自己：

- 我当前关心的是 topology、routing、system integration 还是 workload case？
- 我是否已经统一了这里要用的核心术语？
- 我是要回答结构问题，还是要回答时序 / stall 问题？

如果这三件事都没分清，说明还不该急着往下结论。

## 2. NoC 设计评估 checklist

评估一个设计方案时，至少检查：

- 主流量类型是什么
- 关键路径是 request、response、collective 还是 bulk stream
- 热点根因在 topology、placement、memory 还是 endpoint
- 是否需要 class 隔离
- 是否需要物理多网络
- 结论是否只在某类 workload 下成立

这是最常用的一张总表。

## 3. topology 选择 checklist

选 topology 前，至少确认：

- 流量局部性强不强
- 是否有明显多路径价值
- wire span / floorplan 是否允许
- memory port / cluster 放在哪里
- collective 模式是否频繁

如果没有把 workload 和物理约束带进来，topology 讨论通常没有实义。

## 4. routing / QoS checklist

考虑 routing 与 QoS 时，至少确认：

- 热点是静态还是动态
- deterministic 是否足够
- adaptive 是否真有路径可用
- control / response 是否需要保护
- low-priority 流是否存在 starvation 风险

这样能避免“看到热点就本能上 adaptive”的冲动。

## 5. memory-centric checklist

如果系统偏 memory-centric，至少确认：

- request / response 是否分开统计
- response 是否在关键路径上
- memory port placement 是否合理
- ejection / local SRAM 写入口是否够
- link 不忙但系统慢时，是否先检查 endpoint / memory

这是 decode 类问题最容易漏掉的一组。

## 6. workload-to-trace checklist

生成 trace 前，至少确认：

- placement 已定
- memory placement 已定
- traffic class 已定
- dependency 已保留
- packetization 假设已显式记录

没有这几项，trace 大概率不可复现。

## 7. simulator 实现 checklist

开始写代码前，至少确认：

- 第一版明确不做什么
- 对象边界是否固定
- credit 返回时机是否固定
- tail 释放时机是否固定
- stall reason 是否结构化
- 是否有最小单元测试计划

这张表的作用是防止 simulator 从第一天就失控。

## 8. 实验结果解读 checklist

看结果时，至少确认：

- 我看的是 avg 还是 tail
- network throughput 还是 workload throughput
- 主要 stall 类型是什么
- endpoint / memory 是否已排查
- 结论是否受模型层级限制

否则很容易把结果解释过头。

## 9. 写 case card 前 checklist

沉淀结果前，至少确认：

- 问题是否说清
- baseline 是否说清
- traffic abstraction 是否说清
- model layer 是否说清
- limits / next step 是否说清

这决定结果能不能复用。

## 10. 自测 checklist

如果你想确认自己是否已经能独立做一阶 NoC 分析，至少要能独立回答：

- 为什么 wormhole 会放大 backpressure
- 为什么 response path 往往比 request path 更敏感
- 为什么 link 不忙系统也可能慢
- 为什么 MoE 会逼出 fairness 问题
- 为什么 simulator 第一版不该急着追复杂 adaptive

## 一句话理解

checklist 的价值不是替你思考，而是防止你在复杂问题面前漏掉那些最容易被忽视、却最决定结论的环节。

## 建模启示

如果后面继续扩展 wiki，新的 checklist 最适合放在这里，而不是回流到正文中。这样主线保持简洁，参考层持续增强。
