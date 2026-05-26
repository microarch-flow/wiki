# 08 Simulator Construction

上级：[NOC Wiki](../README.md)

相关：[Evaluation Methodology](../07-evaluation-methodology/README.md)、[Router Pipeline Stages](../02-router-microarchitecture/router-pipeline-stages.md)

## 这页在回答什么问题

这一章回答：在已经明确指标、trace、建模层级和 stall taxonomy 之后，第一版 NoC simulator 到底该怎么设计、实现和验证。

这里的目标不是“做出工业级 RTL 替身”，而是做出一个：

- 边界清晰
- 时序规则一致
- 能解释现象
- 能支撑 architecture exploration

的工作负载驱动仿真器。

## 这一章的主线

这章主要解决五个问题：

- simulator 的边界和对象该怎么定
- event-driven 和 cycle-accurate 应该怎么取舍
- 核心状态和数据结构该怎么组织
- router pipeline 在代码里该怎么推进
- 怎样验证 simulator 至少没有把基础规则写错

## 为什么这一章必须放在方法论之后

如果没有前一章的契约，仿真器很容易写成：

- 指标口径随写随变
- trace schema 没有稳定输入边界
- stall reason 只剩日志，没有结构化统计
- 每个实验都要临时补代码

所以仿真器章节承接的是方法论，不是独立技能树。

## 第一版目标边界

这里默认的第一版目标是：

- flit-level
- wormhole
- credit-based flow control
- 至少一种 deterministic routing
- 至少基本支持 traffic class
- 能接 workload-derived trace

它不是：

- RTL timing signoff 工具
- 物理电气模型
- 完整 coherence 模拟器

## 读完这章后应该得到什么

读完后，你应该能回答：

- 第一个可用 simulator 的核心对象有哪些
- 全局 tick 应该怎样组织
- credit、VC、ejection、allocator 哪些状态必须显式保留
- 怎样从最小功能一路长到能跑 AI workload trace
- 怎样给 simulator 做最小但可信的验证闭环

## 一句话理解

好的 NoC simulator，不是功能最多的那个，而是对象边界、状态推进和验证规则最不含糊的那个。

## 建模启示

这一章对应的实现契约至少要固定：

- `object contract`：Packet / Flit / Router / Link / Endpoint / Stats
- `time contract`：每周期先读什么、再写什么、credit 何时返回
- `trace contract`：输入流如何进入注入队列
- `verification contract`：哪些最小场景必须和手算一致

这四个契约清楚，仿真器才会越长越稳，而不是越长越乱。
