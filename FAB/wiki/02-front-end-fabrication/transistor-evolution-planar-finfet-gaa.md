# 器件演化:Planar -> FinFET -> GAAFET

上级:[前道工艺](./README.md)
相关:[掺杂与离子注入:让硅变成器件](./doping-and-ion-implantation.md), [工艺节点演化与 PPA 取舍](./process-nodes-and-ppa-tradeoffs.md), [Design Rule 和 PDK:架构师与工艺的接口](./design-rule-and-pdk.md)

## 这页在回答什么问题

为什么 transistor 从 planar 演化到 FinFET，再走向 GAAFET/nanosheet。核心不是器件物理推导，而是理解 gate control 如何决定 scaling、功耗、频率和设计规则。

## 为什么 planar 走到极限

Planar MOSFET 的 gate 在沟道上方控制电流。尺寸较大时，这种控制足够有效；channel 缩短后，source/drain 对 channel 的影响增强，gate 对电流的控制变弱，短沟道效应、漏电和阈值控制问题变严重。

如果继续只做平面缩小，架构师希望获得的密度和能效会被漏电、变异性和电压限制吃掉。器件结构演化的目标，是在更短 channel 下恢复 gate 对 channel 的控制。

## FinFET: 把 channel 竖起来

FinFET 把 channel 做成竖起的 fin，让 gate 从多个侧面包住 channel。相比 planar，FinFET 提供更好的 electrostatic control，使先进节点能够继续降低尺寸和电压，同时控制漏电。

FinFET 对设计也有代价。fin 数量离散化后，transistor 宽度不再像 planar 那样连续可调，标准单元设计、drive strength、cell height 和 layout 规则都会更受限制。架构师看到的是库选择更离散、cell 结构更规则、routing 约束更强。

## GAAFET: 进一步包围 channel

GAAFET，也常以 nanosheet/nanoribbon 形态出现，让 gate 从四周包围 channel，目标是在更小节点继续增强 gate control。相比 FinFET，它提供更强的 electrostatic control，并允许通过 nanosheet 宽度调节 drive strength。

代价是制造复杂度上升。多层 nanosheet 的形成、释放、栅极包覆、寄生控制和变异性管理都更难。对架构师而言，GAA 不是“自动更快更省电”，而是给未来节点继续 scaling 提供器件基础，同时带来节点成熟度、成本和设计规则风险。

## 结构对比

```text
Planar:
  gate
  ----
  flat channel

FinFET:
      gate wraps sides
     /---\
    | fin |
     \---/

GAAFET / nanosheet:
  gate surrounds stacked sheets
   [ sheet ]
   [ sheet ]
   [ sheet ]
```

| 器件 | 主要收益 | 主要代价 | 架构侧表现 |
| --- | --- | --- | --- |
| Planar | 设计灵活、成熟 | 短沟道下漏电和控制变差 | 成熟节点、模拟/I/O 友好 |
| FinFET | 更强 gate control、延续 scaling | fin 离散、layout 规则更强 | 先进逻辑主力、库选择更规则 |
| GAAFET | 更强控制、更适合后续节点 | 制造复杂、成熟度爬坡 | 更先进节点的 PPA 潜力与风险并存 |

## 对 SRAM 和模拟的影响

器件演化并不会让所有模块等比例受益。逻辑标准单元可以从更强器件和更密 layout 中获益，但 SRAM bitcell 受稳定性、Vmin、读写 margin 和良率限制；模拟/I/O 受电压、器件模型、噪声和可靠性限制。先进器件结构越复杂，这些非逻辑模块的迁移越需要单独评估。

这也是为什么 SoC 不会简单把所有功能都推到最先进节点。compute logic 可能值得上先进 GAA 节点，I/O、analog 或部分 cache 宏未必获得同等收益。

## 常见误解

常见误解是“GAAFET 比 FinFET 更先进，所以所有设计都应迁移”。实际节点选择取决于 PPA 收益、IP 成熟度、成本、良率和产品周期。器件更先进不代表整颗芯片的所有模块都收益最大。

另一个误解是“transistor 变快，芯片就同比变快”。实际系统频率还受 BEOL wire delay、clock、SRAM、IR drop、thermal 和封装约束限制。器件演化只是 PPA 的一部分。

## 一句话理解

Planar、FinFET、GAAFET 的主线是不断增强 gate 对 channel 的控制，以换取更小尺寸下可用的功耗、频率和漏电空间。

## 架构师启示

如果我评估从 FinFET 节点迁移到 GAA 节点，不能只拿 logic density 做面积缩放。需要分别看 compute logic、SRAM、NoC、PHY、analog、I/O 和电源网络的收益。若系统瓶颈是 HBM 带宽或封装热，而不是 logic density，GAA 带来的收益可能小于封装或内存系统优化。

一个具体例子：大面积 SRAM scratchpad 在先进节点上可能面积收益低于逻辑，Vmin 还更敏感。此时架构上也许应减少片上 SRAM 过度堆叠，转向更高效的数据复用、HBM 带宽或分层 memory，而不是假设 SRAM 会随 logic 完美缩放。
