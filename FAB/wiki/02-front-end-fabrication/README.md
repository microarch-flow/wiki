# 前道工艺

上级:[芯片制造与封测 Wiki 总览](../01-overview/README.md)
相关:[前道与后道:产业分工和技术差异](../01-overview/front-end-vs-back-end.md), [工艺节点、封装路线、测试阶段的命名体系](../01-overview/taxonomy.md), [为什么必须在 wafer 阶段测试](../03-wafer-test-and-cp/why-wafer-sort-exists.md)

## 这页在回答什么问题

前道工艺如何把一片 wafer 变成包含大量可测试 die 的 processed wafer。这里不追设备型号和化学配方，而是建立架构师需要的工艺主线：晶体管、金属互联、设计规则、节点 PPA 和良率约束如何共同限制架构选择。

## 前道的主线

前道 fabrication 可以理解成三层对象逐步形成：

```text
wafer substrate
  -> FEOL: transistor / isolation / well / gate / source-drain
  -> MOL: contact / local interconnect
  -> BEOL: multi-level metal stack / vias / top metal / pad interface
```

FEOL 决定晶体管开关能力、漏电、阈值、电压和密度基础；MOL 决定器件如何接入金属系统；BEOL 决定片上互联、供电网络、时钟、SRAM/logic 周边布线和顶层封装接口。架构师不需要手动设计这些工艺步骤，但必须知道节点选择不是单个 transistor 选择，而是器件、金属、设计规则、IP 和良率成熟度的组合。

## 本章怎么读

| 文件 | 重点 | 架构师要带走的问题 |
| --- | --- | --- |
| [wafer-the-substrate.md](./wafer-the-substrate.md) | wafer 是制造载体 | die 面积、wafer map、边缘损失和缺陷为什么影响成本 |
| [process-flow-overview.md](./process-flow-overview.md) | FEOL/MOL/BEOL 节奏 | 一个版图如何被多轮图形化和材料加工实现 |
| [photolithography-fundamentals.md](./photolithography-fundamentals.md) | 光刻角色 | 为什么图形转移决定 scaling 节奏 |
| [euv-and-multi-patterning.md](./euv-and-multi-patterning.md) | EUV 与多重图形化 | 为什么更小节点会换来成本和工艺窗口问题 |
| [etching-deposition-cmp.md](./etching-deposition-cmp.md) | 三类支柱工艺 | 为什么层数越多，平整度和界面越关键 |
| [doping-and-ion-implantation.md](./doping-and-ion-implantation.md) | 掺杂与器件电性 | 为什么 transistor 不是“画出来的开关” |
| [transistor-evolution-planar-finfet-gaa.md](./transistor-evolution-planar-finfet-gaa.md) | 器件结构演化 | 为什么 FinFET 和 GAA 改变功耗/电压空间 |
| [interconnect-stack-beol.md](./interconnect-stack-beol.md) | 片上金属栈 | 为什么 BUS/NoC 的物理实现受 BEOL 限制 |
| [process-nodes-and-ppa-tradeoffs.md](./process-nodes-and-ppa-tradeoffs.md) | 节点与 PPA | 为什么节点选择不是越小越好 |
| [design-rule-and-pdk.md](./design-rule-and-pdk.md) | PDK/设计规则接口 | 架构师如何把工艺约束传给 floorplan 和模型 |

## 前道对架构的主要约束

| 约束 | 来自哪里 | 影响什么 |
| --- | --- | --- |
| 晶体管密度 | lithography、器件结构、标准单元库 | compute density、控制逻辑面积 |
| SRAM scaling | bitcell、良率、Vmin、周边电路 | cache、scratchpad、register file 面积 |
| 线延迟与拥塞 | BEOL 金属层、via、设计规则 | NoC、clock、wide bus、timing closure |
| IR drop 与 EM | PDN 金属、电流密度、活动因子 | 峰值频率、power gating、floorplan |
| 缺陷密度 | 工艺成熟度、die 面积、层数 | die yield、binning、chiplet 切分 |
| PDK/IP 可用性 | design rule、library、PHY、SRAM compiler | 产品进度、节点迁移成本 |

## 一句话理解

前道工艺不是把版图“印到硅上”这么简单，而是在器件、图形、材料、金属互联和设计规则之间共同决定 die 的 PPA 与良率边界。

## 架构师启示

如果我在早期模型里把 SRAM 容量、NoC 宽度和频率目标一起上调，前道章节提醒我这不是三个独立参数。SRAM 可能不随逻辑等比例缩小，NoC 宽度会增加 BEOL 拥塞和功耗，频率目标会推高电压与 IR/thermal 压力。

架构评审中应把节点选择写成“节点 + 库 + SRAM compiler + 金属栈 + IP + 良率假设”的组合，而不是只写 N5/N3/2nm 这类节点名。
