# Open Source Silicon：开源芯片策略

## 前置知识

- 建议先读 [IP Strategy](../01_product_definition_and_architecture/04_ip_strategy.md)。
- 建议先读 [EDA 工具版图](./01_eda_tools_landscape.md)。
- 建议理解 [Open Source Silicon](../00_overview/05_glossary.md#open-source-silicon)、[IP](../00_overview/05_glossary.md#ip)、[PDK](../00_overview/05_glossary.md#pdk)、[RTL](../00_overview/05_glossary.md#rtl)、[Verification](../00_overview/05_glossary.md#verification)。

## 核心概念

Open source silicon 可以指开源 RTL、开源验证环境、开源 EDA、开放 PDK、开放封装/板卡设计、开源编译器和开源固件。它不是一个单一概念。不同层的开放程度、法律风险和工程价值完全不同。

你计划第一版芯片全栈开源 RTL 和编译器，这有战略价值：吸引开发者、建立信任、降低客户评估门槛、让生态参与优化软件栈。但要诚实区分“可公开的设计资产”和“受 NDA/商业许可证约束的制造资产”。PDK、商业 IP、foundry rule deck、SRAM compiler、timing library、GDS signoff collateral 通常不能公开。

## 开源范围分层

最适合开源的是架构文档、ISA/编程模型、RTL、C model、compiler、runtime、driver、SDK、仿真环境、FPGA prototype、test cases、benchmark harness 和部分形式化属性。这些内容有利于生态协作和客户验证。

谨慎开源的是验证环境、UVM components、performance model 和 microarchitecture 文档。开源能提高可信度，但也会暴露设计细节、攻击面和竞争策略。需要明确许可证、贡献流程和安全审查。

通常不能开源的是 foundry PDK、商业 IP、EDA rule deck、标准单元库、SRAM macro、PHY hard macro、某些 timing/power model、客户 workload、供应商报价和签核报告中的 NDA 内容。

## 关键活动顺序

第一步是定义 open-source boundary。明确哪些 repo 公开、哪些私有、哪些由 CI 自动同步、哪些永不出现在公开日志。这个边界必须在 PDK 和 IP NDA 签署前设计好。

第二步是选择许可证。RTL 常见 Apache-2.0、BSD/MIT、Solderpad、CERN-OHL 等路线；软件可用 Apache-2.0、MIT、GPL/LGPL 等。不同许可证对专利、衍生作品、商业使用和贡献回流的影响不同，应让律师参与。

硬件开源还要考虑 patent grant、mask work、第三方贡献的 DCO/CLA、出口管制、安全漏洞披露和商标使用。软件领域的经验不能直接套到芯片，因为 RTL 可能被综合成产品，贡献者权利、专利和制造责任更复杂。

第三步是建立贡献和验证流程。外部 PR 不能直接进入芯片 tapeout 分支。需要 lint、仿真、formal、coverage、review、security check 和 maintainership。开源不是降低验证要求，而是增加协作入口。

第四步是建立公开文档与私有 signoff 的映射。公开 RTL commit 如何对应私有 PDK-dependent synthesis、STA、DRC/LVS 和 tapeout artifact，要有 release tag 和 reproducibility 说明。否则客户无法知道“开源代码”和“实际硅片”是否一致。

第五步是设计商业模式。开源 RTL/编译器不等于放弃商业化。收入可以来自芯片销售、开发板、云服务、企业支持、定制 IP、验证服务、软件优化、系统集成或生态优势。

## 工具和生态

开源生态包括 CHIPS Alliance、OpenROAD、Yosys、Verilator、Cocotb、KLayout、OpenLane、RISC-V 社区、FOSSi Foundation、LibreCores 等。商业生态仍包括 Synopsys、Cadence、Siemens、Ansys、foundry IP partners 和 OSAT。

对 AI 芯片，开源编译器和 runtime 可能比开源 RTL 更直接影响采用。客户通常先关心模型能否跑、性能是否稳定、调试是否方便、软件 API 是否可靠。开源 RTL 提高透明度，但不能替代成熟软件栈。

## 角色、周期和成本

需要的角色包括开源维护者、架构师、RTL lead、verification lead、compiler/runtime lead、DevRel、security reviewer、legal/IP counsel 和 release manager。开源项目不是把 repo 设为 public，而是长期维护社区、issue、PR、版本和安全披露。

周期上，开源准备通常应在首个公开 release 前提前数周到数月启动：清理 NDA 内容、补文档、建立 CI、确定许可证、写 contribution guide、建立安全披露流程。开源之后是持续投入，不是发布当天结束。每个 silicon revision、compiler release、errata 和客户 workaround 都可能需要同步公开文档。

成本包括文档、CI、代码清理、许可证审查、贡献管理、公开 bug 响应、社区沟通和私有/公开分支同步。量级上，小团队维护高质量开源硬件项目至少需要持续投入工程人力；如果开源范围包含编译器和 runtime，投入会接近一个完整软件产品。可省的是市场教育和部分客户评估成本；不能省的是验证、release 管理、法律审查、安全响应和长期维护。

## 关键决策点

第一个决策是开源目标。是为了社区创新、客户信任、招聘、融资叙事、生态兼容，还是为了降低内部开发成本？目标不同，开源范围和治理不同。

第二个决策是许可证和专利策略。硬件开源涉及专利、mask work、商业 IP 和衍生设计，不能只套用软件经验。对外说“全栈开源”前，要明确不包括哪些 NDA collateral。

第三个决策是贡献进入 tapeout 的规则。外部贡献是否能进入硅片，必须有验证门槛和责任归属。否则开源会变成质量风险入口。

第四个决策是公开 errata。开源公司更容易被期待透明，但也要控制客户沟通和法律风险。可以公开技术事实和 workaround，但不要在证据不足时随意定性。

错误开源决策的后果很具体：如果公开了含 NDA 信息的 PDK wrapper 或 timing model，可能违反合同；如果许可证不清，企业客户可能不敢采用；如果公开 RTL 与实际硅片不一致，社区和客户会质疑透明度；如果外部贡献未经充分验证进入 tapeout，bug 责任会很难界定。

## 上下游接口

上游来自产品定位、IP 策略、foundry NDA 和法律框架。下游影响验证、EDA flow、tapeout、客户支持和生态建设。开源 repo 需要与私有 signoff repo、软件 release、客户版本和 silicon revision 建立映射。

## 典型场景

公司公开 NPU RTL、C model、compiler 和仿真环境，但 PCIe PHY、DDR/HBM PHY、SRAM macro 和 PDK-dependent wrapper 保持私有。公开 CI 使用 Verilator/Yosys/OpenROAD 的成熟节点示例进行 sanity check；私有 CI 使用商业工具完成 7nm signoff。这样既能让社区理解架构和软件，又不违反 foundry/IP NDA。

如果团队把“全栈开源”解释为所有制造文件都公开，很可能在签 PDK/IP 合同时碰壁，甚至违反 NDA。

## 创业公司取舍

开源最适合放大你的软件和架构优势，但它不会自动解决验证、后端、foundry 和量产问题。第一版芯片的务实策略是：把可复用、可讨论、可测试的软件/架构层开放；把受 NDA 约束的制造层私有；把开源代码和实际硅片的一致性用 release tag、hash、文档和测试结果说明清楚。

## 常见坑

- 把开源当营销，不投入文档、CI 和维护。
- 忽略许可证和专利，后续商业客户不敢采用。
- 开源 RTL 没有足够验证，社区发现大量低级问题，反而损害可信度。
- 不区分公开模型和私有 signoff collateral。
- 软件栈不开源或不好用，只开 RTL，客户仍然无法评估产品。

## 后续阅读

- [IP Strategy](../01_product_definition_and_architecture/04_ip_strategy.md)
- [EDA 工具版图](./01_eda_tools_landscape.md)
- [MPW 策略](./04_mpw_shuttle_strategy.md)
- [First Chip Pragmatics](../07_for_software_background_founders/04_first_chip_pragmatics.md)

## 参考公开来源

- [CHIPS Alliance about page](https://www.chipsalliance.org/about/who-we-are/)
- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)
- [CERN Open Hardware Licence](https://ohwr.org/cern_ohl_p_v2.txt)
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

## 内容可信度说明

- **公开信息（高可信）**：开源工具/组织、常见许可证、PDK/IP NDA 与开源边界的基本事实。
- **行业惯例（中可信）**：公开 repo 与私有 signoff repo 分离、贡献门禁、release tag 映射和许可证审查。
- **经验性观察（中低可信）**：AI 芯片开源策略中，编译器/runtime 的采用价值可能高于 RTL 透明度本身。
- **不确定/需向资深工程师确认（低可信）**：具体许可证法律解释、专利风险、foundry/IP NDA 允许的公开范围和客户安全要求。
