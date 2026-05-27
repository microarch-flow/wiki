# EUV 与多重曝光:7nm 之下的两条路

上级:[前道工艺](./README.md)
相关:[光刻:把版图变成芯片的核心步骤](./photolithography-fundamentals.md), [工艺节点演化与 PPA 取舍](./process-nodes-and-ppa-tradeoffs.md), [Design Rule 和 PDK:架构师与工艺的接口](./design-rule-and-pdk.md)

## 这页在回答什么问题

先进节点为什么会在 DUV 多重图形化和 EUV 之间权衡。核心不是 EUV 光源怎么产生，而是为什么 EUV 让更小节点重新可行，同时也带来成本、缺陷和工艺窗口约束。

## 多重图形化解决了什么

当 193 nm DUV 单次曝光无法直接打印足够小的 pitch 时，可以把一个密集图形拆成多次曝光和多次刻蚀。它的逻辑是把“单次做不到的密度”拆成多个可制造步骤。

```text
target dense pattern
  -> split into mask color A / B / ...
  -> expose and etch A
  -> expose and etch B
  -> combine final pattern on wafer
```

这个方法的代价很直接：mask 数量增加，cycle time 增加，多次步骤之间 overlay 风险增加，layout 需要遵守 coloring rule。对架构师而言，它不会直接出现在性能模型里，但会体现在节点成本、设计规则限制、物理设计复杂度和良率成熟速度上。

## EUV 解决了什么

EUV 使用 13.5 nm 波长，相比 193 nm DUV 在 patterning 上提供更强分辨能力。它的工程价值是减少部分关键层对多重图形化的依赖，让先进节点在可接受复杂度下继续缩小 pitch。

EUV 的反直觉点在于它不是把传统透镜缩小。13.5 nm 光会被很多材料强烈吸收，所以 EUV 系统使用反射式光学而不是传统透镜路径。这个差异带来高复杂度光源、反射镜、mask、resist 和缺陷控制要求。

## EUV 不是免费 scaling

EUV 改善了 patterning，但没有让先进节点回到简单时代。它仍受 stochastic defect、resist、mask defect、曝光吞吐、overlay、工艺窗口和设备成本限制。EUV 用得越多，关键层 patterning 可能更直接，但制造成本和工艺控制要求也更高。

| 路线 | 优势 | 代价 | 架构侧感知 |
| --- | --- | --- | --- |
| DUV 多重图形化 | 利用成熟 DUV 设备，延伸旧技术 | mask 多、overlay 复杂、cycle time 长 | 成本、设计规则和物理收敛复杂 |
| EUV | 减少关键层多重图形化，支持更小 pitch | 设备昂贵、缺陷控制难、工艺窗口窄 | 节点成本、成熟度、PPA 风险 |
| High-NA EUV | 面向更先进节点继续提高分辨能力 | 工具、mask、field、工艺集成更复杂 | 未来节点密度与成本 trade-off |

## 为什么这会影响架构

架构师选择节点时，实际是在选择一套 patterning 成本和设计限制。若一个节点大量依赖复杂 patterning，mask 成本、设计周期和物理签核风险会上升；若节点使用 EUV 缓解部分层的复杂度，也要接受更高制造资本密度和良率爬坡风险。

这影响产品策略。高价值 AI/HPC 芯片可以用先进节点换取 compute density 和能效；成本敏感控制芯片或 I/O die 可能更适合成熟节点，因为先进 patterning 带来的面积收益无法覆盖成本和 IP 迁移代价。

## 常见误解

常见误解是“EUV 出现后，多重图形化就不重要了”。实际先进节点会按层选择不同 patterning 策略，EUV 减少但不消灭多重图形化和严格 design rule。

另一个误解是“EUV 等于节点领先”。EUV 是实现先进节点的重要工具，但节点能力还取决于器件结构、BEOL、SRAM、PDK、良率、IP 和设计生态。架构师评估节点不能只看是否使用 EUV。

## 一句话理解

多重图形化用更多步骤延伸 DUV，EUV 用更短波长降低部分关键层复杂度；两者都把 scaling 收益和成本/良率/设计规则绑在一起。

## 架构师启示

如果我在 N5、N3 或更先进节点上评估一颗 AI accelerator，EUV 的存在不意味着面积可以按理想比例缩小。我需要分别检查 logic、SRAM、NoC routing、PHY、analog 和 package interface 的 scaling，因为 patterning 改善主要作用在特定层和特定结构。

一个具体例子：若 compute array 逻辑密度收益明显，但 SRAM 宏和 HBM PHY 面积收益有限，继续换更先进节点可能只改善 compute，不解决 memory wall。此时架构选择可能要转向 HBM、chiplet 或更合理的数据流，而不是单纯追节点。
