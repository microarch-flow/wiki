# 里程碑与签核

## 前置知识

- 建议先读 [市场与 Workload 分析](./01_market_and_workload_analysis.md)。
- 建议先读 [规格定义](./02_spec_definition.md)。
- 建议先读 [架构探索](./03_architecture_exploration.md)、[IP 策略](./04_ip_strategy.md) 和 [工艺节点选择](./05_process_node_selection.md)。

## 为什么早期也需要 Signoff

[Signoff](../00_overview/05_glossary.md#signoff) 不只发生在流片前。产品定义和架构阶段也需要签核，因为这一阶段的输出会锁定下游成本、团队结构、[IP](../00_overview/05_glossary.md#ip) 合同、[EDA](../00_overview/05_glossary.md#eda) 预算、工艺节点、封装和验证范围。

早期签核不是官僚流程，而是风险控制机制。它强迫团队把假设写下来，把不确定性显式化，把跨团队接口对齐，并明确“现在进入下一阶段是否值得”。对创业公司，这尤其重要，因为资金和时间不足以承受无限探索。

## 推荐里程碑

| 里程碑 | 目标 | 关键交付物 | 进入下一阶段条件 |
|---|---|---|---|
| M0 概念立项 | 判断是否值得探索 | 市场假设、目标客户、初始 workload | 有明确问题和潜在客户价值 |
| M1 [Workload](../00_overview/05_glossary.md#workload) 冻结 v0 | 建立工程输入 | workload pack、benchmark 脚本、trace | 架构团队可运行模型 |
| M2 产品规格草案 | 定义产品边界 | [PRD](../00_overview/05_glossary.md#prd)、must/should/could、不可支持列表 | 指标可测量，范围可控 |
| M3 架构候选收敛 | 比较主要架构方案 | 性能模型、PPA 估算、风险矩阵 | 有 1 到 2 个候选方案 |
| M4 IP/节点预签核 | 验证可制造路径 | IP 清单、节点建议、成本模型 | 关键 IP 和 PDK 路径可信 |
| M5 架构规格冻结 | 进入微架构和 RTL | 架构规格、软件契约、验证映射 | 关键接口稳定 |
| M6 项目执行批准 | 正式投入主开发 | 预算、人力、排期、风险接受 | 公司层面接受成本和风险 |

这些里程碑名称可以按公司习惯调整。重要的是每个 gate 都有可检查的输入、owner、评审人、结论和后续 action。

## M0：概念立项

M0 的目标是避免团队在没有客户和问题定义的情况下进入技术自嗨。它应回答：目标客户是谁，为什么现有 GPU/CPU/FPGA/ASIC 不满足，客户愿意为哪项指标付费，公司有什么差异化能力。

M0 不要求完整规格，但必须有清晰假设。例如“面向边缘服务器小 batch LLM decode，目标是降低每 token 能耗和部署成本”。如果只写“做 AI 芯片”或“做开源 [NPU](../00_overview/05_glossary.md#npu)”，还不足以进入工程探索。

M0 参与者包括创始人、产品、系统架构、商务和核心技术负责人。输出应包括目标市场、竞品、客户访谈摘要、第一批 workload 候选和初始商业假设。

## M1：Workload 冻结 v0

M1 的目标是把市场语言变成架构输入。冻结 v0 不表示 workload 永远不变，而是提供一个共同基线。没有这个基线，架构团队、编译器团队和产品团队会拿不同模型争论。

交付物包括 workload list、模型版本、输入分布、精度要求、trace、baseline 性能、benchmark 脚本和测量方法。对 AI 芯片，必须同时记录端到端指标和核心 kernel 指标。只记录 matmul 性能是不够的。

签核问题包括：这些 workload 是否代表目标客户，是否可复现，是否覆盖关键瓶颈，是否有不可支持项，是否能驱动验证和硅后 benchmark。

## M2：产品规格草案

M2 的目标是明确产品边界。PRD 和初始规格需要把 workload 转成性能、功耗、接口、软件、封装、供货和成本目标。这里必须区分 must、should 和 could。

M2 评审重点不是追求完整，而是判断范围是否可控。若 must 列表过长，后续 RTL 和验证会失控。若 must 列表太虚，团队无法执行。

交付物包括 PRD、产品指标表、不可支持列表、客户验收假设、竞品对比、初始成本模型和风险列表。软件负责人和验证负责人必须参与，否则规格可能不可用或不可验证。

## M3：架构候选收敛

M3 的目标是从多个想法收敛到少数候选架构。每个候选都应有 workload 性能数据、面积/功耗估算、内存带宽需求、软件复杂度、验证复杂度、IP 依赖和后端风险。

不要只用单页 PPT 做架构决策。至少需要模型结果、假设、反例和 rejected alternatives。被拒绝的方案也要记录原因，因为后续团队会重新提出类似想法。

M3 的签核问题包括：模型是否校准过，关键瓶颈是否被解释，性能收益是否来自真实 workload，是否有软件映射路径，是否有物理实现反馈，是否存在不可接受的验证复杂度。

## M4：IP 和节点预签核

M4 的目标是确认架构不是纸上方案。关键 IP、工艺节点、foundry 路径、封装和成本模型必须有可信证据。

交付物包括 IP buy/build 决策表、vendor shortlist、授权风险、PDK 获取路径、节点比较、封装假设、EDA 预算、后端资源计划和 NRE 估算。对 7nm 及以下项目，应明确先进节点支持、IP 可用性、物理设计能力和 foundry interface。

M4 如果跳过，项目可能在 RTL 写到一半时才发现关键 PHY 不可用、license 不允许、PDK 拿不到、封装供应链不支持或预算严重不足。

## M5：架构规格冻结

M5 是进入大规模微架构、RTL 和验证的关键门。冻结对象包括外部接口、编程模型、内存模型、主要模块划分、关键参数、错误处理、debug 能力、power state、boot/reset 和验证映射。

冻结不是禁止任何修改，而是规定修改流程。M5 后的变更必须评估影响：RTL、验证、软件、DFT、后端、IP、成本和 schedule。没有变更控制，项目会陷入“永远差一点”的状态。

M5 参与者必须包括产品、架构、RTL、验证、软件、后端、DFT、硅后和项目管理。创始人需要参加，因为这是公司把资金从探索转向执行的节点。

## M6：项目执行批准

M6 是公司层面的 go/no-go。它不仅看技术方案，还看资金、人力、供应链、客户、融资和风险承受能力。芯片项目不是写完 RTL 就结束，后端、流片、封装、测试、bring-up、可靠性和客户导入都需要预算。

交付物包括总体项目计划、预算、团队计划、外包计划、风险登记册、里程碑付款计划、客户验证计划、respin contingency 和融资里程碑对齐表。若公司无法承受一次 respin，项目计划必须更保守。

## 签核会议应该怎么开

每个签核会应提前分发材料，明确决策问题，不应变成开放式 brainstorming。建议每个 gate 输出四类结论：通过、带条件通过、延期、停止。带条件通过必须明确条件 owner 和截止日期。

评审材料应包括数据、假设、风险和替代方案。对争议点，记录 decision owner 和最终判断依据。芯片项目很长，半年后没人记得当初为什么做某个决定，决策记录能减少反复争论。

## 指标与证据

| 证据 | 说明 |
|---|---|
| workload trace | 证明目标场景具体存在 |
| benchmark 脚本 | 证明指标可复现 |
| 性能模型结果 | 证明架构收益 |
| early synthesis | 校准面积和频率 |
| floorplan sketch | 暴露物理风险 |
| IP vendor response | 证明 IP 可获得 |
| cost model | 证明商业可承受 |
| verification mapping | 证明规格可验证 |
| risk register | 证明团队知道不确定性 |

这些证据不需要一开始完美，但必须足以支持进入下一阶段。创业公司可以接受不确定性，但不能接受假装没有不确定性。

## 常见错误

第一个错误是没有明确 gate，导致探索无限延长。每个新想法都看起来有价值，但项目没有进入执行状态。

第二个错误是签核只由架构团队完成。后端、验证、DFT、软件和供应链没有参与，导致方案无法落地。

第三个错误是没有记录 rejected alternatives。后续新人或投资人会不断问同样问题，团队重复消耗。

第四个错误是把融资 PPT 当作工程 signoff。融资材料可以突出愿景，工程签核必须暴露风险。

第五个错误是没有变更控制。规格冻结后仍随意改接口和功能，RTL、验证和软件都会被拖垮。

## 创业公司视角下的取舍

创业公司不需要大公司式厚重流程，但需要轻量、硬约束的 gate。每个 gate 可以是一页 checklist 加一份数据包，但必须有 owner 和结论。流程轻不等于没有流程。

AI Agent 可以帮助维护 checklist、发现文档不一致、生成评审问题、追踪 requirement 到 test plan。但签核必须由具体负责人承担。尤其是成本、节点、IP 和客户承诺，不能交给自动化系统做最终判断。

对第一颗芯片，建议设置更严格的 go/no-go 条件。若 workload 不清、关键 IP 未确认、PDK 路径不清、验证负责人缺位或资金不覆盖后端和硅后，不应进入大规模 RTL 开发。

## 典型场景

团队在 M3 评审中提出两个架构方案。方案 A 性能模型最好，但依赖 HBM、复杂动态调度和高频 NoC。方案 B 性能略低，但使用更成熟内存方案，验证和后端风险明显低。创始人倾向方案 A，因为融资叙事更强。

M4 评审补充 IP、封装、成本和 foundry 信息后发现，方案 A 的 HBM 封装和 IP 路径无法在当前预算和时间内确认。团队最终选择方案 B 进入第一颗芯片，并把方案 A 作为第二代 roadmap，同时设计部分软件接口保持未来兼容。这个决策不是技术保守，而是把项目从不可控风险拉回可执行状态。

## 后续阅读

- [RTL 设计工程实践](../02_frontend_design_and_verification/01_rtl_design_practices.md)
- [前端验证方法学](../02_frontend_design_and_verification/03_verification_methodology.md)
- [综合准备](../02_frontend_design_and_verification/04_synthesis_preparation.md)
- [完整芯片生命周期总览](../00_overview/01_full_lifecycle.md)
- [创业公司 vs 大公司的流程差异](../00_overview/04_startup_vs_bigcompany.md)

## 参考公开来源

- [Accellera IP-XACT](https://www.accellera.org/downloads/standards/ip-xact)
- [RISC-V International Ratified Specifications](https://riscv.org/specifications/ratified/)
- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [Cadence Genus Synthesis Solution](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/synthesis/genus-synthesis-solution.html)

## 内容可信度说明

- **公开信息（高可信）**：芯片开发需要规格、IP、节点、EDA、验证和物理实现等跨团队输入；公开标准和 EDA/foundry 生态可作为签核证据来源。
- **行业惯例（中可信）**：M0-M6 里程碑、gate review、risk register、go/no-go、规格冻结和变更控制是业界常见项目管理实践的抽象。
- **经验性观察（中低可信）**：创业公司需要轻量但硬约束的签核；融资 PPT 和工程 signoff 必须分开；第一颗芯片应设置更严格的进入执行条件。
- **不确定/需向资深工程师确认（低可信）**：具体公司里程碑命名、投资人和客户要求的证据、不同 foundry/IP vendor 的评审材料、特定项目可接受风险阈值。
