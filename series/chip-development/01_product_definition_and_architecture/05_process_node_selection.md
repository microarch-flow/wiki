# 工艺节点选择

## 前置知识

- 建议先读 [芯片项目成本结构总览](../00_overview/03_cost_structure.md)。
- 建议先读 [架构探索](./03_architecture_exploration.md)。
- 建议先读 [IP 策略](./04_ip_strategy.md)。

## 工艺节点选择的本质

工艺节点选择不是“越先进越好”。它是在性能、功耗、面积、成本、IP 可获得性、[Foundry](../00_overview/05_glossary.md#foundry) 关系、封装、良率、[EDA](../00_overview/05_glossary.md#eda) 流程、团队能力和融资节奏之间做系统级决策。

先进节点，例如 7nm、5nm、3nm、2nm，通常提供更高逻辑密度和更好能效，但 [Mask Cost](../00_overview/05_glossary.md#mask-cost)、[Wafer](../00_overview/05_glossary.md#wafer) 成本、EDA/IP 成本、验证要求、后端复杂度和供应链门槛也显著提高。成熟节点，例如 28nm、22nm、16/14nm，成本和风险较低，但在 AI 计算密度和能效上可能无法满足数据中心级需求。

对创业公司，正确问题是：目标产品是否真的需要先进节点，先进节点带来的 PPA 收益能否覆盖 NRE、风险和时间成本。

## 工艺节点影响什么

| 影响项 | 先进节点特点 | 成熟节点特点 |
|---|---|---|
| 逻辑密度 | 更高，适合大规模计算阵列 | 较低，die size 可能变大 |
| 能效 | 通常更好，但受频率、电压和互连影响 | 较差，但实现风险低 |
| SRAM | 不一定按逻辑同比例缩放，macro 选择关键 | 面积大但成熟 |
| 模拟/IO | 复杂且昂贵，PHY 依赖强 | 选择更多，风险低 |
| Mask/NRE | 百万美元到千万美元量级更常见 | 低很多，适合试错 |
| Wafer 成本 | 高，且产能竞争激烈 | 低，供应更分散 |
| EDA 流程 | signoff corner 多，物理规则复杂 | 流程成熟，工具压力小 |
| 后端实现 | routing、IR drop、EM、timing 难度高 | 相对可控 |
| IP 可得性 | 高端 IP 可用但贵且受限 | 基础 IP 丰富 |
| 良率爬坡 | 新节点不确定性更高 | 成熟良率更稳定 |

先进节点还会引入 EUV、多重图形化、复杂设计规则、更严格的电源完整性和信号完整性要求。7nm 及以下不是简单“把 RTL 综合到更小晶体管”。

## AI 芯片为什么倾向先进节点

AI 加速器常需要大量 MAC、SRAM、[NoC](../00_overview/05_glossary.md#noc) 和高速接口。先进节点能在相同面积和功耗下提供更多计算单元，或在相同性能下降低功耗。数据中心 AI 芯片还常需要高带宽内存和先进封装，这些生态通常与领先 foundry 和先进节点绑定。

但 AI 芯片也常被内存和软件限制。如果 workload 主要受外部带宽、host 调度或小 batch 利用率限制，先进节点带来的峰值计算增加可能不能转化为客户价值。此时更先进节点只会提高成本和风险。

## 成本量级

公开信息和行业估算通常显示，先进节点 full mask 和总 NRE 会进入百万到千万美元甚至更高量级。具体数字高度依赖 foundry、节点、mask 层数、商务条件、IP、封装、测试和工程团队规模。先进 AI 芯片全项目成本可能远高于 mask 本身。

这些数字不能当作报价，只能用于早期判断：第一颗芯片如果选择 5nm/3nm，还叠加 HBM、高速 [SerDes](../00_overview/05_glossary.md#serdes)、先进封装和商业 EDA，全项目资金需求会与成熟节点 MPW 或小芯片完全不同。

成本决策还要看销量。[NRE](../00_overview/05_glossary.md#nre) 可以通过销量摊销。若目标市场销量有限，先进节点的固定成本可能压垮毛利。若目标客户愿意为高能效和性能支付高 [ASP](../00_overview/05_glossary.md#asp)，先进节点才更容易成立。

## 节点选择流程

第一步是从产品目标反推 PPA。需要估算目标 workload 下的有效吞吐、功耗、die area、外部带宽和封装需求。

第二步是做多节点架构映射。至少比较一个先进节点和一个较成熟节点，例如 5/7nm 对比 12/16nm，或 7nm 对比 28nm。比较不能只看理论密度，还要包含 SRAM、IP、IO、封装和频率。

第三步是确认 IP 可用性。关键 IP 必须支持目标 foundry 和节点，包括 PCIe、DDR/HBM、SerDes、PLL、SRAM compiler、eFuse、安全 IP 和 DFT 相关支持。

第四步是确认 foundry 和 PDK 获取路径。没有 [PDK](../00_overview/05_glossary.md#pdk)，真实后端和 signoff 无法进行。先进节点 PDK 获取通常需要商务关系、NDA、资质和项目可信度。

第五步是建立成本模型。包括 mask、wafer、封装、测试、IP、EDA、人力、prototype、bring-up、reliability、respin contingency。不要只比较 wafer price。

第六步是评估团队能力。先进节点需要强后端、STA、DFT、低功耗、物理验证、foundry interface 和项目管理能力。创业公司可以外包部分后端，但不能外包系统责任。

## 角色和典型时长

工艺节点选择不是架构师单独决定。参与角色应包括芯片架构负责人、后端/STA lead、DFT/test lead、IP owner、封装工程师、foundry interface、供应链/运营、财务和创始人。若项目涉及 HBM、chiplet 或高速 SerDes，还需要 OSAT、基板、板级 SI/PI 和硅后负责人提前参与。

早期节点筛选可以在数周内完成，但可信的节点决策通常需要数月滚动收敛，因为它依赖 IP vendor 回复、PDK/EDA 路径、封装报价、后端预估、成本模型和融资计划。先进节点或 HBM/2.5D 项目尤其不能等 RTL 写完后再确认工艺和封装。

## 7nm 及以下的特殊考虑

7nm 及以下通常需要更强的物理设计纪律。时序收敛、routing congestion、pin access、IR drop、EM、clock tree、multi-corner multi-mode、低功耗 intent 和 DFM 都更难。架构团队必须早期考虑 floorplan，而不是等 RTL 完成后交给后端。

先进节点的 SRAM 和逻辑缩放不同步。AI 芯片大量 SRAM 可能限制 die area 缩放。一个架构如果主要面积是 SRAM，迁移到更先进节点的收益可能低于预期。

先进节点对 IP 和封装依赖更强。HBM、UCIe、PCIe Gen6、先进 SerDes 和 chiplet 方案会把选择从“工艺节点”扩展成“foundry + IP + package + OSAT + substrate + board”的系统选择。

先进节点的 ECO 成本更高。后期 [ECO](../00_overview/05_glossary.md#eco) 可能受 spare cell、metal layer、timing margin 和 mask 层影响。第一颗芯片应预留 debug 和 workaround 机制，而不是假设首硅完美。

## 28nm/16nm 的现实价值

成熟节点不是落后选择。28nm 常用于成本敏感、模拟/IO 较多、可靠性要求稳定、算力需求不极端的产品。16/14nm FinFET 在性能、功耗和成本之间较平衡，可能适合中等规模边缘 AI、控制芯片、test chip 或 chiplet 中非核心 die。

对创业公司，成熟节点可以用于架构验证、软件栈闭环、IP 集成验证和客户 demo。若目标是数据中心高端 AI 加速器，成熟节点可能无法提供足够能效，但可以作为 test chip 或控制 die 策略的一部分。

## MPW 与 full mask

[MPW Multi Project Wafer](../00_overview/05_glossary.md#mpw-multi-project-wafer) 允许多个设计共享 mask 和 wafer，适合小面积原型、IP 验证和学术/早期创业试验。MPW 成本低于 full mask，但有面积、排期、封装、测试、产量和节点选择限制。

Full mask 适合量产或接近量产的设计，成本高但控制权更强。创业公司可以用 MPW 验证关键 IP 或架构切片，但不要把 MPW 等同于量产路径。MPW 上可行的封装和测试条件，未必代表量产产品可行。

## 关键决策点

第一个决策是产品是否需要领先 PPA。若商业价值来自极致能效和计算密度，先进节点可能必要。若价值来自软件、系统集成、低成本或特定边缘场景，成熟节点可能更合理。

第二个决策是第一颗芯片的目标。它是商业量产芯片、客户评估芯片、架构验证芯片，还是融资里程碑芯片。不同目标对应不同节点策略。

第三个决策是是否承受 respin。先进节点 respin 成本和时间压力大。若团队验证能力不足，直接上最先进节点风险很高。

第四个决策是封装和内存。选择 HBM 往往比选择节点本身更改变成本和供应链。没有封装能力和客户价格支撑，HBM 方案可能不适合第一颗芯片。

## 常见错误

第一个错误是把节点名当成产品竞争力。客户购买的是可用性能、软件、成本和供货，不是“3nm”标签。

第二个错误是只比较逻辑密度。AI 芯片的 SRAM、PHY、IO、封装和热设计常常主导实际成本和面积。

第三个错误是低估 PDK 和 foundry 关系。先进节点不是有钱买 EDA 就能做，PDK、IP、产能和支持都需要关系和资质。

第四个错误是忽略 yield。大 die 在先进节点上良率风险更高，直接影响单颗成本和毛利。

第五个错误是用成熟节点 MPW 的成功推断先进节点 full mask 成功。两者流程、约束和风险完全不同。

## 创业公司视角下的取舍

如果目标是快速建立可信度，可以考虑先做小规模 MPW/test chip，验证核心架构、编译器、SRAM/NoC/接口和硅后流程。如果目标是直接进入高端 AI 市场，则必须准备足够资金、强后端和验证团队、IP vendor 支持、foundry 通道和封装供应链。

可以省的是第一颗芯片的野心，不可以省的是节点选择前的成本模型和供应链验证。工艺节点一旦选定，会锁定 IP、EDA、后端、封装和融资节奏。软件背景创始人应把节点选择视为公司战略决策，而不是技术偏好。

## 典型场景

团队计划做一颗数据中心 AI 芯片，初始选择 3nm，因为希望对标领先 GPU。成本模型显示，除了 mask 和 wafer，还需要 HBM、先进封装、PCIe Gen5/Gen6、复杂电源和散热、商业 EDA、IP 授权、后端外包和硅后实验室。总资金需求远超当前融资能力。

架构团队重新评估后提出两阶段策略：第一阶段在 12/16nm 或 7nm 做较小芯片或 chiplet/test chip，验证核心数据流、编译器和客户 workload；第二阶段在获得客户和融资后进入更先进节点。这个策略牺牲短期宣传，但降低一次性失败风险。

## 后续阅读

- [06_milestones_and_signoffs.md](./06_milestones_and_signoffs.md)
- [后端外包决策](../03_backend_physical_design/09_backend_outsourcing.md)
- [Foundry 关系](../06_cross_cutting_topics/02_foundry_relationships.md)
- [MPW 多项目晶圆策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)
- [Turnkey 服务](../06_cross_cutting_topics/05_turnkey_services.md)

## 参考公开来源

- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [TSMC Annual Reports](https://investor.tsmc.com/english/annual-reports)
- [Synopsys Fusion Compiler](https://www.synopsys.com/implementation-and-signoff/physical-implementation/fusion-compiler.html)
- [Cadence Innovus Implementation System](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/hierarchical-design-and-floorplanning/innovus-implementation-system.html)

## 内容可信度说明

- **公开信息（高可信）**：先进节点、foundry OIP、商业 EDA、PDK/IP 生态、MPW/full mask 概念和工艺节点对 PPA/成本的影响。
- **行业惯例（中可信）**：节点选择流程、多节点比较、IP 可用性检查、成本模型和 foundry/PDK 获取作为关键 gate。
- **经验性观察（中低可信）**：创业公司第一颗芯片不一定应选择最先进节点；成熟节点和 MPW 可用于降低早期风险。
- **不确定/需向资深工程师确认（低可信）**：具体 mask/wafer/IP/EDA 报价、实时 foundry 产能、特定节点良率、先进封装排期、不同 foundry 的 PDK 获取条件。
