# AI Accelerator NoC Case Cards 与论文卡模板

上级：[建模与评估](./README.md)

相关：[实验模板与结果模板](./experiment-result-templates.md)、[AI Dataflow 系统视角](../04-ai-dataflow-system/README.md)

## 为什么这一层值得补

知识体系页帮助你建立框架。  
但如果你后续要长期研究 NoC，真正会沉淀判断力的往往是：

- 论文卡
- 架构案例卡
- 对比卡

没有模板，研究记录很容易越积越散。

## 一：论文卡模板

适用于：

- NoC 论文
- AI accelerator interconnect 论文
- routing / QoS / collective / memory path 相关论文

推荐结构：

```md
# Paper Card: <title>

## Basic Info
- venue
- year
- authors
- link

## Problem
- 这篇论文在解决什么问题

## Proposed Idea
- 核心机制是什么

## NoC-Relevant Details
- topology
- routing
- flow control
- VC / QoS
- endpoint / memory assumptions

## Strengths

## Weaknesses / Assumptions

## What I Can Reuse

## What I Still Doubt
```

## 二：架构案例卡模板

适用于：

- 某个 AI accelerator
- 某家公司公开架构
- 某篇系统论文里的完整芯片

推荐结构：

```md
# Case Card: <architecture>

## System Goal

## Compute Organization

## Memory Organization

## NoC / Interconnect Organization

## Main Traffic Types

## Likely Bottlenecks

## Why This Design Probably Chose This NoC

## What To Compare Against
```

## 三：对比卡模板

适用于：

- flat mesh vs hierarchical NoC
- source routing vs deterministic
- software replication vs hardware multicast

推荐结构：

```md
# Comparison Card: A vs B

## Same Conditions

## Main Difference

## Expected Gain

## Expected Cost

## Best-Case Workload

## Worst-Case Workload

## What Experiment Would Decide It
```

## 四：你记录案例时最该抓的不是“名词”，而是结构

每张卡最重要的是把下面几件事抓清：

- 它的主流量是什么
- 它假设的局部性是什么
- 它最怕的 bottleneck 是什么
- 它靠什么机制保护 forward progress

如果只记录“用了 mesh / 用了 DMA / 用了 SRAM”，研究价值很低。

## 五：建议的案例组织方式

你后续可以按三层来组织：

- `paper-cards/`
- `architecture-case-cards/`
- `comparison-cards/`

这样后面无论做综述还是做架构判断，都更容易复用。

## 六：最值得优先收集哪类案例

对你当前主线，建议优先积累：

- AI tile-based accelerator case
- memory-centric inference case
- collective-heavy case
- hierarchical NoC case

## 七：一个很实用的记录原则

每张卡都补一句：

- “这件事对我的 simulator 或架构探索有什么直接启发？”

否则卡片容易变成信息摘抄，而不是判断工具。

## 本页结论

案例卡和论文卡模板的价值，不在于把资料收集得更漂亮，而在于把外部案例统一压缩成可比较、可迁移、可服务你自己建模工作的结构化资产。
