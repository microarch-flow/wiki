# Foundry Relationships：Foundry 关系

## 前置知识

- 建议先读 [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)。
- 建议先读 [Tapeout 流程](../04_tapeout_and_post_silicon/01_tapeout_process.md)。
- 建议理解 [Foundry](../00_overview/05_glossary.md#foundry)、[PDK](../00_overview/05_glossary.md#pdk)、[Mask Cost](../00_overview/05_glossary.md#mask-cost)、[Wafer Start](../00_overview/05_glossary.md#wafer-start)、[PCN](../00_overview/05_glossary.md#pcn)。

## 核心概念

Foundry 关系决定你能否获得 PDK、工艺支持、IP ecosystem、tapeout 入口、产能、价格、质量信息和问题响应。芯片创业公司不是“选一个节点下单”就能制造芯片，尤其在先进节点，foundry 准入和生态支持本身就是商业资源。

PDK 是必要条件但不是充分条件。真实项目还需要 design rule 解释、reference flow、standard cell/SRAM/IO collateral、IP vendor 支持、waiver 处理、tapeout portal、mask review、failure analysis、yield learning 和量产接口。

## 关系建立路径

第一种路径是直接建立 foundry account。适合有资深团队、融资能力、明确产品计划和较大产能预期的公司。优点是透明度和长期能力强；缺点是门槛高、商务谈判复杂。

第二种路径是通过设计服务或 turnkey 供应商进入。供应商已有 foundry 关系，可以帮助获取 PDK、执行后端、提交 tapeout 和管理制造。优点是快；缺点是你对 flow、成本和问题定位的可见性降低。

第三种路径是先用 MPW、开放 PDK 或成熟节点服务积累经验。适合第一颗 test chip 或团队训练。优点是成本低；缺点是与先进节点量产路径差距大，不能直接证明 full-chip 量产能力。

## 关键活动顺序

第一步是 business fit。Foundry 会关心产品类型、节点、预计 wafer volume、资金、团队经验、IP 需求、量产计划和合规风险。创业公司要准备清楚产品路线图和商业可信度。

第二步是 NDA 和 PDK access。PDK、工艺规则和 IP collateral 通常受严格 NDA 限制，不能开源，也不能随意给 agent 或外包方使用。开源芯片公司要特别设计代码、文档和 PDK collateral 的隔离机制。

第三步是 ecosystem selection。选择 standard cell、SRAM compiler、IO、PLL、SerDes、HBM/DDR/PCIe PHY、ESD、封装选项和 EDA reference flow。工艺节点的可用 IP 生态往往比晶体管性能更实际。

第四步是 tapeout interface。项目接近流片时需要明确 data prep、waiver、DRC/LVS deck、seal ring、scribe line、mask layer、lot setup、wafer quantity、MPW/dedicated、shipping 和 post-silicon support。

第五步是量产和变更管理。量产后要处理 yield review、PCN、process change、capacity reservation、quality excursion 和 supply continuity。Foundry 关系不是 tapeout 后结束，而是进入更长期的运营接口。

## 角色、周期和成本

主要角色包括 CEO/BD、CTO、program manager、foundry interface、physical design lead、DFT/test lead、quality、legal、finance 和 supply chain。先进节点 foundry 关系通常需要高层参与，因为它涉及产能、信用、预付款、NDA、合规和长期商业承诺。

周期从数周到数月甚至更长。获取 PDK、签 NDA、评估 IP、建立 EDA flow 和确认 tapeout slot 都需要时间；先进节点、热门产能或复杂合规审查可能更久。成本包括 PDK/IP access、EDA、mask、wafer、工程服务、封装测试、产能预留和商务条款。

先进节点 full mask 的公开粗量级通常是百万到千万美元级，但这不是报价依据。MPW/shuttle、engineering wafer、dedicated mask、base-layer respin 和 metal-only ECO 的成本差异很大；7nm、5nm、3nm 的 mask、wafer、IP 和 signoff 成本也不是线性关系。商业决策必须把 mask、wafer、封装、测试、IP、EDA、良率和 schedule risk 分开建模。

## 关键决策点

第一个决策是节点和 foundry 是否匹配业务阶段。7nm 以下有性能优势，但 mask、IP、EDA、封装和良率风险都高。第一颗芯片是否必须先进节点，应由 workload、功耗、客户价值和资金决定，而不是创业叙事决定。

第二个决策是直接关系还是代理路径。通过 turnkey 快，但要在合同中明确数据可见性、IP ownership、waiver 审批、GDS ownership、良率数据、问题响应和供应链透明度。

第三个决策是 PDK/保密边界。全栈开源公司必须确认哪些内容能开源：RTL、编译器、验证环境可以开源；PDK、foundry rule decks、商业 IP、library、SRAM compiler 和部分 timing model 通常不能开源。

第四个决策是 capacity commitment。提前锁产能会占现金；不锁可能拿不到 wafer start。创业公司要把客户订单可信度和现金流纳入决策。

如果节点或 foundry 选择错误，后果不是单点成本增加，而是全项目被锁定。比如选择了高性能节点但缺少可用 SerDes/HBM PHY，架构会被迫降级；选择了热门先进封装但没有 allocation，硅片可能可用但无法形成系统；选择了缺少客户认可的 foundry，后续销售和 qualification 会受阻。

## 上下游接口

上游来自产品定位、节点选择、IP 策略和融资计划。下游影响后端、tapeout、封装、量产和客户交付。Foundry 的工艺规则、IP 可用性和交期会反向约束架构。例如想用某高速接口，但对应 PHY 在目标节点不可用或支持不足，架构计划就必须调整。

## 典型场景

团队计划做 5nm AI 加速器并全栈开源 RTL/编译器。与 foundry 接触后发现，PDK、SRAM compiler、标准单元、IO 和物理验证 deck 都在 NDA 下，不能进入公开 repo。正确策略是把开源边界定义为 synthesizable RTL、模型、软件、文档和不含 NDA collateral 的验证环境；同时建立私有 signoff repo 管理 PDK-dependent flow。

## 创业公司取舍

创业公司要把 foundry 关系当成融资和产品路线图的一部分。没有 credible foundry path 的先进节点计划，投资人和客户都会质疑可交付性。早期可以通过成熟节点 MPW 或 turnkey 证明能力，但如果商业目标是高性能 AI 芯片，最终必须建立更直接的 foundry/IP/OSAT 关系。

## 常见坑

- 把“能下载 PDK”当成“能流片和量产”。
- 忽略 IP ecosystem，最后发现 PHY/SRAM/IO 不可用或成本不可接受。
- 没有 PDK 保密隔离，开源策略与 NDA 冲突。
- Foundry/turnkey 合同没有规定良率数据和问题响应。
- 只谈 wafer price，不谈 mask、waiver、FA、PCN、产能和封测接口。

## 后续阅读

- [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)
- [MPW 策略](./04_mpw_shuttle_strategy.md)
- [Turnkey 服务](./05_turnkey_services.md)
- [供应链](../05_production_and_lifecycle/03_supply_chain.md)

## 参考公开来源

- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [TSMC IP Alliance](https://www.tsmc.com/english/dedicatedFoundry/oip/ip_alliance)
- [GlobalFoundries design enablement overview](https://gf.com/gf-ecosystem/design-enablement/)

## 内容可信度说明

- **公开信息（高可信）**：foundry、PDK、OIP/ecosystem、IP alliance、tapeout 和 wafer start 的基本概念。
- **行业惯例（中可信）**：foundry account、NDA、PDK access、waiver、capacity commitment 和 turnkey 进入路径。
- **经验性观察（中低可信）**：开源芯片公司必须把公开 repo 与 NDA collateral 严格隔离。
- **不确定/需向资深工程师确认（低可信）**：具体 foundry 准入门槛、PDK 条款、报价、产能承诺和先进节点商务条件。
