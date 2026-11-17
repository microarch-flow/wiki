# 从门电路到 AI 计算单元

<span class="micro-legacy-anchor" id="compute-域-wikiai-算力单元为何长成这样"></span>
<span class="micro-legacy-anchor" id="与其他域的接口"></span>


这是一条自底向上的阅读路线：从整数运算、选择网络与数据复用，走到流水线、芯片组织和实现成本。它保留原 COMPUTE 入口，不再承担整个微架构系列的分类职责。


<span class="micro-legacy-anchor" id="全域主线"></span>
<span class="micro-legacy-anchor" id="章节地图"></span>

## 主线与章节地图

| 步骤 | 入口 | 要回答的问题 |
| --- | --- | --- |
| 1 | [计算与供数](../02-analysis/problem-statement.md)、[指标边界](../02-analysis/compute-communication-ratio.md) | 工作量、流量和成本分别怎么量 |
| 2 | [运算数据通路](../../01-datapath/README.md) | 从门到 MAC，位宽和选择网络如何改变结构 |
| 3 | [并行执行与阵列](../../04-parallel-execution/README.md) | 通道、驻留和逐拍传递如何组织计算 |
| 4 | [流水线与时序](../../02-pipeline/README.md) | 采样、反馈、吞吐与反压如何约束推进 |
| 5 | [Cache 与 scratchpad](../../../storage/01-memory-hierarchy/02-access-paths/cache-vs-scratchpad.md) | 数据放在哪里，由谁管理 |
| 6 | [处理单元与片上组织](../../07-chip-organization/README.md) | 控制、计算、存储和互连如何组合 |
| 7 | [功耗与实现](../../09-power-implementation/README.md) | 功率、任务能量和可配置性怎样取舍 |
| 8 | [建模应用](../03-modeling/README.md) | 如何把这些机制变成事件与资源约束 |


<span class="micro-legacy-anchor" id="阅读路径"></span>
<span class="micro-legacy-anchor" id="自测"></span>

## 阅读顺序

1. [路线与专题边界](./taxonomy-and-roadmap.md)：选取入口并连接相邻系列。
2. [自测问题](./self-test-questions.md)：检查概念、迁移和架构判断。

## 资料来源与适用范围

这条路线起源于 [Reiner Pope 的 Chip design from the bottom up 访谈](https://www.dwarkesh.com/p/reiner-pope-2)（2026-05）。访谈用于提供问题线索；技术结论以各篇的一手资料和明确模型为依据。它不覆盖完整 CPU 控制、访存子系统或全部加速器类型。

更完整的机制地图和 CPU、GPU、NPU 阅读入口见[微架构首页](../../README.md)。
