# DRC/LVS Signoff

## 前置知识

- 建议先读 [Routing](./04_routing.md) 和 [Power Analysis](./06_power_analysis.md)。
- 建议理解 [DRC](../00_overview/05_glossary.md#drc)、[LVS](../00_overview/05_glossary.md#lvs)、[GDSII](../00_overview/05_glossary.md#gdsii)、[流片 Tapeout](../00_overview/05_glossary.md#流片-tapeout)。

## 核心概念

DRC 检查版图是否符合 foundry 工艺规则；LVS 检查版图抽取出来的电路是否与目标网表一致。二者是 physical signoff 的底线。DRC clean 说明“工艺上可制造”，LVS clean 说明“版图实现的是这个电路”。它们都不证明功能正确，但任何一个失败都不能正常 tapeout。

Physical signoff 还包括 [Antenna Effect](../00_overview/05_glossary.md#antenna-effect)、density、[Metal Fill](../00_overview/05_glossary.md#metal-fill)、[ERC](../00_overview/05_glossary.md#erc)、[DFM](../00_overview/05_glossary.md#dfm)、DFY、[PERC](../00_overview/05_glossary.md#perc)、[ESD](../00_overview/05_glossary.md#esd)/latch-up 相关检查、power/ground connectivity、short/open、seal ring、scribe line、bump/pad 检查等。先进节点的 signoff deck 通常复杂、运行时间长、版本敏感。

## 关键活动顺序

1. 确认 PDK、rule deck、tech file、layer map、foundry signoff checklist 版本。
2. 从实现工具导出 GDS/OASIS、netlist、DEF、LEF、layout database。
3. 运行 block-level DRC/LVS，先清局部问题。
4. 运行 full-chip DRC/LVS，检查 top integration、IP boundary、seal ring、IO、bump。
5. 清 antenna、density、fill、ERC、short/open、floating well、PG connectivity。
6. 对 signoff violation 分类：真实错误、tool/setup 错误、IP vendor waiver、foundry waiver。
7. 修复后回归 STA、power、routing，因为 fill/route/ECO 会改变寄生。
8. 生成 signoff package：clean report、waiver、deck version、run script、GDS checksum、tapeout manifest。

## 工具名

主流工具包括 Siemens Calibre nmDRC/nmLVS、Synopsys IC Validator、Cadence Pegasus。寄生抽取可用 Synopsys StarRC、Cadence Quantus。实现工具 Innovus/IC Compiler II/Fusion Compiler 可做早期 DRC 检查，但最终通常要以 foundry 认可的 signoff deck 和工具配置为准。

## 角色与典型时长

Physical verification engineer 是核心 owner，PD engineer、IP owner、foundry AE、CAD/flow、package/IO engineer 都会参与。小 block 清 DRC/LVS 可能数天到数周；复杂 SoC full-chip physical signoff 可能持续数周甚至更久。先进节点 signoff runtime 和 debug 成本明显更高。

## 关键决策点

- 何时引入 signoff DRC：越早越好，不能等 tapeout 前最后一轮。
- Waiver 是否可接受：必须来自 foundry/IP vendor 或有明确证据，不能用口头解释。
- Metal fill 策略：影响密度、寄生、timing 和 IR，需要回归。
- ECO 修复方式：metal ECO 成本低于 full respin，但能力有限；pre-tapeout ECO 也可能破坏 clean 状态。
- IP black box 验证边界：必须确认 hard IP 的 GDS、LEF、abstract、LVS blackbox、antenna model 一致。

## 先进节点与 28/16nm 差异

7nm 及以下 DRC 规则数量和复杂度显著增加，包括更复杂的 spacing、end-of-line、via、cut metal、coloring、density、pattern matching 和 reliability 规则。即使使用 EUV，也不意味着规则简单。先进节点的 signoff DRC runtime、存储、license 和 debug 成本都更高。

28nm/16nm 中某些 DRC 问题可以较直观定位；先进节点中很多 violation 是上下文相关或 pattern-based，需要专业 physical verification 工程师和 foundry AE 支持。创业公司如果没有经验，必须预留外部支持。

## 常见坑

- 实现工具内部 DRC clean 就以为 signoff DRC clean。
- Rule deck 版本与 foundry tapeout 要求不一致。
- IP vendor 提供的 LEF/GDS/lib/netlist 版本不匹配。
- Metal fill 后没有重新抽取寄生并回 STA。
- LVS blackbox 配置错误，掩盖真实连接问题。
- Waiver 没有 owner、来源、适用范围和到期条件。
- 最后一周才跑 full-chip DRC/LVS，发现大量集成问题。

## 上下游接口

上游来自 routing、ECO、IP integration、package/IO、foundry PDK。下游是 tapeout package 和 mask making。DRC/LVS 失败会反推 routing、floorplan、IP 版本、power grid、IO/bump 规划，甚至 RTL/DFT 结构。

Physical verification 也会影响 STA/power：fill 改变寄生，antenna diode 增加负载，route fix 改变线长，PG fix 改变 IR。每次修复都要评估是否需要重新 signoff 相关项目。

## 创业公司取舍

创业公司可以把 DRC/LVS 执行外包，但不能把 clean 标准外包成黑盒。内部至少要有人能读懂 violation 分类、waiver 风险、deck 版本和 tapeout checklist。先进节点 signoff 需要昂贵 license 和大量 CPU，使用云或服务商可能更现实，但数据安全、版本复现和责任边界必须写清。

不能为了赶 MPW 或客户节点而带 DRC/LVS 风险 tapeout。制造出来的芯片不因你是创业公司而放宽物理规则。

## 成本视角

Physical verification 的直接成本包括 Calibre/ICV/Pegasus 等 license、计算资源、PV 工程师时间和服务商费用。成熟节点小 block 的 PV 支持可能是数千到数万美元量级；复杂 SoC 或先进节点 full-chip DRC/LVS/DFM signoff 支持可能是数十万到数百万美元项目成本的一部分。更大的成本是延误：如果 tapeout 前一周才发现 deck 版本、LVS blackbox 或 full-chip DRC 问题，可能推迟 mask slot；如果错误 waiver 导致硅片不可用，则进入 respin 成本，先进节点通常是百万到千万美元量级风险。

## 典型场景

Tapeout 前三天，团队发现 full-chip LVS 不通过，原因是某个 SRAM macro 的 abstract 与 GDS 版本不一致，power pin 名称在 top-level 连接中被映射错。实现工具没有报错，因为 LEF 视图可以放置布线。修复需要更换 IP deliverable、重新 LVS、重新抽取、重新跑 STA/power。根因不是工具问题，而是 IP 版本管理和 signoff 提前量不足。

## 后续阅读

- [Tapeout 流程](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [Mask 制作与晶圆制造](../04_tapeout_and_post_silicon/02_mask_making_and_wafer_fab.md)
- [Silicon Revision](../04_tapeout_and_post_silicon/08_silicon_revision.md)
- [后端外包](./09_backend_outsourcing.md)

## 参考公开来源

- [Siemens Calibre nmDRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/)
- [Siemens Calibre nmLVS](https://www.siemens.com/en-gb/products/ic/calibre-design/circuit-verification/nmlvs/)
- [Synopsys IC Validator](https://www.synopsys.com/icvalidator)
- [Cadence Pegasus Verification System](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff.html)

## 内容可信度说明

- **公开信息（高可信）**：DRC、LVS、Calibre、IC Validator、Pegasus、physical signoff 工具类别和用途公开可查。
- **行业惯例（中可信）**：deck version control、waiver 管理、fill 后回归、full-chip signoff checklist 是常见实践。
- **经验性观察（中低可信）**：IP 视图版本不一致和最后阶段 full-chip signoff 延迟是创业团队常见风险。
- **不确定/需向资深工程师确认（低可信）**：具体 foundry rule deck、waiver 政策、tapeout checklist、signoff runtime 和云端运行规则。
