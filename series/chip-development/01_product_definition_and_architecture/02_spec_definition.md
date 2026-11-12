# 规格定义

## 前置知识

- 建议先读 [市场与 Workload 分析](./01_market_and_workload_analysis.md)。
- 建议先读 [角色和团队职责](../00_overview/02_roles_and_teams.md)。
- 遇到术语可查 [关键术语表](../00_overview/05_glossary.md)。

## 规格的本质

芯片规格不是宣传材料，也不是架构师个人脑中的设计意图。规格是产品、架构、RTL、验证、软件、后端、DFT、硅后、商务之间的工程契约。它定义“这颗芯片承诺做什么、不做什么、如何判断做对了”。

软件背景的人容易把规格写成 API 文档或 feature list。芯片规格必须更硬。它要包含功能行为、接口时序、性能目标、功耗模式、复位和异常行为、可观测性、可测试性、软件可见寄存器、版本兼容性、验证标准和签核条件。模糊规格会让后续团队在实现过程中自行解释，最终在 [Verification](../00_overview/05_glossary.md#verification)、硅后或客户现场暴露冲突。

## 规格层次

产品需求规格定义客户可见能力，例如目标 workload、性能、功耗、接口、软件兼容性、封装形态、价格区间和供货要求。这一层由产品、系统架构、CEO 和客户输入共同驱动。

芯片系统规格定义 [SoC](../00_overview/05_glossary.md#soc) 组成，例如 [NPU](../00_overview/05_glossary.md#npu)、CPU/control core、memory controller、DMA、[NoC](../00_overview/05_glossary.md#noc)、PCIe、DDR/HBM、安全、调试、时钟、电源和中断。它把产品需求转换为硬件系统边界。

架构规格定义 [Architecture](../00_overview/05_glossary.md#architecture) 行为，例如编程模型、指令或 command queue、内存一致性、精度语义、异常处理、资源隔离、性能计数器和软件 ABI。它是硬件和软件之间最重要的契约。

模块规格定义 block-level 行为，例如接口协议、寄存器、FIFO 深度、状态机、仲裁策略、错误上报、复位行为和时序假设。它是 [RTL](../00_overview/05_glossary.md#rtl) 设计和验证的直接输入。

## 规格应包含什么

| 规格项 | 内容 | 常见遗漏 |
|---|---|---|
| 产品目标 | workload、性能、功耗、价格、客户场景 | 只写峰值 [TOPS](../00_overview/05_glossary.md#tops) |
| 编程模型 | command、kernel、队列、同步、内存模型 | 软件如何使用不清楚 |
| 数据精度 | FP16、BF16、INT8、INT4、舍入、饱和、异常 | 精度边界和误差未定义 |
| 内存系统 | SRAM、cache、DMA、外部内存、地址空间 | 带宽和容量只估平均值 |
| 接口 | PCIe、DDR/HBM、JTAG、I2C/SPI、以太网 | IP 版本和 PHY 依赖未锁定 |
| 功耗模式 | active、idle、sleep、clock gating、power gating | 唤醒延迟和状态保持未定义 |
| 复位和启动 | reset source、boot flow、secure boot、fallback | 多复位域行为模糊 |
| 错误处理 | ECC、parity、timeout、非法命令、错误码 | 错误无法定位或恢复 |
| 可观测性 | performance counter、trace、debug register | 硅后 debug 不够 |
| DFT 约束 | scan、MBIST、JTAG、test mode | 太晚引入导致返工 |
| 验证标准 | test plan、coverage、golden model、signoff | 没有“完成”的定义 |

这里的 [Golden Model](../00_overview/05_glossary.md#golden-model) 必须与规格一致。对 AI 芯片，尤其要写清楚数值语义：舍入模式、溢出、NaN/Inf、denormal、量化 scale、accumulator 位宽、随机性和非确定性。如果这些不写，RTL、编译器和客户模型可能都“各自正确”。

## 关键活动顺序

第一步是把市场和 workload 输入转成 measurable requirements。不要写“高性能”，要写目标场景下的吞吐、延迟、功耗和内存容量范围。不要写“支持主流模型”，要列出第一版支持模型类别和不可支持项。

第二步是定义系统边界。芯片是加速器、完整 SoC、chiplet、PCIe 卡上的 device，还是嵌入式主控芯片。边界决定软件、封装、测试和客户集成方式。

第三步是定义硬件/软件契约。包括寄存器、队列、内存模型、同步、错误处理、驱动接口和编译器 IR 约束。对全栈开源芯片，这部分应尽量稳定，因为外部社区会围绕它构建工具。

第四步是把规格映射到验证计划。每个 must requirement 都应能被仿真、formal、emulation、FPGA prototype、硅后测试或客户 benchmark 验证。无法验证的规格是风险，不是愿景。

第五步是规格评审和冻结。冻结不代表永远不改，而是任何变更必须有影响评估：RTL、验证、后端、DFT、软件、IP、成本和进度。

## 工具和文档管理

规格文档可以用 Markdown、AsciiDoc、Sphinx、Doxygen、Confluence、Notion 或内部文档系统。寄存器规格建议使用结构化格式生成，例如 SystemRDL、PeakRDL、IP-XACT、自研 YAML/JSON，再生成 RTL package、C header、文档和验证模型。这样可以减少文档、RTL 和软件头文件不一致。

需求跟踪可以使用 Jira、Linear、GitHub Issues、Polarion 或 Jama。关键不是工具，而是每个 requirement 有 ID、owner、状态、验证方式和变更记录。芯片项目里规格漂移比文档格式更危险。

接口规格要尽量引用公开标准或 vendor 文档。例如 PCIe 参考 PCI-SIG 规范，RISC-V 参考 RISC-V International 规范，UCIe 参考 UCIe Consortium 规范。自定义协议需要写得比公开协议更严，因为没有外部生态帮你纠错。

## 角色、时长与交付物

产品负责人定义客户可见需求和优先级。系统架构师负责把需求转成芯片系统规格。架构负责人定义编程模型和关键硬件行为。RTL owner 评估可实现性。验证负责人把规格转成 test plan 和 coverage。软件负责人确认驱动、编译器和 runtime 能使用这些能力。后端和 DFT 负责人提前审查时钟、电源、测试和物理实现约束。商务、法务和供应链负责人审查 IP、标准、许可和交付风险。

规格定义通常贯穿早期数月。第一版产品和架构规格可以在数周内形成，但模块规格、寄存器规格和验证映射会随架构探索继续细化。进入 RTL 大规模开发前，关键系统规格和硬件/软件契约必须冻结到足够稳定。

交付物包括 [PRD](../00_overview/05_glossary.md#prd)、SoC 规格、架构规格、寄存器规格、接口协议、内存模型、错误处理文档、boot/reset 文档、power state 文档、debug/trace 文档、DFT 初始需求、验证需求追踪表和规格变更流程。

## 关键决策点

第一个决策是 spec 的 must/should/could 分级。must 是第一颗芯片必须实现且必须验证的能力。should 是有明确价值但可延期的能力。could 是探索项。创业公司如果不分级，项目会被 feature creep 拖垮。

第二个决策是软件兼容性边界。是否兼容 PyTorch、ONNX、MLIR、RISC-V、PCIe、Linux driver、容器部署，决定客户迁移成本。完全自定义软件栈可能提高硬件自由度，但会显著增加市场导入难度。

第三个决策是错误处理和 debug 能力。早期为了省面积砍掉 trace buffer、performance counter、错误寄存器和内部可观测点，硅后会付出高代价。AI 芯片的性能 bug 往往不是“功能全错”，而是某个队列、DMA、NoC 或 memory scheduler 造成利用率下降，没有观测点就很难定位。

第四个决策是规格冻结门槛。过早冻结会锁死错误假设，过晚冻结会导致 RTL 和验证反复返工。合理做法是先冻结外部接口和软件契约，再逐步冻结内部微架构参数。

## 成本视角

规格阶段最容易省的是文档形式和工具复杂度，最不该省的是需求编号、owner、版本控制、变更记录和验证映射。一个轻量 Markdown + Git review + 结构化寄存器生成流程，通常比重型流程更适合早期创业公司；但“口头 spec”不是轻量流程，而是把成本推给后面的 RTL、验证和硅后团队。

错误规格会以三种方式转化为成本。第一是人力成本：接口反复改会让 RTL、验证、driver、compiler、文档同步返工。第二是验证成本：未定义行为会导致 testbench 和 golden model 无法判定对错，回归时间和 bug triage 成本上升。第三是硅后成本：debug 寄存器、错误码、性能计数器、reset/boot 行为如果没定义，首硅问题定位会变慢，严重时需要 [Respin](../00_overview/05_glossary.md#respin)。

创业公司可以把规格写得短，但不能把关键问题留白。能省的是“漂亮模板”，不能省的是“可执行合同”。

## 常见错误

如果精度语义不清，编译器、C model 和 RTL 可能在 rounding 上不一致，硅后发现模型 accuracy 掉点时无法判断是硬件 bug 还是软件映射问题。

如果内存模型不清，驱动和硬件对 cache coherency、DMA ordering、barrier 的理解可能不同，系统会出现随机错误。这类问题常常在小 demo 中不出现，在高并发或长时间运行时出现。

如果 reset 和 boot flow 不清，首硅 bring-up 可能卡在最早阶段。硬件不是软件进程，复位释放顺序、时钟稳定、PLL lock、JTAG 访问和 boot ROM 行为都必须定义。

如果规格没有验证映射，项目后期会出现“RTL 做完了但不知道是否足够验证”的状态，signoff 变成主观争论。

## 创业公司视角下的取舍

可以省的是文档形式，不可以省的是规格清晰度。Markdown 文档加结构化寄存器生成完全可以起步，但每个关键需求必须有 owner、版本和验证方式。

第一颗芯片建议把规格写得更保守。少做不可验证的复杂功能，多做可调试、可测量、可解释的功能。对开源芯片，规格还承担社区接口的角色，后续破坏兼容性会影响外部贡献者和软件生态。

AI Agent 可以帮助检查规格一致性、从规格生成寄存器文档、生成验证 checklist、对比 C model 和 RTL 接口。但 AI Agent 不能替代规格 owner 的责任。规格中的业务取舍、客户承诺和风险接受必须由团队负责人签字。

## 典型场景

团队定义一个 tensor command queue。最初规格只写“host 提交任务，NPU 执行完成后中断”。验证负责人追问后发现缺少关键细节：队列在内存中的布局、descriptor 对齐、非法地址处理、任务取消、timeout、多个进程并发、错误恢复、中断合并、doorbell 顺序、cache flush 要求和性能计数器。

如果这些问题在 RTL 后才补，DMA、MMU、driver、runtime 和验证环境都会返工。正确做法是在规格阶段把 command 生命周期画成状态机，列出每个状态下软件和硬件的责任，并为每个错误路径定义可观测寄存器和测试用例。

## 后续阅读

- [03_architecture_exploration.md](./03_architecture_exploration.md)
- [04_ip_strategy.md](./04_ip_strategy.md)
- [06_milestones_and_signoffs.md](./06_milestones_and_signoffs.md)
- [RTL 设计工程实践](../02_frontend_design_and_verification/01_rtl_design_practices.md)
- [前端验证方法学](../02_frontend_design_and_verification/03_verification_methodology.md)

## 参考公开来源

- [RISC-V International Ratified Specifications](https://riscv.org/specifications/ratified/)
- [PCI-SIG PCI Express Specifications](https://pcisig.com/specifications)
- [UCIe Consortium Specifications](https://www.uciexpress.org/specifications)
- [Accellera IP-XACT](https://www.accellera.org/downloads/standards/ip-xact)
- [Accellera SystemRDL](https://www.accellera.org/downloads/standards/systemrdl)

## 内容可信度说明

- **公开信息（高可信）**：公开接口标准、寄存器描述标准、需求和接口规格对硬件/软件协作的重要性。
- **行业惯例（中可信）**：PRD、SoC 规格、架构规格、模块规格、寄存器规格和验证映射的分层方式；must/should/could 分级。
- **经验性观察（中低可信）**：创业团队容易把规格写成 feature list；debug、错误处理、reset 和数值语义经常被低估。
- **不确定/需向资深工程师确认（低可信）**：具体公司采用的规格模板、客户要求的文档格式、安全认证要求、功能安全或车规项目的额外规格流程。
