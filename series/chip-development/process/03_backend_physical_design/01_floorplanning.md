# Floorplanning

## 前置知识

- 建议先读 [后端物理设计总览](./README.md)。
- 建议理解 [Floorplan](../00_overview/05_glossary.md#floorplan)、[PPA](../00_overview/05_glossary.md#ppa)、[SRAM Compiler](../00_overview/05_glossary.md#sram-compiler)、[PDK](../00_overview/05_glossary.md#pdk)。

## 核心概念

Floorplanning 是后端的第一组关键决策：芯片或 block 多大，形状如何，macro 放在哪里，IO/pad/bump 如何分布，电源网格怎么铺，clock/reset/NoC/高速接口从哪里走，哪些区域保留给 placement 和 routing。

它决定后续实现的天花板。错误 floorplan 会造成后面 placement、CTS、routing、STA、IR drop 全部困难。软件背景容易把 floorplan 想成“二维排版”，但它实际是在用物理约束定义系统架构。尤其对 AI 芯片，大量 SRAM macro、宽数据通路、NoC、HBM/DDR/PCIe/SerDes 接口会让 floorplan 成为 PPA 的第一战场。

## 关键活动顺序

1. 收集输入：网表、初版 SDC、macro list、LEF/lib、UPF、电源域、IO 规划、package/bump 约束、DFT 约束、工艺 metal stack。
2. 确定 die/block size、aspect ratio、utilization 目标和 keepout。
3. 放置 hard macro：SRAM、ROM、PLL、SerDes、PHY、analog IP、large compiled memory。
4. 定义 power plan：ring、stripe、mesh、power switch、level shifter、isolation cell、always-on 区域。
5. 规划 block boundary、pin assignment、feedthrough、NoC/总线走向和 clock entry。
6. 跑 early placement/route estimate，检查拥塞、线长、timing、IR 风险。
7. 与前端/架构迭代：调整 macro banking、pipeline、接口位置、模块层次或目标频率。
8. 冻结 floorplan baseline，作为 placement 和后续 signoff 的起点。

## 工具名

常用工具包括 Cadence Innovus、Synopsys IC Compiler II/Fusion Compiler、Siemens Aprisa。早期 floorplan 还会用 Ansys RedHawk-SC 或 Cadence Voltus 做 power grid 预估，用 PrimeTime/Tempus 做 early timing，用 internal scripts 检查 macro/channel/pin 规则。

## 角色与典型时长

主 owner 通常是 physical design lead。参与者包括架构师、RTL owner、STA、power integrity、DFT、package/IO、IP owner、CAD/flow。小 block floorplan 可以在数天到数周内形成初版；复杂 AI SoC 全芯片 floorplan 往往需要数周到数月迭代。先进节点由于 macro、bump、电源、routing 和 DRC 规则更强，早期迭代次数通常更多。

## 关键决策点

- Die size 与 utilization：utilization 太高会导致拥塞和 timing closure 失败；太低会增加面积和 mask/wafer 成本。
- Macro 位置：靠近使用者可降低线长和功耗，但可能制造 routing blockage。
- 电源网格强度：太弱会 IR/EM 失败；太强会占用 routing resource。
- IO/bump 位置：需要同时满足 package、board、PHY、ESD、信号完整性和软件系统连接。
- 层次划分：hierarchical flow 可以提升容量和并行度，但 boundary timing 和 top-level integration 更复杂。

决策错误的后果通常是后期反复 rip-up：比如 SRAM 放置导致 NoC 横穿 macro channel，routing 拥塞无法修；或者电源网格后期加粗，挤占信号线，导致 timing 和 DRC 同时恶化。

## 成本视角

Floorplan 本身主要消耗资深 PD/架构/STA 人力和若干轮工具运行成本，但它决定 die size 和后续返工概率。Die area 每增加 10% 不只是版图变大，还会影响每片 wafer 上的 die 数、良率和封装成本；具体单颗成本变化要结合 wafer price、die size 和 yield 计算。对先进节点，full mask 成本通常在百万到千万美元量级，因此早期用几周做 physical feasibility 通常比后期 respin 便宜得多。

## 先进节点与 28/16nm 差异

28nm/16nm 项目中，线延迟和设计规则也重要，但 floorplan 有时还有较多后期修补空间。7nm 及以下，wire RC、pin access、multi-patterning/EUV 相关规则、power density、via resistance、cell track 限制更严，错误 macro/channel 规划更难靠工具自动修复。

先进节点还更依赖 foundry 推荐的 routing direction、preferred layer、power grid template、cell height、track pattern 和 block-level signoff rule。创业公司不能把成熟节点经验简单平移到 5nm/3nm。

## 常见坑

- 只按模块层次摆放，不按真实数据流摆放。
- 忽略 SRAM macro 的 pin 方向、access side 和 keepout。
- 初期 utilization 设太高，后期靠工具“压缩”。
- 电源网格规划太晚，先布信号再补 power。
- 没有让 package/IO 团队参与，导致 bump/pad 与内部数据流冲突。
- 忽略 DFT scan chain、test clock、MBIST controller 位置。
- 没有把 floorplan feedback 传回 RTL，导致后端独自承担结构性问题。

## 上下游接口

上游来自前端的输入包括网表、SDC、UPF、macro/IP 视图、模块层次和 early PPA 估算。floorplan 输出给 placement 的是 DEF、physical constraint、macro location、power grid、pin assignment、blockage、region/group constraint。

Floorplan 也会反推前端：如果 critical path 跨越物理距离过长，可能要求加 pipeline；如果 macro 太多导致 channel 不足，可能要求调整 SRAM banking；如果 IO 到 compute path 太远，可能要重构 top-level integration。

## 创业公司取舍

创业公司第一颗芯片应降低 floorplan 风险：减少不必要的 hard macro 类型，避免过多电源域，控制 NoC 复杂度，优先选择可用 reference floorplan 的 IP 和接口。若外包后端，也必须内部参与 floorplan review，因为 floorplan 直接体现产品架构和成本取舍，不应完全交给服务商决定。

可以省的是过度追求极限面积；不能省的是 early floorplan exploration。花几周识别物理不可行结构，比 tapeout 前两个月发现全芯片拥塞便宜得多。

## 典型场景

一个 NPU block 有 64 个 compute tile 和大量 SRAM。初版 floorplan 按 RTL hierarchy 排成矩形，SRAM 放在四周。placement 后发现 tile 到 SRAM 的读写路径跨越大半个 block，关键路径无法收敛，routing channel 也被 macro 切断。修复方案不是简单加 buffer，而是把 SRAM bank 按 tile cluster 分组，调整 NoC 入口，把 reduction tree 增加一级 pipeline，并降低局部 utilization。结果面积略增，但时序、拥塞和功耗更可控。

## 后续阅读

- [Placement](./02_placement.md)
- [Power Analysis](./06_power_analysis.md)
- [先进节点特殊考虑](./08_advanced_node_considerations.md)
- [后端外包](./09_backend_outsourcing.md)

## 参考公开来源

- [Synopsys IC Compiler II](https://www.synopsys.com/implementation-and-signoff/physical-implementation/ic-compiler.html)
- [Cadence Innovus Implementation System](https://www.cadence.com/en_US/home/resources/datasheets/innovus-implementation-system-ds.html)
- [Ansys RedHawk-SC](https://www.ansys.com/en-gb/products/semiconductors/ansys-redhawk-sc)
- [Cadence Voltus](https://www.cadence.com/en_US/home/resources/datasheets/voltus-ic-power-integrity-solution-gt-ds.html)

## 内容可信度说明

- **公开信息（高可信）**：floorplan、macro placement、power grid、early timing/power 分析是公开 EDA flow 中的标准环节。
- **行业惯例（中可信）**：utilization、macro channel、pin assignment、power mesh 和 floorplan review 的具体策略因团队和节点而异。
- **经验性观察（中低可信）**：AI 芯片 floorplan 的主要风险通常来自 SRAM、NoC、宽数据路径和功耗密度。
- **不确定/需向资深工程师确认（低可信）**：具体节点的 routing track、PG template、macro keepout、bump rule 和 foundry 推荐约束。
