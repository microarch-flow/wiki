# Recruitment Priorities：创业初期招聘优先级

## 前置知识

- 建议先读 [角色和团队职责](../00_overview/02_roles_and_teams.md)。
- 建议先读 [常见误区](./01_common_misconceptions.md)。
- 建议理解 [RTL](../00_overview/05_glossary.md#rtl)、[Verification](../00_overview/05_glossary.md#verification)、[DFT](../00_overview/05_glossary.md#dft)、[Physical Design](../03_backend_physical_design/README.md)、[ATE](../00_overview/05_glossary.md#ate)。

## 招聘原则

芯片创业早期最危险的组织形态是“很多聪明软件/架构人 + 没有做过完整芯片交付的人”。你可以用自动化提高效率，但必须有经历过 tapeout、硅后和量产问题的人定义工程底线。

招聘不是补简历关键词，而是补风险 owner。每个关键风险都要有人能判断：RTL 是否工程化、验证是否足够、DFT 是否可测、后端是否可收敛、IP 是否可集成、封装测试是否可执行、客户现场问题如何闭环。

## 第一优先级：芯片工程总负责人

这个人可以是 VP Engineering、Head of Silicon 或非常资深的芯片项目负责人。必须做过完整 ASIC/SoC 项目，理解 spec -> RTL -> verification -> DFT -> backend -> tapeout -> bring-up 的真实接口。最好经历过至少一次硅后问题或 respin，而不是只做过局部 block。

职责是建立工程节奏、signoff gate、外包边界、风险列表和跨团队决策机制。他不一定亲自写最多 RTL，但要能判断哪些问题不能带到 tapeout。

错误招聘：只找一个“很强 RTL 工程师”当总负责人，但他没管理过后端、DFT、验证和硅后。结果项目在局部设计上很强，系统交付失控。

## 第二优先级：验证负责人

对你这种背景，验证负责人比多招几个 RTL 工程师更关键。因为 agent/C model/自动生成可以提高 RTL 产出速度，但验证能力决定这些产出是否可信。验证负责人要能建立 test plan、UVM/formal/assertion/coverage 方法、regression、bug triage 和 signoff 标准。

理想人选做过复杂 SoC 或 AI/CPU/NoC/accelerator 验证，知道 block-level 和 SoC-level 的分工，也能和软件/模型团队对齐 golden model。这个人要敢对创始人说“这个不能流片”。

## 第三优先级：后端/物理设计负责人或强外部顾问

如果第一颗芯片目标是先进节点，必须早期引入后端判断。即使后端执行外包，内部也需要人能审 floorplan、SDC、timing、IR/EM、DRC/LVS、ECO 和供应商报告。

没有后端负责人，软件/架构团队容易设计出理论漂亮但物理不可收敛的结构：超宽总线、过多跨 chip 通信、不合理 SRAM 分布、不可布线 NoC、过高频率目标和不现实电源域。

## 第四优先级：DFT/Test/Product Engineering

DFT 和 test 常被早期团队低估，因为它们不影响 demo 的功能路径。但没有 scan、MBIST、JTAG、test mode、ATE pattern 和 test strategy，芯片无法有效制造测试，量产良率和现场质量无法管理。

早期可以用顾问或外包补 DFT/test，但必须有人定义 DFT 架构和可测性要求。AI 芯片大量 SRAM 和复杂 clock/power domain，DFT 不能等 RTL freeze 后再“插进去”。

## 第五优先级：系统软件/编译器负责人

AI 芯片公司的软件不是附属。编译器、runtime、driver、firmware、debug tools 和 profiler 直接决定客户能否使用芯片。你自身有系统软件背景，这是优势，但仍需要能长期 ownership 的软件负责人，尤其是 ML compiler/runtime 方向。

软件团队要从 day 1 参与架构定义，而不是硅片回来后再适配。否则硬件提供的能力可能无法被编译器有效利用。

## 第六优先级：运营/供应链/质量

当项目接近 tapeout，必须补 operations、supply chain、quality/reliability、foundry/OSAT interface 和 product engineering。早期可以兼职或顾问，但不能等客户要交付时才建立。

这些岗位看起来不如 RTL/AI 架构“核心”，但它们决定 wafer start、封装测试、qualification、RMA 和客户交付。没有它们，公司会在首硅后陷入混乱。

## 招聘顺序建议

如果只能先招 5-8 个核心人，建议优先覆盖：芯片工程总负责人、验证负责人、RTL/microarchitecture lead、后端/PD lead 或资深顾问、DFT/test 顾问、compiler/runtime lead、firmware/driver lead、program manager。具体顺序取决于你已有能力和外包计划。

在你本人能承担架构探索、C model、工具链和部分软件的情况下，最不该重复招聘的是“更多和你相似的软件架构人”。最该补的是你没有经历过的硬件交付链条。

## 分阶段招聘计划

前 3 个关键补位应优先是芯片工程总负责人、验证负责人、compiler/runtime 或系统软件负责人。如果你本人能暂时承担软件负责人，则把第三个名额给 RTL/microarchitecture lead 或后端顾问。目标是在架构冻结前就有人能挑战 spec、验证计划和物理可行性。

架构冻结前应具备：芯片工程总负责人、验证负责人、架构/RTL lead、软件栈 owner、后端顾问。这个阶段后端可以是顾问，但必须参与 floorplan、频率、SRAM/NoC、IO 和 power 假设评审。

RTL freeze 前应具备：验证团队核心、DFT/test owner、后端/PD owner、firmware/driver owner、program manager。DFT/test 此时如果仍然缺位，后续很可能返工。

Tapeout 前应具备：硅后 bring-up owner、board/EVB owner、供应链/OSAT interface、质量/可靠性 owner 或顾问。否则样片回来后团队会临时拼流程。

Bring-up 前应具备：firmware/driver/compiler regression owner、lab owner、FAE/customer support owner、issue triage 机制。客户试用前还要有明确 errata、日志采集和版本管理。

内部 owner 与顾问/外包的边界可以这样划：芯片工程总负责人、验证标准、架构/RTL ownership、软件栈 ownership、客户承诺必须内部；后端执行、DFT 插入、FA、封装测试、部分供应链执行可以外包或顾问支持，但内部要能审结果。

## 面试重点

问候选人做过哪个 tapeout、负责哪些 signoff、遇到过什么硅后 bug、如何定位、是否经历过 respin、如何处理 waiver、如何和后端/验证/DFT 协作。不要只问算法、Verilog 语法或项目名称。

对验证负责人，问如何从 spec 建 test plan、如何定义 coverage closure、如何使用 formal、如何管理 regression、如何判断 tapeout readiness。对后端负责人，问 floorplan 失败案例、timing closure、IR/EM、macro placement、ECO 和 foundry signoff。对 DFT/test，问 scan/MBIST/JTAG/ATE/yield learning。

## 成本和股权视角

资深芯片人才贵，但早期缺这类人更贵。一个错误的 tapeout 或不可调首硅，成本可能远高于几名资深工程师的年薪和股权稀释。创业公司可以用顾问、兼职和外包缓解现金压力，但关键决策 owner 最好内部化。

要谨慎把核心岗位完全外包给顾问。顾问可以评审和救火，但不会像内部负责人一样为长期产品质量、团队成长和客户承诺负责。

量级上，资深芯片负责人、验证负责人、后端负责人和编译器负责人通常都是高成本岗位；但与先进节点 mask、EDA license、IP、外包后端、封装测试和一次 respin 相比，缺关键人的代价更大。务实做法是：早期用少数高质量内部 owner + 顾问网络 + 明确外包合同，而不是用大量初级人堆规模。

## 常见坑

- 招很多 RTL 工程师，却没有验证负责人。
- 招算法/模型人很多，却没有 compiler/runtime 和系统软件 owner。
- 后端完全外包，内部没人能审报告。
- 太晚招 DFT/test，导致可测性结构返工。
- 创始人用软件项目管理方式压硬件 signoff 时间。
- 没有 program manager，跨团队接口靠口头同步。

## 后续阅读

- [第一颗芯片务实建议](./04_first_chip_pragmatics.md)
- [快速迭代真实约束](./05_fast_iteration_realities.md)
- [角色和团队职责](../00_overview/02_roles_and_teams.md)

## 参考公开来源

- [Accellera UVM Working Group](https://www.accellera.org/activities/working-groups/uvm)
- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [Teradyne semiconductor test overview](https://www.teradyne.com/industries/semiconductor-test/)

## 内容可信度说明

- **公开信息（高可信）**：RTL、verification、DFT、physical design、ATE、foundry/OSAT 等角色类别和职责。
- **行业惯例（中可信）**：早期芯片团队需要验证、后端、DFT/test、软件、运营质量等核心 owner。
- **经验性观察（中低可信）**：软件背景创始人最容易过招架构/软件、欠招验证/后端/DFT/运营。
- **不确定/需向资深工程师确认（低可信）**：具体招聘顺序、薪酬股权、候选人市场和外包/内部化比例。
