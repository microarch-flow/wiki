# Backend Outsourcing

## 前置知识

- 建议先读 [后端物理设计总览](./README.md)。
- 建议先读 [先进节点特殊考虑](./08_advanced_node_considerations.md)。
- 建议理解 [Turnkey Services](../06_cross_cutting_topics/05_turnkey_services.md)、[Foundry](../06_cross_cutting_topics/02_foundry_relationships.md)、[Signoff](../00_overview/05_glossary.md#signoff)。

## 核心概念

后端外包是把 physical implementation、STA、physical verification、power signoff、tapeout package 准备等工作的一部分交给设计服务公司、EDA/foundry partner 或 turnkey 服务商。外包可以弥补创业公司经验、license、算力和人手不足，但不能外包最终产品判断和风险责任。

后端外包的本质不是“买一份 GDS”，而是建立一套责任清楚、输入可复现、阶段可验收、风险可见的协作流程。外包失败通常不是服务商不会跑工具，而是需求、约束、版本、PPA 目标、signoff 标准和变更控制不清。

## 可以外包的部分

- Block-level place and route。
- Full-chip integration implementation。
- STA closure 和 timing ECO 执行。
- DRC/LVS/antenna/density/fill 清理。
- Power grid implementation 和 IR/EM 分析执行。
- Tapeout package 准备。
- Flow setup、EDA scripting、compute farm/cloud 运行。
- 某些 IP hardening 或 SRAM/compiler integration。

## 不应完全外包的部分

- 架构级 PPA 目标和取舍。
- Floorplan 的关键决策，尤其 macro、NoC、IO、power、package 相关。
- Timing exception 的设计依据。
- Power workload 和真实 activity 定义。
- Waiver 接受决策。
- Signoff 是否可 tapeout 的最终判断。
- ECO 是否影响产品功能和软件契约。
- IP 版本、授权、foundry 关系和商业风险管理。

创业公司内部至少要有一名能审查后端结果的 senior physical/implementation owner，或长期顾问。没有这类能力，服务商给出的“clean”无法被独立判断。

## 关键活动顺序

1. 明确外包范围：block、subsystem、full-chip、STA、PV、power、tapeout。
2. 准备 handoff package：网表、SDC、UPF、LEF/lib/GDS、IP 版本、PDK、目标 PPA、signoff checklist。
3. 定义里程碑：floorplan review、placement QoR、CTS QoR、route QoR、post-route STA、DRC/LVS、final signoff。
4. 定义报告格式：[WNS/TNS](../00_overview/05_glossary.md#wnstns)、area、power、congestion、IR、DRC count、LVS status、ECO list、waiver list。
5. 建立变更控制：RTL/netlist/SDC/IP/PDK/tool 版本冻结规则。
6. 每周或更频繁 review，问题按前端、后端、IP、foundry、工具分类。
7. 关键节点做内部/第三方审查，尤其 floorplan、SDC、STA exception、waiver。
8. tapeout 前验收完整 signoff package 和可复现脚本。

## 工具名

服务商可能使用 Cadence Innovus/Tempus/Quantus/Voltus/Pegasus，Synopsys Fusion Compiler/IC Compiler II/PrimeTime/StarRC/IC Validator，Siemens Calibre，Ansys RedHawk-SC。合同中应明确工具链、版本、foundry-certified flow、license 责任、运行环境和数据交付格式。

## 角色与典型时长

外部角色包括项目经理、PD engineer、STA engineer、PV engineer、power engineer、CAD engineer。内部角色包括 chip lead、architecture/RTL owner、verification owner、DFT owner、software/runtime owner、foundry/IP owner。外包项目仍可能需要数月，不能因为外包就压缩物理 signoff 时间。

## 关键决策点

- Time-and-materials 还是 fixed-bid：fixed-bid 看似可控，但需求变化和 closure 风险容易引发争议。
- 外包到 block 还是 full-chip：block 外包易管理，全芯片外包依赖更强。
- 是否使用 turnkey：turnkey 覆盖 foundry/封测/流片，但透明度和控制权可能降低。
- 数据交付深度：只给 GDS 不够，必须要脚本、报告、waiver、版本、checkpoint。
- 风险归属：timing 不收敛、IP 延迟、PDK 变更、RTL bug、tool bug 分别谁负责。

## 成本与合同量级

后端外包通常按人月、里程碑或 turnkey package 报价。成熟节点单个 block 的 P&R/STA/PV 支持可能是数万美元到数十万美元量级；复杂 SoC top-level integration、全芯片 STA/PV/power signoff、先进节点 tapeout support 可能进入数十万到数百万美元量级。若服务商还提供 EDA license、计算资源、foundry interface、tapeout coordination 或 turnkey 管理，费用会继续上升。

报价里最容易遗漏的是变更成本：RTL/netlist 重交付、SDC 修改、IP 版本变化、PDK/deck 更新、late ECO、额外 corner/mode、额外 power scenario、追加 DRC/LVS 回归。合同应明确哪些属于基础范围，哪些按人月或变更单收费。固定价合同如果没有清晰输入冻结和验收标准，往往会在后期变成争议。

## 先进节点与 28/16nm 差异

成熟节点后端外包供应商更多、成本较低、流程相对稳定。7nm 及以下，服务商必须有对应节点 tapeout 经验、foundry access、certified flow、EDA license 和资深 signoff 能力。先进节点外包费用、管理成本和数据安全要求都更高。

对先进节点，创业公司尤其不能只看报价。低价服务商如果缺少节点经验，可能在最后 DRC/STA/IR signoff 阶段暴露问题，延误代价远超服务费差异。

## 常见坑

- 前端 handoff 不完整，把问题甩给后端服务商。
- 合同只写“完成后端”，没有定义 PPA、signoff、waiver、版本和验收。
- 内部没有人能审查 SDC 和 timing exception。
- 服务商修改网表或约束后，前端没有同步，LEC/验证断裂。
- Floorplan 由服务商独立决定，架构团队后期才发现性能/功耗不符合预期。
- 只在 tapeout 前 review，平时看不到 QoR 趋势。
- 没有明确数据所有权、脚本交付和可复现环境。

## 上下游接口

外包上游依赖前端 signoff package、IP deliverable、foundry/PDK、package/IO 约束。外包下游连接 tapeout、mask、foundry、OSAT 和硅后 bring-up。服务商发现的问题必须反馈给 RTL/架构/验证，而不是在后端内部用不可追踪 ECO 掩盖。

Physical feedback 对创业公司尤其重要。你要把外包方的 congestion、timing、IR、DRC 报告转化成产品决策：降频、增面积、改 RTL、改软件调度、延后功能、换节点或接受风险。

## 创业公司取舍

外包适合补执行能力，不适合替代核心工程判断。首版芯片建议把非核心 block、常规 implementation、PV 执行外包，同时内部保留 architecture-to-physical feedback loop。若资金有限，优先请资深顾问审查 floorplan、SDC、STA、power 和 signoff，而不是只买最低价服务。

外包不能让“快速迭代”绕过物理周期。服务商可以提高并行度和减少踩坑，但 mask、fab、封装、可靠性和 signoff 仍有硬约束。

## 典型场景

创业公司把全芯片后端固定价外包，内部只提供 RTL 和目标频率。两个月后服务商反馈 timing 无法收敛，建议降低频率。内部才发现 SDC 中多个 false path 没设计依据，SRAM macro 放置导致关键路径过长，power workload 也没定义。项目争议焦点变成“谁的责任”。正确做法是在合同前定义 handoff checklist、阶段 review、QoR dashboard、前端反馈机制和 signoff 验收标准。

## 后续阅读

- [Turnkey Services](../06_cross_cutting_topics/05_turnkey_services.md)
- [Foundry Relationships](../06_cross_cutting_topics/02_foundry_relationships.md)
- [Tapeout 流程](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [招聘优先级](../07_for_software_background_founders/03_recruitment_priorities.md)

## 参考公开来源

- [Synopsys IC Compiler II](https://www.synopsys.com/implementation-and-signoff/physical-implementation/ic-compiler.html)
- [Cadence Innovus Implementation System](https://www.cadence.com/en_US/home/resources/datasheets/innovus-implementation-system-ds.html)
- [Siemens Calibre nmDRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/)
- [Ansys RedHawk-SC](https://www.ansys.com/en-gb/products/semiconductors/ansys-redhawk-sc)

## 内容可信度说明

- **公开信息（高可信）**：后端实现、STA、PV、power signoff 工具和服务类别公开可查。
- **行业惯例（中可信）**：外包 handoff、milestone review、QoR dashboard、signoff package、版本冻结是常见项目管理实践。
- **经验性观察（中低可信）**：创业公司外包失败常见原因是内部缺少后端判断能力和验收标准。
- **不确定/需向资深工程师确认（低可信）**：具体服务商能力、报价、节点经验、foundry access、合同条款和责任划分需逐案尽调。
