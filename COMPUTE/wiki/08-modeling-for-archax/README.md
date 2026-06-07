# 08 · 面向 archax 的建模

前七章是 COMPUTE 知识本身,每篇结尾有通用仿真抽象的"建模启示"。本章是**从知识到工具的转换层**:把那些散落的结论汇总成 7 条,并映射到 archax 的四元抽象。这是全域唯一显式使用 archax 术语(Resource/Topology/Interaction/Capability、Execution IR、M1/M2/S1)的章节。

## 篇目

1. **[面向 archax 的建模启示:把 COMPUTE 主线翻译成可建模量](./modeling-insights.md)**
   7 条建模启示(对应 Pope 讲座文末 7 条)+ 四元抽象映射表。核心:计算/通信比做成 Execution IR 一等派生量,任意粒度可求值;其余 6 条是它在 Capability/microarch/Interaction/Topology 各层的落点。

## 本章在主线上的位置

本章把[主线](../01-overview/compute-communication-ratio.md)从"知识主线"转成"建模主线":比值即 Execution IR 的一等派生量。COMPUTE 域到此闭环——从一个门的 p×q 到整片芯片的跨单元带宽,同一比值贯穿,最终成为 archax 里可审计、任意粒度可求值的物理量。

## 读法

建议先通读前七章建立知识,再读本章把知识接到工具。每条启示都回指其 COMPUTE 来源篇,可双向对照:正文篇讲"为什么硬件这样设计",本章讲"这个设计如何进仿真模型"。
