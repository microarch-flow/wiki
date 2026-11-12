# End of Life：生命周期退出

## 前置知识

- 建议先读 [Supply Chain](./03_supply_chain.md)。
- 建议先读 [Field Support](./04_field_support.md)。
- 建议理解 [EOL](../00_overview/05_glossary.md#eol)、[PCN](../00_overview/05_glossary.md#pcn)、[Last Time Buy](../00_overview/05_glossary.md#last-time-buy)、[Revision](../00_overview/05_glossary.md#revision)、[Traceability](../00_overview/05_glossary.md#traceability)。

## 核心概念

End of Life 是产品停止新设计导入、停止接受新订单、最后采购、最后发货和长期支持结束的管理流程。它不是“卖不动就停”，而是面向客户、供应商、库存、质量、软件和法律承诺的受控退出。

芯片生命周期通常比软件版本长。客户把芯片设计进系统后，替换成本高，尤其是工业、服务器、网络设备和汽车客户。即使你的创业公司要快速迭代，也不能假设客户愿意每几个月换硬件。EOL 管理能力会影响客户是否愿意在第一代产品上下注。

## 关键活动顺序

第一步是生命周期状态定义。常见状态包括 active、not recommended for new design、last time buy、last time ship、support only 和 discontinued。每个状态要对应销售限制、库存策略、软件支持、质量支持和客户通知。

第二步是 EOL 触发评估。触发因素可能是新一代芯片替代、需求下降、毛利过低、关键供应商停产、foundry 工艺/封装材料退出、质量风险、法规变化、IP license 限制或公司战略转向。EOL 不应只由销售数据决定，也要看供应链和质量风险。

第三步是客户影响分析。团队要识别哪些客户在用、库存多少、合同是否有供货年限、是否需要替代型号、是否需要软件迁移、是否有安全或可靠性义务。对大客户，EOL 通常需要提前通知，并给出 last time buy 和 last time ship 日期。

第四步是供应链和库存计划。运营团队计算剩余 wafer、封装材料、ATE capacity、成品库存和备件需求。last time buy 可能带来短期订单高峰，但如果 forecast 错误，会形成无法消化的库存或客户缺货。

第五步是支持退出。即使硬件停止出货，仍可能需要 firmware/driver/compiler bug fix、安全补丁、RMA、FA 和文档维护。支持结束日期应清晰写入客户沟通和内部计划。

## 工具和文档

常用工具包括 PLM、ERP、CRM、QMS、PCN/PDN 系统、库存系统、合同管理、客户通知模板和软件 release 管理系统。关键文档包括 product change notification、product discontinuance notice、last time buy notice、last time ship notice、replacement guide、migration note、errata 和 support policy。

具体系统举例：SAP/Oracle/NetSuite 管库存和订单，Arena/Oracle Agile PLM/Siemens Teamcenter 管产品结构和变更，Salesforce 管客户通知和机会影响，Jira/GitHub/GitLab 管软件维护任务，DocuSign/合同系统管理供货承诺，QMS 系统记录 PCN/PDN 和客户确认。

对 AI 芯片，迁移文档很重要。新芯片可能有不同算子支持、内存容量、compiler 行为、driver API、功耗策略和性能模型。只告诉客户“新型号更快”不够，必须说明软件迁移和系统验证成本。

## 角色、周期和成本

主要角色包括 product management、operations、supply chain、quality、legal、sales、FAE、finance、software release manager 和 customer support。EOL 是商业决策，不是单纯工程决策。

周期通常是数月到数年，取决于市场和客户合同。消费类产品退出较快，工业/服务器/汽车客户通常要求更长生命周期和提前通知。成本包括库存持有、最后批次生产、长期测试支持、RMA、软件维护、客户迁移支持和潜在合同责任。

提前通知窗口通常是月级到年级，而不是周级。JEDEC JESD48 提供产品停产通知的行业参考，实际要求还取决于客户合同和市场：消费类客户可能接受较短窗口，工业、服务器、通信和汽车客户通常要求更长 last-time-buy/last-time-ship 安排。last-time-buy 的现金占用可能达到数月到一年以上需求量，对创业公司是实质融资和库存风险。

## 关键决策点

第一个决策是何时宣布 not recommended for new design。如果太早，会影响现有销售；太晚，会让新客户刚导入就遇到 EOL，损害信任。创业公司需要把产品 roadmap 和供应风险透明化到适当程度。

第二个决策是 last time buy 数量。数量太少会断供，数量太多会压现金。芯片库存不能像软件 license 一样无限复制，且硬件 revision 或客户需求变化可能让库存失去价值。

第三个决策是替代产品策略。替代产品如果 pin compatible、软件兼容、性能更好，客户迁移成本低；如果架构和软件栈大变，客户会把 EOL 当成重新选型机会。

第四个决策是支持边界。是否继续修 driver、compiler、firmware、安全问题和现场 bug，必须与客户合同、收入、团队资源和下一代产品节奏匹配。

## 上下游接口

上游包括 supply chain 状态、field support 数据、质量风险、客户 forecast、产品路线图和财务模型。下游输出包括 EOL notice、last time buy/ship plan、替代型号、库存策略、长期支持计划和客户迁移计划。

EOL 也会反向影响新产品定义。V1 的客户迁移痛点应进入 V2 的兼容性目标：驱动 API 是否稳定、compiler 是否支持向后兼容、板卡接口是否复用、封装 pinout 是否尽量兼容。

## 典型场景

V1 AI 推理芯片采用 16nm 工艺和成熟封装，已被两个客户导入边缘服务器。V2 使用 7nm 并改了内存接口，性能提升明显，但 V1 的封装基板供应商宣布某材料即将停产。团队如果立即停止 V1，会让客户的已设计系统断供；如果继续无限支持，会占用现金和工程资源。务实做法是宣布 V1 not recommended for new design，给现有客户 last time buy 窗口，准备 V2 migration guide，并保证一定期限内的软件 bug fix 和 RMA。

如果团队没有提前管理 EOL，客户可能在量产系统中突然缺料，后续不会再信任你的 roadmap。

## 先进节点与成熟节点差异

先进节点产品的 EOL 风险常来自产能、封装/HBM 供应、成本压力和下一代节点迁移。成熟节点产品的生命周期可能更长，但也可能遇到老工艺、封装材料或测试平台退出。成熟节点不等于永远可买，供应商 PCN/PDN 仍需持续监控。

## 创业公司取舍

快速迭代公司要区分内部迭代速度和客户生命周期。内部可以每年甚至更快推出新 silicon，但客户希望软件接口、系统集成和供货承诺稳定。对第一颗芯片，最好在销售前就明确 sample、early access、production 和 long-term support 的边界，避免把实验性产品卖成长期量产承诺。

可以外包物流和部分库存管理，但不能外包 roadmap 信任。EOL 沟通如果粗暴，客户会把你视为不可依赖供应商。

## 常见坑

- 新产品发布后立刻忽视旧产品客户，导致现场问题无人处理。
- 没有 last time buy 计划，供应商停产时被动断供。
- 替代产品软件不兼容，客户迁移成本接近重新设计。
- EOL 通知只发销售邮件，没有工程迁移文档和支持政策。
- 库存策略只看销量，不看 revision、客户合同和质量风险。

## 后续阅读

- [Startup vs Big Company](../00_overview/04_startup_vs_bigcompany.md)
- [First Chip Pragmatics](../07_for_software_background_founders/04_first_chip_pragmatics.md)
- [Fast Iteration Realities](../07_for_software_background_founders/05_fast_iteration_realities.md)

## 参考公开来源

- [JEDEC JESD48 product discontinuance standard page](https://www.jedec.org/standards-documents/docs/jesd48)
- [SEMI T26 supply-chain traceability description](https://store-us.semi.org/products/t02600-semi-t26-specification-for-electronic-supply-chain-traceability-using-distributed-ledger-technology-3)
- [AEC-Q100 overview by Renesas](https://www.renesas.com/en/products/automotive-products/aec-q100)

## 内容可信度说明

- **公开信息（高可信）**：EOL、PCN/PDN、last time buy、last time ship、traceability 和产品生命周期管理的基本概念。
- **行业惯例（中可信）**：生命周期状态、客户通知、替代产品、长期支持和库存计划。
- **经验性观察（中低可信）**：快速迭代芯片公司必须把内部 silicon cadence 与客户硬件生命周期分开管理。
- **不确定/需向资深工程师确认（低可信）**：具体客户通知提前期、合同义务、地区法规、长期供货承诺和软件安全维护责任。
