# 前道与后道:产业分工和技术差异

上级:[芯片制造与封测 Wiki 总览](./README.md)
相关:[一片 wafer 到一颗成品芯片的完整路径](./from-wafer-to-product.md), [前道工艺的整体节奏:FEOL/MOL/BEOL](../02-front-end-fabrication/process-flow-overview.md), [后道封装](../04-back-end-packaging/README.md)

## 这页在回答什么问题

前道、后道、封装、测试这些词经常混用，它们到底在技术对象和工程责任上怎么分。理解这个边界，是为了知道架构问题什么时候落在 transistor/BEOL，什么时候落在 package/substrate/test。

## 前道在制造 die，后道在制造 product

前道 fabrication 的核心对象是 wafer 上的 die。它通过光刻、刻蚀、沉积、掺杂、CMP、金属互联等步骤，把晶体管和片上互联做进硅片。前道结束后，die 的逻辑功能、晶体管特性、片上 SRAM、BEOL 互联、pad 或 bump 接口已经被制造出来。

后道 packaging and assembly 的核心对象是 package。它把一个或多个 die 连接到 substrate、interposer、RDL 或 bridge 上，再通过 bump、underfill、molding、lid、TIM 等结构把裸 die 变成可上板、可供电、可散热、可测试的产品。后道不只是保护芯片外壳，在先进封装中，它已经决定 die 间互连密度、HBM 邻接、供电完整性、热路径和机械可靠性。

## 三个容易混的“后道”

中文里“后道”在不同语境里会指 wafer fabrication 内部的 BEOL，也会指封装 assembly。为了避免混乱，本 wiki 使用下面的边界：

| 术语 | 本 wiki 中的含义 | 典型对象 | 为什么重要 |
| --- | --- | --- | --- |
| FEOL | front-end-of-line，晶体管形成 | transistor、well、gate、source/drain | 决定器件性能、漏电、密度基础 |
| MOL | middle-of-line，器件到局部互联的连接 | contact、local interconnect | 决定器件到金属栈的接入代价 |
| BEOL | back-end-of-line，die 内金属互联 | M0/M1/... metal stack | 决定片上互联、时序、IR、布线拥塞 |
| Packaging / assembly | die 外部封装与系统集成 | substrate、interposer、RDL、bump、underfill | 决定 package 级互连、供电、热、可靠性 |
| Test | wafer/package/system 阶段筛选 | CP、final test、burn-in | 决定风险在哪个阶段被发现 |

这个区分影响架构判断。NoC 的片上 wiring 主要先受 BEOL 约束；chiplet 的 die-to-die wiring 主要受 package/interposer/RDL 约束；HBM stack 内部和 logic-HBM 之间同时涉及 DRAM die 制造、3D stack、2.5D package 和测试策略。

## 分工不是绝对边界

传统产业分工可以粗略写成：foundry 做前道 wafer，OSAT 做封装与测试，fabless 做设计和产品定义。但先进封装让边界变得更紧。因为 2.5D/3D 集成需要把 wafer-level 工艺能力、封装 assembly、测试和设计协同放在同一条量产链上，一些 foundry 会把高端封装平台纳入自身体系，一些 OSAT 也会向 fan-out、bridge、2.5D 和系统级封装上探。

本章不展开具体公司版图，产业分工的详细讨论放在 [产业地图](../07-industry-map/README.md)。这里要保留的技术结论是：越先进的封装，越不能把 foundry、OSAT、memory、substrate、材料和测试当作彼此独立的后置供应商选择。

## 常见误解

常见误解是“BEOL 和封装都是后道，所以差不多”。实际上，BEOL 是 die 内部金属互联，受前道工艺设计规则和晶圆厂流程约束；封装是 die 外部系统集成，受 substrate、interposer、RDL、bump、材料、热机械和 assembly 约束。二者都影响互连，但物理尺度、材料体系、良率机制和责任边界不同。

另一个误解是“封装只是 OSAT 的事”。在高端 AI/HPC package 里，封装路线会反向影响 die floorplan、HBM interface、D2D PHY、power delivery、thermal budget 和测试结构。架构师不需要决定每个 assembly 参数，但必须在产品定义时知道这条路线由哪些能力闭合。

## 一句话理解

前道把电路做进 die，后道把 die 变成产品；BEOL 是片内互联，packaging 是片外/封装内系统集成，二者不能混为一谈。

## 架构师启示

如果我在设计片上 NoC，BEOL 金属层、线延迟、拥塞和 IR drop 是主要物理边界；如果我在设计 chiplet fabric，micro-bump pitch、interposer/RDL routing、package SI/PI 和 KGD 才是主边界。把这两类互连都抽象成“多几条 link”会低估后者的封装复杂度。

因此，在架构模型中至少要区分 on-die interconnect 与 in-package interconnect。前者主要跟工艺节点、金属栈和 floorplan 绑定；后者主要跟封装路线、substrate/interposer 能力、热机械和测试策略绑定。
