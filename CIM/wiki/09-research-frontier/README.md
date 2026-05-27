# 09 研究前沿

上级：[CIM Wiki](../README.md)
相关：[08 产业与产品](../08-industry-and-products/README.md), [指标术语表](metrics-glossary.md), [论文阅读模板](paper-review-template.md)

## 这页在回答什么问题

这一章回答：CIM/PIM/NMC 研究论文到底在推进什么问题，以及这些结果如何被正确阅读。

08 章看产品化、供应链和客户导入；09 章看论文创新、实验口径和开放问题。同一个对象可以出现在两章，例如 Samsung HBM-PIM 在 08 是 memory vendor 的产品化案例，在 09 是 PIM 架构研究案例；TSMC 16nm CIM macro 在 09 是 macro-level 研究案例，不应被写成 TSMC 已经推出 CIM 产品。

| 页面 | 研究问题 |
| --- | --- |
| [研究视角与产业视角](research-vs-industry-perspective.md) | 为什么论文跑通和产品成功之间有系统性落差 |
| [近期研究主题](recent-progress-themes.md) | 低比特、mixed precision、3D、new device、LLM memory-bound 的研究主线 |
| [TSMC 16nm CIM macro](case-study-tsmc-16nm-cim-macro.md) | 如何阅读先进工艺下的 SRAM/gain-cell CIM macro 指标 |
| [东大 ReRAM CIM](case-study-u-tokyo-reram-cim.md) | ReRAM 多值存储、10 年保持和推理精度补偿的研究意义 |
| [Samsung HBM-PIM 研究视角](case-study-samsung-hbm-pim-research-angle.md) | HBM-PIM 作为 PIM 架构研究对象时该看什么 |
| [指标术语表](metrics-glossary.md) | TOPS/W、TFLOPS/W、energy/MAC、system speedup 等指标如何防误读 |
| [论文阅读模板](paper-review-template.md) | 读 CIM/PIM/NMC 论文时最少要记录哪些字段 |
| [Open problems](open-problems.md) | 哪些问题仍是研究难点，哪些更像工程优化 |

本章的核心规则是：先判定层级，再看数字。一个 `macro-level` 的 188 TOPS/W 不等于 `chip-level` 能效；一个 `system-level` 的 2x speedup 不等于 cell/array 计算效率；一个 `prototype` 不等于 volume shipment。

## 一句话理解

09 章教你把 CIM/PIM/NMC 论文读成“研究问题和证据链”，而不是读成宣传数字。

## 研究启示

研究前沿的价值在于暴露真实瓶颈：analog CIM 卡在非理想性、校准和外围；digital SRAM-CIM 卡在容量、数据搬移和 reduction；ReRAM/PCM/Flash CIM 卡在器件可靠性；PIM/NMC 卡在系统软件和 memory command。好的论文不是只给更高指标，而是把这些瓶颈中的一个讲清楚、测清楚，并说明它距离系统落地还差哪几层。
