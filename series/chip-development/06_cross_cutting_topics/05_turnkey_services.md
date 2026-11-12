# Turnkey Services：设计服务与 Turnkey

## 前置知识

- 建议先读 [后端外包决策](../03_backend_physical_design/09_backend_outsourcing.md)。
- 建议先读 [Foundry 关系](./02_foundry_relationships.md)。
- 建议理解 [Turnkey](../00_overview/05_glossary.md#turnkey)、[Foundry](../00_overview/05_glossary.md#foundry)、[OSAT](../00_overview/05_glossary.md#osat)、[Signoff](../00_overview/05_glossary.md#signoff)、[NRE](../00_overview/05_glossary.md#nre)。

## 核心概念

Turnkey 服务是供应商承担从某个设计阶段到流片、封装、测试甚至量产交付的一揽子服务。范围可以很窄，例如只做后端 P&R；也可以很宽，例如 RTL freeze 后由供应商完成 synthesis、DFT、physical design、tapeout、OSAT、ATE 和供应链管理。

Turnkey 的价值是速度、经验和供应链入口；风险是黑盒、依赖、成本不透明和 ownership 模糊。创业公司使用 turnkey 是合理的，但必须知道外包的是执行，不是产品责任。

## 服务类型

前端设计服务包括 RTL implementation、IP integration、UVM verification、formal、DFT insertion 和 synthesis。适合补足短期人力，但核心架构和验证标准不应完全外包。

后端设计服务包括 floorplan、placement、CTS、routing、STA closure、IR/EM、DRC/LVS、DFM 和 tapeout package。这是最常见外包项，尤其对缺少先进节点后端团队的创业公司。

制造 turnkey 包括 foundry interface、mask、wafer、OSAT、final test、reliability、logistics 和量产数据。它能降低运营复杂度，但会降低你对成本、良率和问题定位的直接可见性。

IP/平台 turnkey 包括已有 SoC platform、NoC、CPU subsystem、security、debug、DDR/PCIe/Ethernet 子系统和软件 BSP。它能缩短周期，但会锁定架构、许可证和供应商路线。

## 关键活动顺序

第一步是明确外包边界。写清楚输入、输出、质量标准、工具版本、交付物、review 节点、waiver 审批、IP ownership、数据可见性和变更流程。不要只写“完成后端”。

第二步是供应商评估。看节点经验、类似芯片案例、团队资深度、foundry/OSAT 关系、工具 license、质量体系、项目经理能力、数据透明度和 reference customer。销售材料不等于交付能力。

第三步是合同和里程碑。按 milestone 付款：RTL handoff review、synthesis clean、DFT signoff、floorplan approval、timing closure、physical signoff、tapeout、silicon bring-up support。每个 milestone 要有可验证 artifact。

验收证据要具体。RTL handoff 应包含 RTL freeze tag、lint/CDC 状态、known issue 和约束假设；synthesis clean 应包含面积、频率、timing、congestion estimate 和 unmapped/undriven 检查；DFT signoff 应包含 scan/MBIST/LBIST coverage、pattern count、test mode constraints；floorplan approval 应包含 macro/IO/power grid/congestion/thermal 假设；physical signoff 应包含 STA corner、DRC/LVS、IR/EM、SI、DFM、waiver 和 ECO 清单。每项都要指定客户和供应商谁签字，失败时进入 change order 还是供应商返工。

第四步是执行治理。内部必须参加 weekly review、issue triage、ECO review、waiver review 和 signoff review。外包项目失败的常见原因不是供应商不会做，而是客户没有清晰输入和快速决策。

第五步是知识回收。项目结束后要拿回 scripts、reports、constraints、waiver rationale、lessons learned、test collateral 和数据模型。否则 V2 仍然从零依赖供应商。

## 工具、角色和成本

供应商可能使用 Synopsys、Cadence、Siemens、Ansys 等商业工具，也可能用 foundry reference flow。内部角色包括 technical owner、program manager、RTL/verification owner、PD owner、DFT/test owner、legal、finance 和 supply chain。不要让纯商务人员管理 turnkey 技术交付。

周期上，供应商评估和合同谈判通常需要数周；后端/DFT 执行取决于设计规模和 RTL 稳定度，可能是数月；制造 turnkey 会贯穿 tapeout、fab、封装、测试和量产爬坡，周期跨越多个季度。若 RTL 和 spec 不稳定，任何固定报价都会通过 change order、延期或质量下降体现出来。

成本模式包括 fixed price、time and material、milestone payment、NRE plus unit margin、royalty 或 manufacturing markup。后端/DFT/physical signoff 服务可能是数十万到数百万美元量级；先进节点、复杂 SoC、HBM/SerDes、紧急 schedule 和制造 turnkey 会更高。低报价通常意味着 scope 少、风险转嫁或后续 change order。

## 关键决策点

第一个决策是外包哪些能力。创业公司可以外包后端执行、DFT 插入、封装测试执行，但产品架构、验证 signoff 标准、IP 决策、客户质量和量产承诺应内部掌握。

第二个决策是 black-box vs transparent。黑盒 turnkey 快但危险。至少要要求中间报告、脚本、关键约束、waiver 和 review 权限。

第三个决策是供应商激励。若供应商按 tapeout 收费，可能倾向于把风险带到硅后；若按量产良率或长期制造服务收费，激励更接近产品成功，但成本更复杂。

第四个决策是退出机制。合同中要规定资料交付、IP ownership、未完成里程碑、质量缺陷、人员替换、保密和终止后的数据归还。

错误 turnkey 决策的后果通常在硅后暴露：供应商说按合同交付了 GDS，但 bring-up 失败时没有足够 waiver rationale、约束历史和 ECO 记录；量产良率低时你拿不到 wafer map 和 test 数据；V2 想换供应商时缺少 scripts 和 flow 知识，迁移成本接近重做。

## 上下游接口

上游输入包括 spec、RTL、constraints、UPF、IP collateral、verification status、DFT plan、floorplan assumptions 和 schedule。下游输出包括 netlist、GDS/OASIS、reports、waiver、test collateral、manufacturing data、bring-up support 和量产数据。

输入不清会直接转化为 change order 和 schedule slip。比如 RTL 还在大改就交给后端，供应商只能不断重跑，成本和关系都会恶化。

## 典型场景

一家 AI 芯片创业公司内部有架构、C model、RTL generator 和编译器，但没有 7nm 后端经验。合理方案是内部完成 spec、RTL、验证计划、DFT 架构和 top-level floorplan 约束，外包 P&R/signoff，并要求每周 timing/area/power/DRC/IR dashboard。tapeout 后，供应商支持 bring-up 和 ECO，但内部保留 bug triage 和 V2 架构决策。

错误方案是把“C model 生成的 RTL”直接交给 turnkey，期待供应商补完验证、约束、DFT、后端和 tapeout。供应商可能能把它推到 GDS，但硅后 bug 的责任边界会非常模糊。

## 创业公司取舍

Turnkey 能让创业公司少走弯路，但不能让你跳过学习。第一颗芯片可以利用 turnkey 降低执行风险，同时建立内部 checklist、review 能力和数据基础设施。长期要逐步把核心判断能力内化，否则每一代芯片都会被供应商节奏和报价控制。

## 常见坑

- 合同只写交付 GDS，不写 signoff 标准和 waiver 审批。
- 供应商中间结果不可见，项目到最后才暴露问题。
- 内部 RTL/spec 不稳定，导致外包成本失控。
- 不拿回脚本和报告，下一代无法复用经验。
- 认为外包能替代验证，硅后责任无法界定。

## 后续阅读

- [后端外包决策](../03_backend_physical_design/09_backend_outsourcing.md)
- [Foundry 关系](./02_foundry_relationships.md)
- [量产供应链](../05_production_and_lifecycle/03_supply_chain.md)
- [第一颗芯片的务实建议](../07_for_software_background_founders/04_first_chip_pragmatics.md)

## 参考公开来源

- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [ASE technology services overview](https://www.aseglobal.com/en/technology)
- [Synopsys design services overview](https://www.synopsys.com/services/design-services.html)

## 内容可信度说明

- **公开信息（高可信）**：turnkey、design service、foundry/OSAT interface、EDA signoff 的基本服务类型。
- **行业惯例（中可信）**：milestone-based delivery、waiver review、data visibility、fixed price vs T&M 等外包治理方式。
- **经验性观察（中低可信）**：创业公司可以外包执行，但不能外包产品判断和质量责任。
- **不确定/需向资深工程师确认（低可信）**：具体供应商能力、报价、合同条款、责任限制和制造 markup。
