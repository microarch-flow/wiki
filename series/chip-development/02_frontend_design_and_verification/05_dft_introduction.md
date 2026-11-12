# DFT 引入

## 前置知识

- 建议先读 [综合准备](./04_synthesis_preparation.md)。
- 建议先读 [前端签核标准](./08_signoff_criteria.md)。
- 建议理解 [DFT](../00_overview/05_glossary.md#dft)、[Scan Chain](../00_overview/05_glossary.md#scan-chain)、[MBIST](../00_overview/05_glossary.md#mbist)、[ATE](../00_overview/05_glossary.md#ate)。

## DFT 解决什么问题

[DFT](../00_overview/05_glossary.md#dft) 是 Design for Test，可测性设计。它解决的是制造后如何判断每颗芯片是否存在缺陷。功能仿真证明设计意图，DFT 和量产测试筛出制造缺陷。两者不是一回事。

晶圆制造会产生随机缺陷、系统性缺陷、桥接、开路、存储器坏位、时序相关故障和封装问题。没有 DFT，内部触发器和 SRAM 很难被 [ATE](../00_overview/05_glossary.md#ate) 控制和观察，量产时无法有效筛选坏片，良率分析也缺少诊断数据。

## 常见 DFT 结构

| 结构 | 作用 |
|---|---|
| Scan chain | 把触发器串起来，便于外部加载和观察内部状态 |
| Scan compression | 降低 scan pattern 数据量和测试时间 |
| MBIST | 测试 SRAM、register file、memory macro |
| LBIST | 用内部逻辑产生测试 pattern，常见于安全相关应用 |
| Boundary scan/JTAG | 板级连接测试和调试访问 |
| IJTAG | 访问片内嵌入式仪器 |
| Test points | 增强可控性和可观察性，提高 fault coverage |
| ATPG | 自动生成测试向量 |

AI 芯片含大量 SRAM，因此 [MBIST](../00_overview/05_glossary.md#mbist) 往往是 DFT 的核心工作之一。

## 为什么 DFT 要早介入

软件背景的人容易把测试理解为后期 QA。芯片 DFT 不能后期补。Scan 需要触发器结构适合替换，异步 reset/set、gated clock、latch、multiple clock、black box、memory macro 都会影响插入。MBIST 需要 memory 实例、端口、repair、测试时钟和 power mode 规划。JTAG/test mode 需要顶层 pin、寄存器和安全策略。

DFT 后期才介入的后果包括：某些寄存器不可 scan，fault coverage 达不到目标；test mode 与功能模式冲突；scan chain 过长，测试时间和成本上升；ATPG pattern 产生大量 X，覆盖率差；MBIST controller 放不下或接不进 memory；测试功耗超过电源网或 ATE 能力，导致 false fail；后端需要大规模 ECO。

## RTL 对 DFT 的影响

RTL designer 应避免让 DFT 团队被迫重构设计。常见要求包括：

- 时钟结构清晰，不手写危险 gated clock，使用标准 clock gate cell 或综合可识别风格。
- reset 策略一致，避免无法控制的异步 set/reset。
- test mode 能 bypass clock gating、isolation 或部分 low-power 控制。
- memory 通过 wrapper 或明确接口接入 MBIST。
- 不产生过多 X source，例如未初始化控制寄存器、三态总线、不可控 analog/IP 输出。
- scan enable、test clock、test reset 在顶层规划清楚。
- 安全逻辑和 debug/test 访问权限定义明确。

## ATPG、覆盖率和成本

ATPG 根据故障模型生成测试向量。常见故障模型包括 stuck-at、transition delay、bridging、cell-aware 等。覆盖率目标因产品、市场和安全要求而异，消费类、数据中心、汽车电子要求不同。不要在没有 DFT 专家的情况下承诺具体数字。

测试覆盖率不是越高越免费。更高覆盖率可能增加 test points、pattern 数量、ATE 时间、测试功耗和调试成本。创业公司要在客户质量要求、成本和上市时间之间做取舍，但不能省掉基本制造测试。

## DFT 与低功耗、后端和封测

低功耗设计会显著影响 DFT。Power gating、isolation、retention、level shifter、clock gating 都需要 test mode 下的行为定义。某些 power domain 关闭时 scan path 如何连通，MBIST 如何供电，test pattern 是否会造成过高 toggle，都要提前规划。

DFT 不止前端插 scan。它会影响后端 scan chain reorder、test clock tree、test pin、power grid、pattern 交付、ATE program、wafer sort 和 final test。OSAT 和测试工程师也需要早参与，尤其是高速接口、HBM、chiplet 或复杂封装项目。

前端阶段至少要输出 DFT architecture、scan/MBIST plan、test mode 定义、pattern 策略、coverage 目标、DFT rule check 报告和风险列表。

## 角色、节奏、成本与接口

DFT owner 通常是 DFT engineer 或 test lead，RTL、后端、低功耗、封测、ATE 工程师都需要参与。DFT 架构应在微架构和 top-level integration 阶段确定，scan/MBIST rule check 应在综合前后多次运行，ATPG 和 pattern 调试会延续到后端、tapeout 前和硅后测试开发。具体时长因 memory 数量、clock/reset 复杂度、test compression 和产品质量要求差异很大。

上游输入包括 RTL、memory macro 清单、clock/reset 结构、UPF、IP DFT 文档、封装和测试策略。下游输出包括 scan/MBIST 插入约束、test mode、ATPG pattern、coverage 报告、ATE 程序输入和 failure analysis 数据。成本包括 DFT/ATPG license、DFT 工程人力、额外面积、测试时间和 ATE 成本。创业公司可以外包 DFT 执行，但不能外包 coverage、test mode 和测试成本的风险判断权。

## 典型场景

团队设计了一个大 NPU SRAM scratchpad，RTL 中把多个 SRAM macro 包在自定义 wrapper 里，但没有暴露标准 MBIST 接口。后期 DFT 工程师要求接入 MBIST controller，发现 wrapper 内部还有 clock gating 和 bank remap 逻辑，测试模式下无法单独控制每个 macro。修改影响 RTL、验证、综合和 floorplan。

更好的做法是在微架构阶段就定义 memory wrapper 模板：功能端口、BIST 端口、repair 信息、test clock、test reset、power mode 和 DFT bypass。验证环境同时包含功能访问测试和 MBIST connectivity 检查。

## 创业公司视角

创业公司可以外包 DFT 实施和 ATPG，但不能外包 DFT 架构责任。内部至少要有人理解 scan、MBIST、test mode、coverage、ATE 时间和量产质量之间的关系。第一颗芯片如果没有量产计划，也应保留基本 DFT，因为硅后 debug、yield learning 和投资人/客户尽调都会看可测性。

开源 RTL 项目更要注意：公开 RTL 不等于公开 foundry-specific DFT 实现。scan cell、memory BIST、test compression 可能依赖商业库和工具。可以开源 DFT 意图、wrapper、接口和可替代实现，但量产级 DFT 仍需要商业工具和工艺库配合。

## 后续阅读

- [CDC 与 RDC](./06_cdc_and_rdc.md)
- [低功耗设计](./07_low_power_design.md)
- [前端签核标准](./08_signoff_criteria.md)
- [硅后 Bring-up](../04_tapeout_and_post_silicon/04_post_silicon_bringup.md)

## 参考公开来源

- [Synopsys TestMAX DFT](https://www.synopsys.com/implementation-and-signoff/test-automation/testmax-dft.html)
- [Cadence Modus DFT Software Solution](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/test-automation/modus-dft-software.html)
- [Siemens Tessent BoundaryScan](https://www.siemens.com/en-us/products/ic/tessent/test/boundaryscan/)
- [Siemens Tessent Products](https://www.siemens.com/en-us/products/ic/tessent/offerings/)

## 内容可信度说明

- **公开信息（高可信）**：scan、MBIST、ATPG、boundary scan、DFT 工具类别和主要商业工具公开可查。
- **行业惯例（中可信）**：DFT 需要早介入 RTL、clock/reset、memory wrapper、test mode、low-power 和后端流程；DFT coverage 与 ATE 成本、量产质量相关。
- **经验性观察（中低可信）**：创业公司可以外包 DFT 实施但不能缺少内部 DFT owner；AI 芯片 SRAM 多，MBIST 风险尤其重要。
- **不确定/需向资深工程师确认（低可信）**：具体 fault coverage 目标、pattern 数量、scan compression 策略、ATE 时间、OSAT 要求和 automotive/functional safety 约束需按产品确认。
