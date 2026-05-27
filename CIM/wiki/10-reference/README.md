# 10 Reference

上级：[CIM Wiki](../README.md)
相关：[CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md), [指标术语表](../09-research-frontier/metrics-glossary.md), [学习路径](../01-overview/learning-roadmap.md)

## 这页在回答什么问题

这一章回答：读完整个 CIM wiki 后，怎样快速查术语、排除常见误解、选择技术路线和按目标回到对应章节。

10 章不是新知识章节，而是 reference layer。它把 01 到 09 的判断规则压缩成可查询工具，避免读者在后续阅读论文、公司材料或架构方案时重新混淆 CIM/PIM/NMC、memory technology 和 compute paradigm。

| 页面 | 用途 |
| --- | --- |
| [术语表](glossary.md) | 统一 CIM/PIM/NMC、analog/digital/mixed-signal、macro/tile/chip/system 等术语 |
| [高频问题](high-frequency-questions.md) | 回答最容易误判的概念，例如 PIM 是否等于 CIM、HBM-PIM 是否是 CIM |
| [路线选型决策树](decision-tree-cim-route-selection.md) | 按目标、约束和风险选择 SRAM-CIM、ReRAM/Flash CIM、DRAM/HBM-PIM 或 NMC |
| [按目标阅读路径](reading-roadmap-by-goal.md) | 根据学习、研究、建模、产品分析目标回到对应章节 |

使用本章时有一个原则：先查 taxonomy，再查技术路线，最后查指标。分类错了，后面的比较都会错；层级错了，指标会误导；目标错了，阅读路径会变成散点信息堆积。

## 一句话理解

10 章是整份 wiki 的索引、术语约束和路线选择工具。

## 维护原则

参考章的价值不在于提供更多材料，而在于降低误读成本。新增术语时先对齐 [01 taxonomy](../01-overview/cim-pim-nmc-taxonomy.md)，新增公司时先判 CIM/PIM/NMC 和产品层级，新增指标时先链接到 [09 指标术语表](../09-research-frontier/metrics-glossary.md)，新增路线时先落到 memory technology × compute paradigm 矩阵。
