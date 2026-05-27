# 芯片制造与封测 Wiki 总览

上级:[芯片制造与封测 Wiki](..)
相关:[为什么架构师必须懂工艺与封装](./problem-statement.md), [一片 wafer 到一颗成品芯片的完整路径](./from-wafer-to-product.md), [工艺节点、封装路线、测试阶段的命名体系](./taxonomy.md)

## 这页在回答什么问题

这份 wiki 要解决的不是“半导体制造有哪些名词”，而是架构师如何把工艺、封装、测试和可靠性纳入产品定义与架构选型。读完这一章后，你应该知道后续各章在整条芯片交付链里分别负责哪一段，以及哪些问题必须提前问。

## 这份 wiki 的边界

芯片从设计图变成产品，不是一条只属于工艺工程师的制造流水线。架构师决定 die 面积、SRAM 容量、HBM 数量、chiplet 切分、I/O 位置、功耗密度和目标 SKU 时，已经在决定后续制造与封装难度。工艺节点限制晶体管密度、频率、电压和漏电；封装限制 die 间带宽密度、供电、散热、机械可靠性和可测试性；测试与良率决定一个设计是否能以可接受成本出货。

本 wiki 的正文按时间线展开：先看产品为什么需要理解制造，再进入前道晶圆制造、中测、后道封装、终测与可靠性，最后把热、应力、PI/SI、失效模式和良率经济学作为跨阶段问题合并分析。产业地图独立放在第 07 章，避免把技术判断和商业版图混在同一层讨论。

## 全局路径

一颗芯片的交付链可以压成下面的对象流：

```text
architecture intent
  -> RTL / physical design
  -> mask / wafer fabrication
  -> wafer sort / CP
  -> die singulation
  -> package assembly
  -> package-level test / burn-in / reliability qualification
  -> module / board / system product
```

这条路径里每一步都在筛选风险。前道把设计规则、晶体管、金属互联和缺陷密度变成 die 的 PPA 与良率；CP 在 wafer 阶段尽早筛掉坏 die；封装把一个或多个 known-good die 组合成 package；终测和可靠性验证再确认它能在目标电压、温度、机械和寿命条件下工作。

对架构师最重要的结论是：后续阶段不是“实现细节”，而是设计约束的回声。一个过大的 monolithic die 会把良率风险压到前道；一个多 chiplet 设计会把风险转移到 die-to-die 互连、KGD 和封装良率；一个 HBM 方案会把内存带宽问题转化为 2.5D/3D 集成、供电、热和测试问题。

## 章节角色

| 章节 | 主要回答 | 后续依赖 |
| --- | --- | --- |
| 01-overview | 为什么学、路径怎么走、术语怎么命名 | 全 wiki 的语言边界 |
| 02-front-end-fabrication | wafer 内部如何形成 transistor 与 BEOL 互联 | 工艺节点、PPA、PDK、良率 |
| 03-wafer-test-and-cp | 为什么 wafer 阶段就要测试，KGD 为什么关键 | 3DIC、HBM、良率经济学 |
| 04-back-end-packaging | package 如何从传统封装演化到 2.5D/3D/HBM | 热、应力、PI/SI、选型 |
| 05-final-test-and-reliability | 出货前如何验证功能、寿命和可靠性 | 失效分析、认证边界 |
| 06-cross-cutting-engineering | 热、应力、供电、信号、失效和良率如何贯通 | 架构到工艺/封装选型 |
| 07-industry-map | 公开产业链分工与能力版图 | 技术路线的供应侧约束 |
| 08-reference | 术语、指标、FAQ、决策树 | 快速复习与查表 |

## 架构师应该带着哪些问题读

读前道章节时，不要把重点放在设备型号或化学细节上，而要问：这个节点为什么能提供更高密度或更低能耗，它付出了哪些设计规则、成本、良率和 SRAM scaling 代价。读封装章节时，不要只记 CoWoS、EMIB、SoIC 这些名字，而要问：这条路线解决的是全局大平台、局部高密度互连，还是垂直堆叠；它把风险放在 interposer、RDL、bridge、bonding、substrate 还是测试环节。

这份 wiki 的目标不是让架构师替代制造团队做工艺开发，而是让架构师在产品定义阶段能提出正确问题。例如，若一个 AI accelerator 需要 8 个 HBM stack 和多个 compute chiplet，问题不是“封装团队能不能接一下”，而是封装路线、HBM 供给、package 尺寸、热路径、PDN、KGD、测试覆盖率和良率经济学能否同时闭合。

## 一句话理解

芯片制造与封测是架构决策的物理边界：它把 PPA 目标、die 切分、内存带宽、供电、散热、测试和成本拉进同一个可制造性问题。

## 架构师启示

架构师不需要掌握每一道工艺 recipe，但必须知道哪些设计选择会把风险推给制造和封装。如果我在定义一颗 AI 加速器，单 die、chiplet、HBM 数量和封装路线不能分开定：单 die 可能受 reticle 与良率约束，chiplet 需要付出 D2D 互连和封装测试代价，HBM 则会把系统推向 2.5D/3D 集成、强 PDN 和严格热设计。

一个实用做法是，在架构评审里把“制造与封测问题”前置成四个问题：目标节点能否支撑面积与 SRAM 密度；封装能否支撑所需带宽密度；热和供电路径是否有物理闭合方案；测试和 KGD 策略是否能把组合良率压到可接受范围。
