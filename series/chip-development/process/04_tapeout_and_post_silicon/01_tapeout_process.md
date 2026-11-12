# Tapeout Process

## 前置知识

- 建议先读 [后端物理设计总览](../03_backend_physical_design/README.md)。
- 建议先读 [DRC/LVS Signoff](../03_backend_physical_design/07_drc_lvs_signoff.md)。
- 建议理解 [流片 Tapeout](../00_overview/05_glossary.md#流片-tapeout)、[GDSII](../00_overview/05_glossary.md#gdsii)、[OASIS](../00_overview/05_glossary.md#oasis)、[Signoff](../00_overview/05_glossary.md#signoff)、[ECO](../00_overview/05_glossary.md#eco)。

## 核心概念

Tapeout 是把最终版物理设计数据交给 foundry，进入 mask 制作和晶圆制造的里程碑。它不是“后端导出一个 GDS 文件”，而是跨团队确认设计、物理、测试、封装、IP、waiver、版本和商业风险都达到可接受状态。

Tapeout 之后，修改成本显著上升。严重 RTL bug、DRC/LVS 误判、timing exception 错误、UPF 不一致、DFT 不可用、IP view 错配，都可能变成首硅失败或 respin。软件背景的人要把 tapeout 看作一次不可轻易回滚的发布，而不是 CI 构建产物。

## Tapeout 前必须完成的签核

典型签核包括：

- STA：多 corner/mode setup/hold closure，timing exception 审查完成。
- DRC/LVS/ERC/antenna/density/fill：physical verification clean 或 waiver 明确。
- IR/EM/power/SI：电源完整性、功耗、串扰和噪声风险闭合。
- DFT/ATPG/scan/MBIST：制造测试结构和 pattern 可用。
- CDC/RDC/formal equivalence：前端静态风险和 RTL-to-netlist 等价闭合。
- ECO closure：所有 late ECO 已回归 STA、LEC、DRC、LVS、power。
- IP signoff：hard IP 的 GDS、LEF/DEF、lib、LVS blackbox、timing model、version 一致。
- Package/IO：pad/bump、seal ring、scribe、package constraints 与版图一致。

任何 waiver 都必须有 owner、理由、影响范围和风险接受人。没有证据的 waiver 不是“经验判断”，而是带风险流片。

## Tapeout Package

Tapeout package 通常包括 GDSII/OASIS、版图数据库、signoff reports、netlist、DEF/LEF、SPEF、SDC、UPF、Liberty 版本、PDK/rule deck 版本、IP 版本清单、waiver 清单、DRC/LVS clean reports、ATPG/test collateral、metal fill、seal ring、scribe/test structures、checksum 和 manifest。

Foundry 或 turnkey partner 可能有固定模板。创业公司必须让 CAD/flow owner 和后端负责人维护一份可复现 manifest，记录每个文件来自哪个版本、由哪个工具生成、使用哪个 PDK/deck 版本。

## 典型工具

Tapeout 前的报告来自多类工具：STA 常见 Synopsys PrimeTime、Cadence Tempus；物理验证常见 Siemens Calibre、Synopsys IC Validator、Cadence Pegasus；等价检查常见 Synopsys Formality、Cadence Conformal；DFT/ATPG 常见 Siemens Tessent、Synopsys TestMAX、Cadence Modus；实现数据库来自 Cadence Innovus、Synopsys Fusion Compiler/IC Compiler II、Siemens Aprisa；寄生抽取来自 StarRC、Quantus 等。Tapeout package 本身还会使用内部 CAD 脚本、checksum、manifest 和 foundry 提交门户。

工具名不是装饰信息。项目必须记录工具版本、PDK/deck 版本、command/script、输入文件 hash 和报告路径，否则硅后发现问题时无法复现 tapeout 状态。

## 关键活动顺序

1. 冻结 RTL/netlist/IP/PDK/deck/tool 版本。
2. 完成 final signoff run，并保存原始报告和摘要。
3. 召开 tapeout readiness review，逐项审查 timing、power、PV、DFT、IP、package、test、known issue。
4. 审查 waiver 和 residual risk，明确谁接受风险。
5. 生成 GDS/OASIS、checksum、manifest 和 foundry 要求的辅助文件。
6. 由 foundry/turnkey 做 incoming check，发现数据或规则问题则回退修正。
7. 正式提交 mask data，进入 mask making。

## 角色与典型时长

参与者包括后端 lead、STA、physical verification、DFT/test、IP owner、package/IO、firmware/bring-up、项目负责人、foundry interface、EDA/CAD。Tapeout 前最终准备通常是天到数周量级；复杂先进节点项目会有多轮 dry run 和 foundry check。

CEO/CTO 不需要逐条看 timing path，但必须知道：还有哪些 waiver、哪些 bug 未关闭、是否有足够资金和时间承受 respin、foundry slot 是否确认、封装和 bring-up 是否准备好。

## ECO 边界

Tapeout 前 ECO 分为 RTL ECO、netlist ECO、metal ECO。越晚越倾向于小范围 ECO，因为全流程回归成本高。Tapeout 后如果 mask 尚未制作，可能还能撤回或替换数据；mask 制作后，metal-only respin 只能修改部分金属层，无法修正大规模逻辑结构、SRAM macro、模拟 IP 或封装级错误；base-layer 或 full respin 成本和周期显著更高。

先进节点 metal-only ECO 也可能是数十万到数百万美元量级；full mask/full respin 可能进入数百万到千万美元量级。具体取决于节点、修改层数、foundry 商务和 schedule。

## 常见坑

- 最终 GDS 使用的 IP 版本与 STA/LVS 报告里的 IP 版本不一致。
- Foundry rule deck 不是 tapeout 要求版本。
- DRC clean 但 fill 后没有重新抽取并回归 STA。
- Timing waiver 没设计依据，只是为了清报表。
- DFT pattern 还没准备好，tapeout 后才发现测试不可用。
- 后端团队单独决定 tapeout，软件/bring-up/test 团队没有 ready。
- Agent 或 generator 生成 RTL 的 traceability 没有进入 signoff 包，后续 bug 无法回溯。

## 上下游接口

上游来自后端 physical signoff 和前端 verification/DFT/CDC/LEC closure。下游接收方是 foundry mask data prep、mask shop、wafer fab、OSAT、ATE/test、bring-up 团队。Tapeout package 的版本错误会污染下游所有结果，因此必须严控 manifest 和 checksum。

## 创业公司取舍

创业公司可以使用 turnkey 或后端服务商协助准备 tapeout package，尤其是先进节点、缺少 CAD/flow 和 PV 经验时。但内部必须保留风险决策权，不能接受“供应商说 clean 所以流片”。

如果资金只够一次流片，没有 respin buffer，tapeout 标准应更严格，而不是更宽松。首颗芯片赶时间可以降低频率目标、减少功能、选择成熟节点或 MPW，但不应牺牲基本 signoff。

## 典型场景

团队准备 tapeout，STA、DRC、LVS 报告都显示 clean。Tapeout review 中 test lead 发现 scan compression pattern 还没在 final netlist 上重新生成；package engineer 发现 bump map 与 latest floorplan 不一致；firmware lead 发现 boot strap pin 定义和文档不同。若直接提交，首硅可能无法测试或无法 boot。正确做法是暂停提交，修正版本，重跑必要 signoff，再更新 manifest。

## 后续阅读

- [Mask 制作与晶圆制造](./02_mask_making_and_wafer_fab.md)
- [Packaging](./03_packaging.md)
- [Post-silicon Bring-up](./04_post_silicon_bringup.md)
- [Silicon Revision](./08_silicon_revision.md)

## 参考公开来源

- [Siemens Calibre nmDRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/)
- [Synopsys IC Validator](https://www.synopsys.com/icvalidator)
- [Cadence Pegasus Verification System](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff.html)
- [TSMC Open Innovation Platform overview](https://www.tsmc.com/english/dedicatedFoundry/oip)

## 内容可信度说明

- **公开信息（高可信）**：tapeout、GDS/OASIS、DRC/LVS、STA、DFT、ECO、foundry handoff 的基本概念。
- **行业惯例（中可信）**：tapeout readiness review、manifest、waiver 管理、final signoff package 的组织方式。
- **经验性观察（中低可信）**：创业公司常见风险是版本不一致、waiver 不透明、test/bring-up 准备晚于 layout。
- **不确定/需向资深工程师确认（低可信）**：具体 foundry 提交流程、文件模板、ECO 可行性、mask data prep 要求和商务撤回窗口。
