# 学习路径与各章节依赖关系

上级:[芯片制造与封测 Wiki 总览](./README.md)
相关:[为什么架构师必须懂工艺与封装](./problem-statement.md), [工艺节点、封装路线、测试阶段的命名体系](./taxonomy.md), [按目标的学习路径](../08-reference/reading-roadmap-by-goal.md)

## 这页在回答什么问题

这份 wiki 应该按什么顺序读，哪些概念必须先建立，哪些章节可以按目标跳读。它的目的不是导航所有文件，而是避免把前道、封装、测试、可靠性和产业地图混成一团。

## 推荐主线

第一次读建议按 `01 -> 02 -> 03 -> 04 -> 05 -> 06`，最后按需要读 `07` 和 `08`。

```text
01 overview
  -> 02 front-end fabrication
  -> 03 wafer test / CP / KGD
  -> 04 back-end packaging
  -> 05 final test / reliability
  -> 06 cross-cutting engineering
  -> 07 industry map
  -> 08 reference
```

这个顺序背后的原因很简单：前道决定 die 的物理基础，CP 决定哪些 die 可以进入后续高价值集成，封装决定 die 如何变成 product，终测和可靠性决定产品能否出货，跨工艺问题只有在前面对象都建立后才讲得清。

## 第一遍读什么

第一遍不要追求每个工艺细节，而要建立对象关系。

| 目标 | 建议阅读 | 应该得到的能力 |
| --- | --- | --- |
| 建立全链路 | `01` 全章，`02/process-flow-overview.md`，`03/why-wafer-sort-exists.md`，`04/packaging-taxonomy.md` | 能说清 wafer、die、package、test 的关系 |
| 理解工艺节点 | `02/process-nodes-and-ppa-tradeoffs.md`，`02/design-rule-and-pdk.md` | 能判断节点选择影响哪些 PPA 与设计约束 |
| 理解 HBM/AI 封装 | `04/hbm-as-case-study/*`，`06/thermal-path-and-management.md`，`06/power-delivery-pi-pdn-decap.md` | 能把 HBM 带宽和 2.5D/3D 封装联系起来 |
| 理解 chiplet/3DIC | `04/3d-routes/*`，`03/kgd-known-good-die.md`，`06/yield-economics-across-stages.md` | 能判断 D2D、KGD、热和良率为什么耦合 |
| 做路线选型 | `04/2.5d-routes/*`，`06/from-architecture-to-process-selection.md`，`08/decision-tree-process-and-package.md` | 能从架构需求反推节点和封装路线 |

## 章节依赖关系

`02-front-end-fabrication` 是后续所有节点和 PPA 讨论的基础。比如 BEOL 金属互联会连接到 BUS wiki 里的物理实现问题，工艺节点与 SRAM scaling 会连接到 RAM wiki 的 SRAM 工艺缩放讨论。

`03-wafer-test-and-cp` 是 `04` 和 `06` 的前置。没有 KGD，就很难理解 HBM、3DIC 和多 chiplet package 为什么必须把测试前移。CP 章节不只是测试知识，它是良率经济学的入口。

`04-back-end-packaging` 是本 wiki 的核心主体，内部顺序也重要：先读后道总览，再读 2.5D 路线，再读 3D 路线，再读 RDL/bump/substrate/underfill 这些关键组件，最后用 HBM 案例把它们合起来。

`05-final-test-and-reliability` 讲出货前最后如何收敛风险。它和 `03` 的区别是：`03` 主要在 wafer/die 阶段筛选，`05` 主要在 package/product 阶段验证功能、寿命和可靠性。

`06-cross-cutting-engineering` 是压轴章。热、应力、PI、SI、失效和良率不是某一个阶段的问题，而是跨前道、封装、测试共同形成的约束。只有读完 `02-05` 后，这一章的 trade-off 才不会变成抽象口号。

## 何时读产业地图

`07-industry-map` 不放在主线中间，是为了保持技术概念清洁。先理解路线和约束，再看谁能做什么、谁卡在哪里，判断会更稳。若一开始就看公司和平台名，容易把商品名当技术分类，把公开路线图当工程能力。

正文里出现厂商平台时，只用于标注技术例子；系统性的供应链、foundry、OSAT、材料、设备和大陆能力对比统一放到 `07`。

## 与已有 BUS/RAM/NoC wiki 的读法

如果你从 NoC 过来，建议先读 `04/3d-routes` 和 `06/signal-integrity-in-package.md`，再回看 NoC 的 [chiplet 与 die-to-die 互连](../../NOC/wiki/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)。这样能把“跨 die 不是多几 hop”落到封装物理上。

如果你从 RAM 过来，建议先读 `04/hbm-as-case-study`，再回看 RAM 的 [HBM 协议](../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md) 与 [HBM 集成](../../RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv.md)。这样能把 HBM 的协议宽接口和 package 对象关系连起来。

如果你从 BUS 过来，建议读 `02/interconnect-stack-beol.md` 和 `06/power-delivery-pi-pdn-decap.md`，再回看 BUS 的 [互连组件与数据路径分解](../../BUS/wiki/04-microarchitecture-integration/interconnect-components.md)。这样能把片上路径模型和物理布线/供电约束连接起来。

## 一句话理解

这份 wiki 应按“die 怎么造、die 怎么筛、die 怎么封、产品怎么测、跨阶段问题怎么闭合”的顺序读。

## 架构师启示

如果我只关心架构选型，最短路径不是跳到封装名词表，而是先读 `01`、`02/process-nodes-and-ppa-tradeoffs.md`、`04/packaging-taxonomy.md`、`04/2.5d-routes/2.5d-routes-tradeoff-map.md` 和 `06/from-architecture-to-process-selection.md`。这样能避免把 CoWoS、SoIC、EMIB、Fan-out 这些名字当作孤立选项。

如果我正在做具体 AI 芯片方案，阅读顺序应围绕对象树组织：compute die 用什么节点，memory 是 HBM 还是外部 GDDR/LPDDR，die 是否拆分，封装是否 2.5D/3D，测试在哪些阶段拦截坏 die。这个顺序比按厂商平台名阅读更接近工程决策。
