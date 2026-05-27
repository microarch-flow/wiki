# 掺杂与离子注入:让硅变成器件

上级:[前道工艺](./README.md)
相关:[前道工艺的整体节奏:FEOL/MOL/BEOL](./process-flow-overview.md), [器件演化:Planar -> FinFET -> GAAFET](./transistor-evolution-planar-finfet-gaa.md), [工艺节点演化与 PPA 取舍](./process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

为什么 transistor 不是在硅上“画出一个开关”，而是通过材料、电荷和几何结构共同形成可控器件。掺杂与离子注入的重点，是理解电性控制如何影响阈值、电压、漏电、变异性和良率。

## 掺杂解决什么问题

纯硅本身不是架构师想象中的理想开关材料。要形成 NMOS/PMOS、source/drain、well、channel 和阈值控制，需要在特定区域引入受控杂质，让局部材料呈现不同电学行为。掺杂把“硅片”变成能被 gate 控制的器件区域。

离子注入是常见实现方式：把特定离子以受控能量和剂量打入硅中，再通过热处理激活和修复晶格损伤。架构师不需要掌握剂量 recipe，但应理解剂量、深度、横向扩散和激活都会影响器件参数。

## 掺杂如何影响 PPA

| 电性结果 | 架构侧表现 | 风险 |
| --- | --- | --- |
| 阈值电压变化 | high-Vt / low-Vt cell 选择 | 漏电与速度 trade-off |
| 漏电控制 | standby power、power gating 收益 | 移动/边缘场景待机功耗 |
| source/drain 电阻 | cell delay、drive strength | 高频路径和库选择 |
| 随机变异 | timing margin、Vmin、SRAM stability | 低电压运行和良率 |
| 热处理预算 | 与后续材料和应力工程耦合 | 工艺集成窗口 |

这解释了为什么同一节点会提供不同 Vt library、不同 SRAM compiler 和不同电压/频率建议。架构师看到的是库选项；工艺侧背后是器件结构、掺杂、应力和变异性控制。

## 为什么先进节点更难

随着器件尺寸缩小，少量掺杂原子的位置和数量波动都可能对局部电性产生更大影响。短沟道效应、随机 dopant fluctuation、界面质量和寄生电阻会让简单缩小失去可控性。这也是器件结构从 planar 走向 FinFET 和 GAAFET 的原因之一：需要用更强 gate control 来减少对传统平面掺杂调控的依赖。

低电压运行尤其敏感。AI 加速器和移动 SoC 希望降低能耗，但 Vmin 不只由逻辑门延迟决定，也受 SRAM stability、器件变异和工艺角影响。若变异性过大，模型里的低电压高能效点可能在实际 silicon 上无法稳定量产。

## 常见误解

常见误解是“掺杂只是制造 NMOS/PMOS 的基础步骤，和架构没关系”。实际掺杂和器件电性决定 Vt、漏电、速度、变异性和 Vmin，这些参数会直接进入库、SRAM、功耗模型和 binning。

另一个误解是“同一个节点只有一个性能点”。实际产品会在不同 Vt cell、不同 voltage corner、不同 bin 和不同 leakage target 之间选择。架构师定义功耗和频率目标时，已经在选择器件电性 trade-off。

## 一句话理解

掺杂与离子注入把硅局部调成可控电性区域，它们通过阈值、电阻、漏电和变异性影响节点的可用 PPA 空间。

## 架构师启示

如果我想用更低电压运行 NPU 阵列来追求能效，不能只看标准单元在 typical corner 的能耗。SRAM Vmin、低 Vt cell 漏电、工艺角和随机变异会决定低电压点是否能成为量产规格。

一个具体决策是：高频控制路径可能需要 low-Vt cell 提速，但大规模 always-on SRAM 和控制逻辑可能要用 higher-Vt 降漏电。架构模型如果只有单一 delay/power 标量，会错过这种库级 trade-off。
