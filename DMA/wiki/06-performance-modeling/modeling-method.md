# 从抽象模型到系统诊断

上级：[06 性能建模与调优](./README.md)

相关：[DMA 与 NoC](../05-system-integration/dma-and-noc.md)、[AI 加速器里的 DMA](../07-workloads-case-studies/ai-accelerator-dma.md)、[NOC：建模层次（解析/事件/周期）](../../../NOC/wiki/07-evaluation-methodology/modeling-layers-analytical-event-cycle.md)

## 这页在回答什么问题

如果要建一个能解释 DMA 行为的模型，应该从哪里开始、按什么层次加细节；以及为什么一开始就做“全精度仿真”通常既慢又不解释问题。

## 模型最容易犯的两个错误

第一个错误是把一切都原封不动搬进模型。descriptor、AXI 通道、NoC path、row locality、completion、interrupt、cache visibility 全部显式建进去，结果模型既重又难调，而且你很快失去对主瓶颈的直觉。

第二个错误是反过来把 DMA 压成一个“固定带宽 + 固定延迟”的黑盒。这样模型虽然好跑，但你会立刻失去对 stall、tail latency、completion backlog 和 overlap 失败的解释能力。

有用的 DMA 模型必须站在这两者之间：只保留那些会改变性能形状和状态闭环的变量，把不会改变判断结构的实现细节折叠掉。

## 第一层：理想带宽模型

第一层只回答最粗的问题：理论上多久能搬完，哪条链路先打满。它通常只保留：

- 总字节数
- 端到端带宽上限
- 可能的重叠上界

这一层适合做上界估算，也适合快速判断某个方案是否在数量级上可行。但它几乎解释不了 stall，因为它没有 queue、没有 outstanding、没有 return path、也没有 completion。

## 第二层：事务与队列模型

第二层开始把 DMA 真正关键的执行结构放进去：

- descriptor / submit 成本
- queue 深度
- outstanding limit
- request / response 分离
- completion 可见性延迟

这层模型已经足以解释大量真实性能损失。你会开始看到为什么带宽看着够但 steady-state 起不来，为什么 queue 太浅时 latency hiding 做不起来，为什么 completion 回收慢会拖住下一轮。

## 第三层：系统耦合模型

第三层再把 DMA 放回真实系统资源：

- NoC 注入与回压
- local SRAM bank / port
- DDR / HBM row locality 与 return latency 分布
- 多流冲突与优先级
- software-visible completion 与 consumer-ready 边界

只有到这一层，你才有能力解释“为什么这代芯片的 DMA 在另一个 workload 上突然变差”“为什么 single-stream 好，多 stream 坏”“为什么平均值没问题，尾巴烂掉”。

## 按问题选层次，而不是按信仰选层次

如果问题只是早期方案筛选，第一层就够；如果你已经看到 queue 深度或 outstanding 改动会显著影响结果，第二层才是正确起点；如果你面对的是 AI 供数断流、NoC 热点、HBM 行为差异、completion 长尾，那就必须上第三层。

更直接地说，模型层次不是越高越高级，而是越贴近你当前要解释的问题越有价值。

## 如何把 05 章的系统抽象接进模型

这一页同样适合显式使用 `Resource / Topology / Interaction / Capability`：

- `Resource`：queue、inflight table、SRAM port、NoC ejection、MC bank/port、completion queue
- `Topology`：descriptor path、data path、return path、completion path 的共享点
- `Interaction`：submit、issue、response、writeback、completion visible、consumer ready
- `Capability`：queue depth、outstanding depth、burst policy、priority、moderation、buffer count

这套抽象的价值在于，它能让模型既保留因果结构，又不被具体 RTL 细节淹没。

## 常见误解

常见误解：`越精细的模型一定越好`。实际上如果你解释不了结果，精细只是在制造复杂度。

常见误解：`理想带宽模型没价值`。实际上它是最便宜的上界和 sanity check，没有它你很难知道后续损失是否合理。

常见误解：`只要有 NoC/DDR，就必须从系统全模型开始`。实际上很多问题在事务与队列层就已经能解释清楚。

## 一句话理解

对 DMA 建模，关键不是先做最复杂，而是先做最小但能稳定解释主瓶颈的分层模型。

## 建模启示

这页本身就是建模启示。最实用的做法是把模型显式分成三级，并允许逐层启用状态。

```text
L1 upper-bound:
  bytes, bw_limit

L2 queue-transaction:
  submit_q, outstanding, resp_latency, completion_delay

L3 system-coupled:
  noc_path, sram_ports, row_state, multi_stream_conflict
```

在这三层里，L1 更偏 `Capability` 上界，L2 更偏 `Interaction` 闭环，L3 则必须把 `Resource` 和 `Topology` 拉进来。若模型跨不过这种层次划分，后续调优会很难有条理。
