# EDA Tools Landscape：EDA 工具版图

## 前置知识

- 建议先读 [Frontend Design and Verification](../02_frontend_design_and_verification/README.md)。
- 建议先读 [Backend Physical Design](../03_backend_physical_design/README.md)。
- 建议理解 [EDA](../00_overview/05_glossary.md#eda)、[Synthesis](../00_overview/05_glossary.md#synthesis)、[STA](../00_overview/05_glossary.md#sta)、[DRC](../00_overview/05_glossary.md#drc)、[LVS](../00_overview/05_glossary.md#lvs)、[Signoff](../00_overview/05_glossary.md#signoff)。

## 核心概念

EDA 工具不是一个软件包，而是一组贯穿 spec、RTL、验证、综合、DFT、后端、物理验证、功耗、测试、封装和量产数据分析的工具链。先进节点芯片项目的真实 flow 往往由商业 EDA、foundry reference flow、IP vendor collateral、内部脚本和数据平台共同组成。

软件背景的人容易低估 EDA 的两个特点。第一，很多结果不是“运行成功就正确”，而是要看约束、corner、waiver、版本和 signoff methodology。第二，工具之间的接口非常多：RTL、SDC、UPF、Liberty、LEF/DEF、SPEF、GDS/OASIS、SAIF/VCD、STIL、STDF。任何接口版本错配都可能造成后续阶段错误。

这些接口大致这样流转：RTL 由前端设计交给仿真、lint、综合和形式验证；SDC 由架构/前端/后端共同定义时钟和时序例外，错配会让 STA 结果失真；UPF 描述电源域和 isolation/retention，错配会造成低功耗仿真和实现不一致；Liberty、LEF/DEF、SPEF 连接综合、布局布线、寄生抽取和 STA，版本不一致会导致时序和面积结果不可比；GDS/OASIS 是 tapeout 版图交付；SAIF/VCD 用于功耗估算；STIL/测试 pattern 和 STDF/量产测试数据连接 DFT、ATE 和良率分析。每个文件都应有 owner、版本、生成脚本和消费工具列表。

## 工具链分层

前端仿真常见工具包括 Synopsys VCS、Cadence Xcelium、Siemens Questa。Lint/CDC/RDC 常见 Synopsys SpyGlass、Siemens Questa CDC、Cadence Jasper/Conformal CDC。形式验证包括 Cadence JasperGold、Synopsys VC Formal、Siemens Questa Formal。仿真加速和 emulation 包括 Cadence Palladium、Synopsys ZeBu、Siemens Veloce。

综合和逻辑实现常见 Synopsys Design Compiler/Fusion Compiler、Cadence Genus。DFT 常见 Siemens Tessent、Synopsys TestMAX、Cadence Modus。STA 常见 Synopsys PrimeTime、Cadence Tempus。功耗分析包括 Synopsys PrimePower、Cadence Voltus、Ansys RedHawk-SC。

物理实现常见 Cadence Innovus、Synopsys Fusion Compiler/ICC2、Siemens Aprisa。寄生抽取包括 Synopsys StarRC、Cadence Quantus。物理验证包括 Siemens Calibre、Synopsys IC Validator、Cadence Pegasus。封装/板级 SI/PI 可能用 Cadence Allegro/Sigrity、Ansys SIwave/HFSS、Keysight ADS 等。

开源生态包括 Verilator、Icarus Verilog、Yosys、Surelog/UHDM、OpenROAD、OpenLane、KLayout、Magic、Netgen、Cocotb、SymbiYosys、UVM Python 相关工具和各种脚本框架。它们对教育、原型、小规模设计、CI、lint、仿真和部分成熟节点 flow 很有价值，但先进节点 signoff 仍主要依赖商业工具和 foundry 认证流程。

## 关键活动顺序

第一步是定义 tool strategy。团队要明确哪些阶段必须使用商业工具，哪些可以用开源工具做快速检查，哪些由外包供应商负责。先进节点 AI SoC 通常不能只靠开源 flow 完成 signoff，但可以用开源工具做早期 lint、仿真、CI 和小模块探索。

第二步是建立 reproducible flow。每次 RTL、constraint、library、PDK、tool version、script 变化都要可追溯。芯片 flow 的“可复现”比软件 build 更难，因为工具 license、服务器环境、foundry collateral 和运行时间都影响结果。

第三步是建立 signoff checklist。每个 signoff 项要定义工具、版本、corner、输入文件、pass/fail 标准、waiver 规则和 owner。没有 checklist，团队会把“我跑过”误认为“项目可流片”。

第四步是自动化数据汇总。将 lint violation、coverage、timing slack、DRC count、IR drop、power、area、test coverage、waiver 统一进 dashboard。快速迭代的价值来自快速发现回归，而不是每次手工打开几十个报告。

## 角色、周期和成本

主要角色包括 CAD/flow engineer、verification lead、RTL lead、DFT lead、physical design lead、signoff owner、IT/license admin 和项目经理。创业公司常没有完整 CAD 团队，但至少需要一名懂 EDA flow 的负责人，否则 agent 生成代码和脚本很快会变成不可维护系统。

周期上，最小可用 flow 建立通常需要数周；能支撑 block-level 回归、综合 QoR 和基本后端试跑的 flow 往往需要数月；先进节点 signoff flow 会贯穿整个项目，并在 PDK、IP、工具版本和设计规模变化时持续维护。不要把 CAD/flow 视为一次性脚本。

商业 EDA 成本通常是芯片创业公司 NRE 的重要部分，先进节点全套 license、服务器和外包 flow 支持可能达到数十万到数百万美元量级，具体受工具组合、license 模式、节点、并发数和商业谈判影响。开源工具能降低学习和早期实验成本，但不能把先进节点 signoff 成本降为零。服务器和存储也要预算：大型仿真、emulation 数据、STA corner、DRC/LVS 和波形文件会产生可观的计算和存储需求。

## 关键决策点

第一个决策是商业工具覆盖范围。若目标是 7nm 及以下量产 ASIC，STA、物理验证、功耗/IR/EM、DFT、CDC/RDC 和后端 signoff 通常需要商业工具与 foundry 支持。开源工具可以做前置检查，但不能替代 foundry signoff。

第二个决策是 flow ownership。如果后端和 signoff 外包，内部仍要掌握输入/输出、约束、waiver 和结果解释。完全黑盒会让你无法判断供应商交付质量。

第三个决策是自动化优先级。早期最该自动化的是重复且容易漏的检查：lint、CDC、仿真回归、coverage、综合 QoR、timing regression、artifact versioning。不要一开始就追求“全自动 tapeout”，那会掩盖未定义的 signoff 责任。

如果自动化优先级错了，常见后果是脚本很多但证据很少。比如自动生成大量 RTL 和 GDS，却没有稳定的 SDC、CDC waiver、coverage closure 和 QoR regression，团队会在 tapeout 前才发现基础假设不成立。

## 上下游接口

EDA flow 上游接收 PRD、架构规格、RTL、testbench、SDC、UPF、IP collateral 和 PDK。下游输出 netlist、reports、GDS/OASIS、waiver、test patterns、signoff evidence 和量产测试数据。每个接口都应版本化，并能追溯到 commit、工具版本和配置。

## 典型场景

一个团队用 agent 从 C model 生成 RTL，并用 Verilator 做快速仿真。早期看起来迭代很快，但综合后出现大量 latch、multi-driver、CDC violation 和时序不可收敛。正确做法不是停止自动生成，而是把生成结果接入 lint、CDC、synthesis smoke test、formal equivalence 和 coding guideline check，让 agent 的输出接受硬件 flow 约束。

## 创业公司取舍

创业公司可以用开源工具做低成本前置过滤，用商业工具做关键 signoff，用外包团队执行专业后端。但必须内部保留 flow 负责人和数据 owner。否则你无法判断是 RTL 问题、约束问题、工具脚本问题、IP collateral 问题还是供应商执行问题。

## 常见坑

- 把工具报告 count 当成质量指标，不看 violation 类型和 waiver 依据。
- 不固定工具版本和 PDK 版本，导致结果不可复现。
- SDC/UPF 由少数人手写，没有 review 和回归。
- 只在 tapeout 前跑 signoff，发现问题时已经没有 schedule buffer。
- 以为开源 EDA 成功跑完就等价于 foundry-ready。

## 后续阅读

- [RTL 设计工程实践](../02_frontend_design_and_verification/01_rtl_design_practices.md)
- [Synthesis Preparation](../02_frontend_design_and_verification/04_synthesis_preparation.md)
- [DRC/LVS Signoff](../03_backend_physical_design/07_drc_lvs_signoff.md)
- [开源芯片策略](./03_open_source_silicon.md)

## 参考公开来源

- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)
- [Siemens Calibre nmDRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/)
- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Cadence Innovus](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff/soc-implementation-and-floorplanning/innovus-implementation-system.html)

## 内容可信度说明

- **公开信息（高可信）**：主流 EDA 工具类别、常见工具名称、输入输出格式和 signoff 类型。
- **行业惯例（中可信）**：商业/开源混合 flow、reproducible flow、signoff checklist 和 dashboard 实践。
- **经验性观察（中低可信）**：agent 生成 RTL 必须进入硬件 EDA 约束闭环，否则会快速制造不可维护问题。
- **不确定/需向资深工程师确认（低可信）**：具体工具报价、foundry 认证工具版本、license 条款和先进节点 signoff methodology。
