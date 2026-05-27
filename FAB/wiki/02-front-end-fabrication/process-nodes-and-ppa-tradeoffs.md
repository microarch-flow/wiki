# 工艺节点演化与 PPA 取舍

上级:[前道工艺](./README.md)
相关:[为什么工艺红利在让位于封装红利](../01-overview/why-process-and-packaging-matter-now.md), [器件演化:Planar -> FinFET -> GAAFET](./transistor-evolution-planar-finfet-gaa.md), [SRAM 工艺缩放挑战](../../RAM/wiki/02-sram-foundations/sram-process-scaling-challenge.md)

## 这页在回答什么问题

工艺节点为什么会影响 PPA，但不能被简化成“数字越小越好”。架构师需要把节点看成 logic density、SRAM、BEOL、Vmin、IP、成本和良率成熟度的组合。

## 节点名代表平台代际

`7nm`、`5nm`、`3nm` 这类节点名不是某个单一物理尺寸。它们代表一代工艺平台，包括器件结构、标准单元库、金属栈、SRAM bitcell、设计规则、mask、PDK、IP 和良率成熟度。

公开数据可以作为量级锚点。TSMC 对 N3E 的公开描述给出相对 N5 约 20% speed improvement、超过 30% power saving、约 1.6x logic density 的量级。早期 N5 相对 N7 的公开沟通也常以约 15% speed、约 30% power、约 1.8x logic density 作为量级参考。这里的重点不是记数字，而是理解这些收益针对的是特定条件和特定结构，不会自动等比例作用到整颗 SoC。

## PPA 不同部分缩放不同

| 模块 | 节点缩放收益 | 常见限制 |
| --- | --- | --- |
| Logic standard cell | 密度、速度、能效收益明显 | routing、IR、库选择、物理收敛 |
| SRAM | 面积收益低于逻辑的风险更高 | bitcell stability、Vmin、良率 |
| Analog / PLL / SerDes | 收益不稳定 | 电压、噪声、可靠性、模型成熟度 |
| I/O PHY | 面积和功耗受接口标准限制 | ESD、pad、package、signal integrity |
| BEOL global wire | 不按 logic 密度理想缩放 | RC、via、repeaters、拥塞 |
| Embedded memory/NoC 系统 | 取决于布局和数据流 | macro placement、routing、thermal |

这张表解释了为什么 AI/HPC 芯片不会只靠节点推进。compute logic 可以受益于先进节点，但 SRAM 和外存接口不一定同等受益；当系统瓶颈转向 memory bandwidth、package power 或 thermal 时，封装和架构重组可能比继续缩节点更有效。

## 节点选择的 trade-off

更先进节点带来潜在 PPA 上限，也带来更高 mask 成本、设计复杂度、IP 迁移成本、EDA 收敛压力和良率爬坡风险。成熟节点在 logic density 上落后，但 IP、模拟、I/O、成本和量产风险可能更适合特定 die。

这就是 chiplet 有吸引力的原因之一：compute tile 使用先进节点，I/O die 或 analog die 使用成熟节点，memory stack 由专门 DRAM 工艺制造，再用封装集成。但这样会把单 die 工艺问题变成 package、D2D、KGD 和组合良率问题。

## PPA 影响表

| 节点变化 | 可能收益 | 可能代价 | 架构师问题 |
| --- | --- | --- | --- |
| 更密 logic | 更多 compute/control per area | routing 和 PDN 压力上升 | compute 是否真是瓶颈 |
| 更低能耗 | 同性能功耗下降 | 低电压受 Vmin/variation 限制 | workload 能否稳定低压运行 |
| 更高频率 | 单线程/控制路径更快 | 热、IR、clock、wire delay 上升 | 频率收益是否被 memory stall 吃掉 |
| 更小 SRAM bitcell | cache/scratchpad 面积下降 | Vmin/良率/周边占比限制 | SRAM 是否仍值得堆大 |
| 更复杂 BEOL | 更强 routing 潜力 | 成本、EM、via、拥塞风险 | NoC/PDN 是否物理闭合 |

## 常见误解

常见误解是“从 N5 到 N3，整颗芯片面积按 logic density 比例缩小”。实际 SoC 面积包含 SRAM、analog、I/O、PHY、power grid、routing channel 和 keep-out；只要这些部分占比不小，整片面积收益就会低于纯 logic 缩放。

另一个误解是“先进节点一定更省钱”。单位晶体管成本在部分场景可能改善，但设计成本、mask、良率、IP 和封装协同会影响产品总成本。高价值 compute die 值得上先进节点，低价值 I/O 或控制 die 未必值得。

## 一句话理解

工艺节点决定 PPA 上限，但真实收益取决于 logic、SRAM、BEOL、IP、良率和封装共同构成的产品目标函数。

## 架构师启示

如果我在 archax 中比较 N5 与 N3 方案，不能把所有资源统一乘一个 scaling factor。应至少拆分 logic、SRAM、NoC wire、PHY/I/O、analog 和 package interface。RAM wiki 的 [SRAM scaling](../../RAM/wiki/02-sram-foundations/sram-process-scaling-challenge.md) 尤其需要单独处理，因为片上 SRAM 往往是 AI 芯片面积和 Vmin 的关键约束。

一个具体决策例子：若模型显示性能受片外带宽限制，从 N5 换到 N3 可能提高 compute density，但也可能让 memory wall 更严重。此时更合理的方案可能是保持 compute die 节点不变，改 HBM 数量、封装路线或数据流，而不是盲目追求更小节点。
