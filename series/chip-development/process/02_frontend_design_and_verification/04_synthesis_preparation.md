# 综合准备

## 前置知识

- 建议先读 [RTL 设计工程实践](./01_rtl_design_practices.md)。
- 建议先读 [微架构设计](./02_microarchitecture_design.md)。
- 建议理解 [Synthesis](../00_overview/05_glossary.md#synthesis)、[Netlist](../00_overview/05_glossary.md#netlist)、[SDC](../00_overview/05_glossary.md#sdc)、[Standard Cell Library](../00_overview/05_glossary.md#standard-cell-library)、[STA](../00_overview/05_glossary.md#sta)。

## 综合准备的目标

[Synthesis](../00_overview/05_glossary.md#synthesis) 把 RTL 转换成门级 [Netlist](../00_overview/05_glossary.md#netlist)。常见工具包括 Synopsys Design Compiler / Fusion Compiler、Cadence Genus、开源探索中的 Yosys/OpenROAD。综合不是“点击编译”，它需要工艺库、时序约束、面积/功耗目标、层次策略、DFT 约束和与后端一致的假设。

综合准备的目标是尽早发现 RTL 的物理实现风险：关键路径太长、面积超预算、memory macro 不合理、约束缺失、clock gating 不规范、不可综合语法、reset/enable 结构影响优化。越晚发现，修改成本越高。

## 输入物

| 输入 | 来源 | 说明 |
|---|---|---|
| RTL | RTL 团队 | 必须 lint-clean 或有解释过的 waiver |
| Library | foundry/IP vendor | standard cell、memory macro、IO、physical abstract |
| SDC | RTL/后端/STA | clock、IO delay、false path、multicycle path |
| UPF/CPF | low-power 团队 | power domain、isolation、retention、level shifter |
| DFT constraint | DFT 团队 | scan、test clock、test mode、MBIST |
| Design config | 集成团队 | file list、define、parameter、top module |
| Timing target | 架构/后端 | 目标频率、corner、mode |
| Physical estimate | 后端 | macro、wireload、floorplan 约束或 early physical guidance |

先进节点下，综合最好尽早引入 physical awareness。纯逻辑综合可能低估线延迟和拥塞。

## SDC 不是形式文件

[SDC](../00_overview/05_glossary.md#sdc) 定义时钟、输入输出延迟、false path、multicycle path、clock groups、generated clock、uncertainty 和 transition/load。错误 SDC 比没有 SDC 更危险，因为工具会给你看似干净但实际无效的 timing 报告。

常见问题包括：漏定义 generated clock，导致部分路径未分析；把真实路径错误标成 false path，掩盖 timing bug；multicycle path 没有配套 hold 约束；异步时钟没有正确分组；IO delay 没有对应 board/IP 时序假设；test mode 和 functional mode 混在一起。软件背景的人容易把 constraint 当配置文件，实际它是设计意图的一部分，需要 review、版本管理和 signoff。

## Early Synthesis

Early synthesis 应在 RTL 仍可修改时运行。目标不是一次达到最终 PPA，而是回答：代码是否可综合；面积量级是否离谱；关键路径在哪里；是否存在过宽 mux、过大 comparator、深组合链；clock gating 是否被识别；memory 是否被正确实例化或 infer；DFT/test mode 是否破坏时序；约束是否完整。

对 agent 生成 RTL，early synthesis 是必要检查。很多代码仿真能跑，但综合后生成巨大组合逻辑或不可接受的 latch/mux 结构。

## 层次、报告和 LEC

综合可以 flatten 设计，也可以保持层次。保持层次有利于调试、ECO、团队分工和增量构建；flatten 可能给优化更多空间，但也可能破坏模块边界和可读性。大型 SoC 通常采用 hierarchical synthesis，与后端 block-level implementation 对齐。

综合输出不只是 netlist，还应包括 timing、area、power、QoR、constraint check、clock gating、DFT readiness 和 LEC setup 报告。不要只看 WNS/TNS。Unconstrained path、错误 false path、巨大面积异常和 clock gating 未识别同样危险。

综合后需要逻辑等价检查，常见工具包括 Synopsys Formality、Cadence Conformal。LEC 证明综合后的 netlist 与 RTL 功能等价。它不能证明 RTL 符合规格，但能防止综合优化、retiming、clock gating 或手工 ECO 改变功能。

## 角色和典型节奏

综合准备由 RTL lead、synthesis engineer、STA engineer、后端实现工程师、DFT engineer 和 low-power engineer 共同负责。Block 级 early synthesis 可以在 RTL 初步稳定后每周或每两周运行；subsystem 和 SoC 级综合会随着集成逐步加严。先进节点项目通常需要更早的 physical guidance，成熟节点或小型 MPW 项目可以轻量一些，但仍应保留约束审查和综合 smoke test。

## 典型场景

一个 agent 生成的 address decoder 使用大 `case` 和多个嵌套条件。仿真正确。Early synthesis 报告显示该模块成为关键路径，且面积远高于预期。进一步分析发现生成代码把多个互斥条件写成并行比较，综合出宽 mux 和大量 comparator。

团队把地址空间重构成分层 decode，并让寄存器配置路径和高速数据路径分离。验证补充 equivalence-style directed tests，综合后关键路径从 decoder 转移到预期的数据通路。这说明“功能正确”不等于“可实现结构合理”。

## 创业公司视角

创业公司不应等 RTL 全部完成才第一次综合。建议每个重要 block 达到基本功能后就跑 quick synthesis，形成面积、频率和关键路径趋势。即使没有最终 PDK，也可以用可用库做相对比较，但不能把结果当最终签核。

如果目标是 7nm 及以下，尽早让后端或外包实现团队参与约束和 physical feedback。先进节点的 wire delay、macro placement、clock tree、power grid 会反向影响 RTL。只靠前端团队闭门优化很容易误判。

## 后续阅读

- [DFT 引入](./05_dft_introduction.md)
- [低功耗设计](./07_low_power_design.md)
- [前端签核标准](./08_signoff_criteria.md)
- [后端物理设计总览](../03_backend_physical_design/README.md)

## 参考公开来源

- [Synopsys Design Compiler NXT](https://www.synopsys.com/implementation-and-signoff/rtl-synthesis-test/design-compiler-nxt.html)
- [Cadence Genus Synthesis Solution](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/synthesis.html)
- [Synopsys Formality](https://www.synopsys.com/implementation-and-signoff/signoff/formality-equivalence-checking.html)
- [Cadence Conformal Equivalence Checker](https://www.cadence.com/ja_JP/home/tools/digital-design-and-signoff/logic-equivalence-checking/conformal-equivalence-checker.html)

## 内容可信度说明

- **公开信息（高可信）**：Design Compiler、Genus、Formality、Conformal 等工具公开存在；SDC、standard cell library、netlist、STA 是数字 ASIC 流程基础概念。
- **行业惯例（中可信）**：early synthesis、constraint review、QoR report、hierarchical synthesis、LEC 准备是常见前端到后端衔接实践。
- **经验性观察（中低可信）**：agent 生成 RTL 常在综合后暴露面积和关键路径问题；创业公司应高频运行 quick synthesis 而不是等 RTL freeze。
- **不确定/需向资深工程师确认（低可信）**：具体 timing target、corner 设置、physical guidance、flatten 策略和 false/multicycle path waiver 必须由综合/STA/后端专家确认。
