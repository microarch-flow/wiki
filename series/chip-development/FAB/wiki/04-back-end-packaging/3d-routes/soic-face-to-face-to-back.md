# SoIC:F2F/F2B/CoW/WoW 的关系

上级:[3D 路线](README.md)
相关:[Wafer-to-Wafer vs Die-to-Wafer](w2w-vs-d2w.md), [Micro-bump vs Hybrid Bonding](micro-bump-vs-hybrid-bonding.md), [3DIC:为什么需要垂直堆叠](3dic-fundamentals.md)

## 这页在回答什么问题

SoIC 语境里 F2F、F2B、CoW、WoW 经常一起出现，但它们属于不同分类维度。本页把 die 朝向和制造组织拆开，避免概念混用。

## 两组概念

| 概念组 | 回答的问题 |
| --- | --- |
| Face-to-Face / Face-to-Back | 上下 die 的连接面如何相对摆放 |
| CoW / WoW | 制造时是 die 贴 wafer，还是 wafer 贴 wafer |

Face-to-Face/F2F 与 Face-to-Back/F2B 是结构拓扑；CoW/WoW 是制造组织。它们不是同义词，也不是互斥层级。

## 什么是 face

在芯片语境里，face 可以理解为带有主要器件层、BEOL 金属层和主要连接界面的那一面。讨论 face-to-face 或 face-to-back，就是讨论上下两颗 die 的主要连接面如何相对。

## Face-to-Face

Face-to-Face 表示两颗 die 的主要连接面彼此相对，高密度连接发生在两个正面之间。

```text
die A face
   ||
die B face
```

它的直觉优势是互连短、连接密度潜力高，适合追求极限带宽和低互连功耗。代价是供电、散热和后续引出路径会更难组织。

## Face-to-Back

Face-to-Back 表示一颗 die 的主要连接面朝向另一颗 die 的背面。

```text
die A face
   ||
die B back
```

这种结构往往需要 TSV、backside routing 或其他背面引出能力来完成连接和封装接入。它在后续系统级封装衔接上更有组织空间。

## CoW 与 WoW

CoW 是 chip-on-wafer，对应 D2W 思路：底层保持 wafer，顶层 die 先切割、筛选，再贴到 wafer 上。它适合异构、高价值 die 和 KGD 控制。

WoW 是 wafer-on-wafer，对应 W2W 思路：上下 wafer 整片键合。它适合同尺寸、规则阵列、高良率节点。

## 组合关系

```text
orientation dimension:
  F2F or F2B

manufacturing organization dimension:
  CoW or WoW
```

这两个维度可以交叉组合。判断一个 3D 堆叠结构时，先问朝向，再问制造组织，最后再问使用 micro-bump 还是 hybrid bonding。

## 为什么这个区分重要

如果把 F2B 当成 CoW，把 WoW 当成 F2F，后续分析会错位。朝向影响热、供电、信号引出和 TSV 需求；制造组织影响 KGD、良率、吞吐和异构灵活性。两者共同决定 3DIC 的可制造性。

## 一句话理解

F2F/F2B 讲 die 怎么摆，CoW/WoW 讲制造时怎么组织；它们是两个正交维度。

## 架构师启示

架构师评估 SoIC-style 堆叠时，应把问题拆成三步：朝向是否支持目标互连和散热，制造组织是否支持 KGD 和异构，连接工艺是否满足 pitch 与功耗目标。三个问题任意一个不成立，平台名本身都不能保证方案成立。
