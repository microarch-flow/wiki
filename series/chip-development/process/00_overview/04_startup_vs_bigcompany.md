# 创业公司 vs 大公司的流程差异

## 前置知识

- 建议先读 [01_full_lifecycle.md](./01_full_lifecycle.md)、[02_roles_and_teams.md](./02_roles_and_teams.md)、[03_cost_structure.md](./03_cost_structure.md)。
- 术语参考 [05_glossary.md](./05_glossary.md)。

## 核心差异

大公司用流程降低规模化风险，创业公司用取舍换速度和生存概率。两者都不能违反物理约束。区别在于，大公司可以并行投入多个团队、购买完整工具链、锁定 foundry 产能、维护长期 IP 关系，并承受一次项目延迟。创业公司必须更早做出范围取舍，更清楚哪些风险必须内部掌握，哪些工作可以外包。

对“快速迭代芯片公司”来说，正确目标不是把 18 到 24 个月的传统流程机械压缩成几个月，而是把单次迭代目标变小，把架构和 RTL 生成自动化，把验证和 signoff 证据系统化，把不可变的制造周期前置规划。

## 产品定义上的差异

大公司通常有稳定客户、销售渠道、历史芯片数据和平台路线图。产品定义可以围绕既有生态优化。创业公司缺少这些资产，最容易犯两个错误：一是按论文或 benchmark 定义芯片，忽略客户实际部署；二是按大公司旗舰芯片设目标，忽略自身软件、供应链和资金边界。

创业公司更适合选择一个明确 wedge market，例如特定模型推理、特定边缘设备、特定企业 workload 或特定开源软件生态。第一颗芯片的目标应当是验证商业和技术闭环，而不是覆盖所有场景。

产品定义还要匹配融资节奏。大公司可以为长期平台投入多个版本，创业公司第一颗芯片通常要承担融资、客户验证和团队信誉三重任务。范围过大导致延期，可能比小幅性能退让更致命。

## 架构与规格上的差异

大公司可以做复杂平台，支持多代复用，维护大量兼容性。创业公司应避免第一版规格过宽。每增加一个接口、数据类型、低功耗状态、虚拟化模式或异常行为，都会增加 RTL、验证、DFT、软件和硅后成本。

这并不意味着创业公司只能做简单芯片，而是要把复杂度集中在真正差异化的地方。对于 AI 芯片，差异化可能在编译器可用性、内存层级、算子映射、能效或特定模型端到端延迟，而不一定在所有外设都自研。

规格管理也不同。大公司常有专门配置管理和跨团队变更委员会，创业公司则容易在 Slack/飞书里口头改需求。硬件规格口头变化会造成 RTL、验证、软件、后端不同步，最终形成难以定位的系统 bug。

## 流程和 signoff 的差异

大公司有完整 signoff gate，例如 architecture review、RTL freeze、verification closure、DFT signoff、physical signoff、tapeout readiness review、bring-up readiness review。创业公司经常觉得这些流程“官僚”。实际上，流程的价值是让风险显性化。创业公司可以简化文档形式，但不能取消关键问题：

- 规格是否冻结，未冻结项是否有 owner 和截止时间。
- RTL 是否 lint clean，CDC/RDC 是否无高风险问题。
- 覆盖率缺口是否被审查，waiver 是否合理。
- timing exception 是否可信，不是为了过 STA 随便 false path。
- DRC/LVS/IR/EM 是否 signoff，waiver 是否可接受。
- bring-up 所需 firmware、driver、board、lab、test plan 是否准备好。

创业公司正确的流程裁剪方式是保留“硬证据”，减少“低价值仪式”。例如可以不用大公司几十页模板，但必须有 architecture spec、verification plan、coverage report、CDC report、DFT plan、timing report、physical signoff checklist 和 bring-up checklist。

## 外包策略差异

大公司通常内部掌握大部分关键能力，并外包非核心或产能波峰。创业公司更依赖设计服务、turnkey、IP vendor、OSAT 和顾问。外包可以换速度，但也会引入信息不对称。

可以外包执行，不应外包判断。比如后端 placement/routing 可以由服务公司做，但内部必须有人能审 timing、floorplan、congestion、IR drop 和 ECO。IP 可以购买，但内部必须知道 IP 的约束、验证证据、版本风险和集成责任。测试程序可以由 OSAT 或测试服务公司开发，但内部必须理解 fault coverage、测试时间和 yield 数据。

外包最容易失败的地方是交付物定义不清。合同里写“RTL-to-GDS”不够，必须明确 PPA 目标、signoff corner、waiver 规则、ECO 响应、报告格式、责任边界、工具版本、PDK 版本和 tapeout 交付清单。

## 自动化与 AI Agent 的真实边界

自动化可以加速重复、结构化、可验证的任务，例如 spec consistency check、RTL 模板生成、register map 生成、lint 修复建议、test generation、coverage triage、仿真回归调度、bug clustering、EDA report parsing、设计空间搜索和文档同步。

自动化难以替代的是工程判断和物理反馈：架构取舍、客户需求判断、timing exception 合法性、CDC waiver 合法性、DFT coverage 是否足够、foundry rule 解释、封装 SI/PI、硅后异常归因、可靠性认证和供应链谈判。

最危险的自动化误区是“能生成 RTL 等于能做芯片”。生成 RTL 只是开始。还要证明它可综合、可验证、可测、可布线、可调试、可量产。

Agent 生成 RTL 也不能替代 signoff owner。每个 waiver、timing exception、CDC 结构、DFT 覆盖缺口和硅后 debug 取舍，都必须有人承担工程责任。

## 成本与融资节奏差异

大公司可以把芯片项目放在多年 roadmap 中摊销。创业公司必须把技术里程碑与融资里程碑对齐。投资人和客户通常不会只看 PPT 上的 TOPS，而会看 demo、软件栈、样片、性能功耗数据、客户试用和供应链可信度。

第一颗芯片如果选择先进节点 full mask，现金压力会非常大。更务实的路径可能是 FPGA/emulation 验证软件栈，MPW 验证关键 IP 或小型 test chip，再做商业 SoC。若业务必须依赖先进节点能效，则需要更强融资、foundry 关系和团队履历支撑。

## 典型流程对比场景

大公司做下一代 AI SoC，会并行启动架构、软件、IP、验证、后端、封装和客户 enablement。多个团队有成熟流程，供应商提前锁定，若某个 block 延迟，可以调资源。

创业公司做第一颗芯片，如果照搬大公司旗舰方案，会同时踩中先进节点、HBM、高速 SerDes、大 die、复杂软件栈和高验证成本。更合理的做法是定义最小可销售或最小可验证芯片，把差异化 NPU 做深，把外围风险降到可控。错误选择的后果不是“晚几个月”，而是 tapeout 前发现收不住，或者首硅回来无法 demo，进而影响融资和客户信任。

## 创业公司应保留的硬门槛

创业公司可以轻流程，但必须保留硬门槛。至少包括 architecture signoff、RTL freeze、verification signoff、DFT signoff、physical signoff、tapeout readiness、bring-up readiness、production readiness。每个门槛都要有 owner、checklist、已知风险和接受风险的人。

如果 founder 想压缩流程，应该问的问题不是“这个 review 能不能取消”，而是“这个 review 要防止哪个昂贵错误；有没有更轻量但同样有效的证据”。如果没有替代证据，取消流程通常只是把风险推迟。

## 后续阅读

- [03_cost_structure.md](./03_cost_structure.md)
- [../06_cross_cutting_topics/05_turnkey_services.md](../06_cross_cutting_topics/05_turnkey_services.md)
- [../07_for_software_background_founders/04_first_chip_pragmatics.md](../07_for_software_background_founders/04_first_chip_pragmatics.md)
- [../07_for_software_background_founders/05_fast_iteration_realities.md](../07_for_software_background_founders/05_fast_iteration_realities.md)

## 内容可信度说明

- **公开信息（高可信）**：芯片流程 gate、EDA/signoff 类别、制造和封测不可即时迭代的物理现实。
- **行业惯例（中可信）**：大公司和创业公司组织方式差异、外包执行但保留判断的原则。
- **经验性观察（中低可信）**：创业公司第一颗芯片范围控制、融资里程碑与技术里程碑绑定、AI Agent 加速边界。
- **不确定/需向资深工程师确认（低可信）**：具体公司可接受的流程裁剪程度、foundry 对初创客户支持力度、投资人对不同技术里程碑的接受度。
