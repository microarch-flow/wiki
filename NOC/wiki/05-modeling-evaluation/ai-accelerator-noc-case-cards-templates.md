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

- NoC（片上网络）论文
- AI accelerator（AI 加速器）interconnect（互连）论文
- routing（路由）/ QoS（服务质量）/ collective（集合通信）/ memory path 相关论文

推荐结构：

```md
# Paper Card: <title>

## Basic Info
- venue
- year
- authors
- link
- source links

## Problem
- 这篇论文在解决什么问题

## Proposed Idea
- 核心机制是什么

## NoC-Relevant Details
- topology（拓扑）
- routing
- flow control（流量控制）
- VC（虚通道）/ QoS
- endpoint（端点）/ memory assumptions

## What Is Public Fact

## What Is Inference

## Strengths

## Weaknesses / Assumptions

## What I Can Reuse

## What I Still Doubt

## Confidence

## Modeling-Safe Takeaway
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

## Sources

## What Is Public Fact

## What Is Inference

## Why This Design Probably Chose This NoC

## What To Compare Against

## Confidence

## What Can Be Safely Modeled
```

## 三：对比卡模板

适用于：

- flat mesh（扁平网格）vs hierarchical NoC（层次化片上网络）
- source routing（源路由）vs deterministic（确定性路由）
- software replication vs hardware multicast（硬件组播）

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
- 它靠什么机制保护 forward progress（前向推进）

如果只记录”用了 mesh（网格）/ 用了 DMA（直接内存访问）/ 用了 SRAM（静态随机存储）”，研究价值很低。

## 五：建议的案例组织方式

你后续可以按三层来组织：

- `paper-cards/`
- `architecture-case-cards/`
- `comparison-cards/`

这样后面无论做综述还是做架构判断，都更容易复用。

## 六：最值得优先收集哪类案例

对你当前主线，建议优先积累：

- AI tile-based accelerator（基于计算单元的 AI 加速器）case
- memory-centric inference case
- collective-heavy case
- hierarchical NoC case

## 七：一个很实用的记录原则

每张卡都补一句：

- “这件事对我的 simulator 或架构探索有什么直接启发？”

否则卡片容易变成信息摘抄，而不是判断工具。

## 本页结论

案例卡和论文卡模板的价值，不在于把资料收集得更漂亮，而在于把外部案例统一压缩成可比较、可迁移、可服务你自己建模工作的结构化资产。
