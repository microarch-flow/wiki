# Field Support：现场支持

## 前置知识

- 建议先读 [Post-silicon Debug](../04_tapeout_and_post_silicon/05_post_silicon_debug.md)。
- 建议先读 [Volume Ramp](./02_volume_ramp.md) 和 [Supply Chain](./03_supply_chain.md)。
- 建议理解 [RMA](../00_overview/05_glossary.md#rma)、[Failure Analysis](../00_overview/05_glossary.md#failure-analysis)、[Errata](../00_overview/05_glossary.md#errata)、[FAE](../00_overview/05_glossary.md#fae)、[PCN](../00_overview/05_glossary.md#pcn)。

## 核心概念

Field support 是产品进入客户环境后，对问题复现、定位、缓解、修复和质量闭环的工程体系。芯片公司卖出的不只是 die 或封装器件，而是一个包含 silicon、board、firmware、driver、compiler、runtime、SDK、散热、电源和文档的系统能力。

软件背景团队容易把现场支持理解成客服或应用工程。对于芯片公司，现场问题可能意味着 silicon errata、封装失效、板级 SI/PI、ATE escape、客户使用超规格、firmware bug、driver race、编译器错误或系统散热不足。没有结构化 triage，团队会在客户压力下随机派工程师救火。

## 关键活动顺序

第一步是问题接收和分级。FAE 或客户支持收集客户、系统配置、芯片 revision、lot/date code、board revision、firmware/driver/compiler 版本、工作负载、环境条件、日志、复现概率和影响范围。问题应按 severity、客户影响和是否安全/数据正确性风险分级。

一个实用分级模板是：S0 表示数据错误、安全风险、量产停线或大面积不可用，需要小时级响应和高层升级；S1 表示关键客户阻塞或系统稳定性严重受损，需要日级 owner 和固定沟通节奏；S2 表示有 workaround 的功能/性能问题；S3 表示文档、易用性或非阻塞问题。每个 severity 都应绑定工程 owner、FAE owner、客户沟通 cadence 和升级路径，避免销售单独承诺工程结果。

第二步是复现。工程团队在内部环境尽量复现客户问题。如果无法复现，要判断缺失的是硬件条件、温度、电源、traffic pattern、软件版本还是客户数据。AI 芯片经常需要客户 workload 或模型才能复现性能/正确性问题。

第三步是 triage。产品工程、系统软件、硬件、验证、test、质量和供应链共同判断问题类别。优先排除使用条件、版本不匹配和系统集成问题，再进入 silicon debug、FA 或 RMA 流程。

第四步是 workaround 或 fix。软件 workaround 可以是 firmware patch、driver 限制、compiler 避免某条路径、降频降压、禁用某个 feature、调整 thermal policy 或更新客户文档。硬件问题可能需要 errata、RMA、筛选测试增强或 [silicon revision](../04_tapeout_and_post_silicon/08_silicon_revision.md)。

第五步是闭环。每个 field issue 应回写到验证计划、ATE 测试、datasheet、应用笔记、客户 FAQ、下一版芯片需求和质量系统。没有闭环，现场支持只会重复救火。

## 工具和基础设施

常用工具包括 issue tracker、CRM、RMA 系统、QMS、日志采集工具、remote debug 工具、JTAG/trace、性能计数器、crash dump、firmware telemetry、ATE retest、wafer map 查询、lot traceability 数据库、FA 实验室工具和客户版本管理系统。

具体系统举例：Jira/Linear 可做工程 issue，Salesforce/Zendesk/ServiceNow 可做客户 case，Arena/Agile PLM 或 QMS 系统可管理质量闭环，GitLab/GitHub release 可绑定软件版本，Sentry/内部 telemetry 可采集软件异常，Splunk/Elastic 可分析日志。芯片专用数据通常还要连接 ATE/STDF、wafer map、RMA 和 FA 数据库。

AI 芯片应提供可用的现场诊断包：一键采集 driver/firmware/compiler/runtime 版本、PCIe 状态、温度、电压、频率、ECC error、DMA error、NPU error register、性能计数器和最近 workload 摘要。没有诊断包，客户现场问题会被大量沟通成本淹没。

## 角色、周期和成本

主要角色包括 FAE、customer support、product engineer、system software、firmware、driver、compiler、hardware architect、verification、DFT/test、quality、failure analysis、program manager 和 account manager。重大客户问题还需要 CEO/CTO 参与承诺边界。

现场问题的周期从小时到数月不等。软件配置问题可能当天解决；间歇性 silicon bug、封装问题或 ATE escape 可能需要数周 FA；涉及 respin 的问题可能跨季度。成本包括工程人力、客户实验室支持、替换样品、RMA 物流、FA、补充测试、折价、赔偿、客户延期和商誉损失。

量级上，单个复杂客户 issue 可能消耗数人周到数人月；一次高端 FA 或第三方实验室分析可能达到数千到数万美元量级；批量 RMA、替换板卡、客户停线或云集群延期的商业损失可能远高于芯片本身成本。现场支持预算不能只按“客服人数”估算。

## 关键决策点

第一个决策是是否承认为 silicon errata。过早承认可能造成商业和法律压力，过晚承认会损害客户信任。正确做法是基于证据发布限制条件、影响范围和 workaround。

第二个决策是 workaround 是否可接受。如果 workaround 影响性能、功耗或功能，必须判断客户是否接受、是否需要改合同或更新 datasheet。AI 芯片如果通过 compiler workaround 避免 bug，要确保所有客户软件路径都被约束。

第三个决策是是否扩大筛选。发现 field failure 后，可能需要增加 ATE 测试、收紧 test limit、召回某批次或暂停出货。这个决策影响收入，但质量逃逸扩大后成本更高。

第四个决策是是否 respin。现场 bug 如果影响数据正确性、安全、系统稳定或关键客户承诺，软件 workaround 可能只是短期措施。应与 [silicon revision](../04_tapeout_and_post_silicon/08_silicon_revision.md) 决策联动。

## 上下游接口

上游包括 volume ramp 数据、lot traceability、ATE test records、datasheet、errata、软件 release notes 和客户配置。下游包括 RMA、FA report、corrective action、PCN、软件补丁、客户通知、验证计划更新和下一版芯片需求。

现场支持还反向影响销售。客户如果看到问题处理专业、边界清晰、workaround 可验证，即使芯片有 errata 也可能继续合作。相反，含糊回应和反复改口会让客户把技术风险上升为供应商风险。

## 典型场景

某客户报告 AI 推理卡在高负载 48 小时后随机 hang。现场日志显示 driver timeout，但内部短测无法复现。支持团队采集到出问题的卡都来自同一 package lot，并且发生在高温机箱。进一步 retest 发现某电源域 margin 偏低，firmware 在温度升高后切换频率策略触发边界条件。短期 workaround 是限制高温下最高频率并更新 firmware；中期增加 final test 高温筛选；长期在下一版芯片改进电源监控和 reset recovery。

如果团队只让软件工程师不断改 driver，而不追溯 lot 和温度条件，会把硅/封装/电源问题误判成软件 bug。

## 创业公司取舍

创业公司不能为所有客户提供大型原厂级支持，但必须选择可支持的客户数量和场景。第一批客户应愿意共同 debug，有工程能力，且接受清晰的 sample/production 边界。把未成熟芯片卖给支持要求高但不愿共享信息的客户，会消耗团队并制造信誉风险。

可外包的是部分 RMA 物流、FA 实验室和客户现场驻场资源。不能外包的是 issue triage、errata 判断、software workaround 设计、客户承诺和下一版产品修正。

## 常见坑

- 没有版本和 lot 信息，现场问题无法复现和归因。
- 销售为了安抚客户承诺“下周修好”，工程无法兑现。
- 把所有现场问题都丢给软件团队，忽略 silicon、package、power 和 test escape。
- errata 文档不透明，客户踩到已知问题后信任下降。
- workaround 没有进入 regression，后续软件版本又绕回 bug 路径。

## 后续阅读

- [生命周期退出](./05_end_of_life.md)
- [Fast Iteration Realities](../07_for_software_background_founders/05_fast_iteration_realities.md)
- [Software Engineer Pitfalls](../02_frontend_design_and_verification/09_software_engineer_pitfalls.md)

## 参考公开来源

- [JEDEC JESD47 standard page](https://www.jedec.org/standards-documents/docs/jesd47)
- [SEMI T26 supply-chain traceability description](https://store-us.semi.org/products/t02600-semi-t26-specification-for-electronic-supply-chain-traceability-using-distributed-ledger-technology-3)
- [Texas Instruments reliability testing overview](https://www.ti.com/quality-reliability/reliability/testing.html)

## 内容可信度说明

- **公开信息（高可信）**：RMA、failure analysis、errata、PCN、lot traceability 和质量闭环的基本概念。
- **行业惯例（中可信）**：field issue triage、workaround、FA report、corrective action 和客户沟通流程。
- **经验性观察（中低可信）**：AI 芯片现场问题常跨 silicon、软件、板卡、散热和客户 workload，不能按单一团队处理。
- **不确定/需向资深工程师确认（低可信）**：不同客户的 SLA、赔偿条款、RMA 流程、现场数据权限和法律披露要求。
