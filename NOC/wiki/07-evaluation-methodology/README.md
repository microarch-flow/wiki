# 07 Evaluation Methodology

上级：[NOC Wiki](../README.md)

相关：[AI NOC Specifics](../06-ai-noc-specifics/README.md)、[Simulator Construction](../08-simulator-construction/README.md)

## 这页在回答什么问题

这一章回答：已经知道 NoC 应该长什么样、承载什么流量之后，应该怎样系统地评估它，而不是陷入“看几张利用率图再拍脑袋”的状态。

真正有用的 NoC 评估，不是多跑几个仿真，而是建立一条稳定的方法链：

- 用什么指标
- 指标对应哪一层模型
- workload 怎样转成 trace
- stall 怎样归因
- 参数探索怎样形成可复用结论

## 这一章的主线

这章把评估过程拆成五个问题：

- 我到底在优化什么指标
- 这些指标当前模型能不能可信地产出
- workload 如何变成 simulator 能消费的输入
- 性能下降时，根因是带宽、仲裁、端点还是系统依赖
- 参数 sweep 应该怎样形成架构决策，而不是形成一堆图

## 为什么这章必须独立存在

很多 NoC 项目失败，不是因为没写出 simulator，而是因为：

- 指标混乱
- trace 抽象不稳定
- 模型层级和问题层级不匹配
- 看到 tail latency 变差，却说不清究竟是谁导致的

所以方法论不是附录，而是仿真和架构探索的中轴。

## 读完这章后应该得到什么

读完后，你应该能回答：

- 为什么 average latency 不足以评价 AI NoC
- 为什么某些问题停在 analytical / event-level 就够，某些必须上 flit-level
- workload trace 至少要保留哪些信息
- stall taxonomy 如何把“系统变慢”拆成可行动的根因
- 一轮 architecture exploration 应该怎样组织 baseline、sweep 和结论

## 一句话理解

好的 NoC 评估方法，不是把 simulator 做得更复杂，而是让指标、模型、trace 和根因归因彼此对齐。

## 建模启示

这一章对应的方法框架至少要固定四件事：

- `metric contract`：每层模型能产出什么、不能产出什么
- `trace contract`：输入流量必须保留哪些字段
- `attribution contract`：每个 stall 和 slowdown 怎样归因
- `experiment contract`：baseline、变量、观察项、结论口径如何统一

没有这些契约，后面的 simulator 再精细，也很难持续产出稳定洞察。
