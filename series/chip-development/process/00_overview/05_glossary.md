# 关键术语表

## 前置知识

- 无。本文件是全 Wiki 的术语入口。
- 建议配合 [01_full_lifecycle.md](./01_full_lifecycle.md) 阅读。

## ASIC

Application-Specific Integrated Circuit，专用集成电路。与 FPGA 不同，ASIC 最终会制造成固定功能的硅片，单位成本和能效通常更好，但前期 [NRE](#nre) 高，修改成本高。

## SoC

System on Chip，片上系统。把计算核心、存储控制器、互连、外设、安全、调试和电源管理等集成到一颗芯片中。AI 芯片通常是 SoC，而不只是一个矩阵乘单元。

## PPA

Power、Performance、Area，即功耗、性能、面积。芯片设计的核心三角。提高性能可能增加面积和功耗，降低功耗可能牺牲频率或面积。先进节点选择、架构、后端实现都围绕 PPA 取舍。

## RTL

Register Transfer Level，寄存器传输级描述。通常用 Verilog/SystemVerilog 编写，描述时钟边界上的寄存器和组合逻辑。RTL 不是普通软件代码，它会被综合成真实硬件结构。

## C Model

用 C/C++ 或类似语言实现的功能或性能模型。它常作为 reference model、架构探索工具或验证对照。C model 正确不等于 RTL 正确，因为 C model 通常不完整表达时序、并行、资源冲突、复位和物理约束。

## Workload

芯片实际要处理的任务集合，包括模型、输入 shape、batch size、数据精度、算子分布、内存访问、延迟和吞吐要求。AI 芯片的架构定义应由 workload 驱动，而不是只由峰值算力指标驱动。

## PRD

Product Requirements Document，产品需求文档。它把客户场景、功能范围、性能、功耗、成本和交付目标写成产品层面的约束。芯片 PRD 必须能继续分解为架构规格、验证计划和成本模型。

## TOPS

Tera Operations Per Second，每秒万亿次操作。常用于宣传 AI 芯片峰值算力，但它不能单独代表真实性能。真实客户更关心目标 workload 下的利用率、延迟、功耗、软件可用性和成本。

## NPU

Neural Processing Unit，神经网络处理单元。通常指面向矩阵乘、卷积、attention、量化等 AI workload 优化的加速器核心。NPU 只是 AI SoC 的一部分，外部内存、NoC、DMA、软件栈同样关键。

## NoC

Network on Chip，片上网络。用于连接计算单元、SRAM、DMA、CPU、外设和内存控制器。NoC 设计会影响带宽、延迟、功耗、拥塞、验证复杂度和后端布局布线。

## SerDes

Serializer/Deserializer，串并转换高速接口电路。常用于 PCIe、Ethernet、chiplet、die-to-die 等高速链路。SerDes 是强模拟/混合信号 IP，依赖工艺、封装、板级信号完整性和 vendor 支持。

## Golden Model

验证中的参考模型。RTL 输出会与 golden model 对比。Golden model 必须定义清楚精度、舍入、异常行为和未定义行为，否则会产生“模型和硬件谁对”的争议。

## Architecture

架构。定义芯片对外呈现的能力、编程模型、数据流、存储层级和系统边界。架构回答“产品应该支持什么能力”。

## Microarchitecture

微架构。把架构规格细化成 pipeline、buffer、arbiter、FSM、cache、queue、接口时序等实现结构。架构说明“做什么”，微架构说明“怎么用硬件做”。

## UVM

Universal Verification Methodology，通用验证方法学，由 Accellera/IEEE 标准化体系维护，用于构建可复用 SystemVerilog 验证环境。UVM 常用于复杂 ASIC/SoC 验证，但它本身不是质量保证，关键仍是 test plan、coverage、assertion 和 scoreboard。

## Formal Verification

形式验证。用数学方法证明设计满足某些属性，常用于协议、仲裁、死锁、等价性和安全属性检查。它不能自动证明整个大 SoC 都正确，但能有效覆盖仿真难以穷尽的状态空间。

## Emulation

硬件仿真/加速验证。用专用 emulation 硬件运行大规模设计，速度通常高于软件仿真，适合 SoC 级软件 bring-up、长场景测试和性能验证。它成本高，不能替代 block-level 验证。

## Lint

RTL 静态检查。发现潜在编码问题，例如未驱动信号、隐式锁存器、位宽不匹配、不可综合写法和风格违规。Lint clean 不代表功能正确，但 lint 不干净通常说明工程纪律不足。

## CDC

Clock Domain Crossing，时钟域跨越。信号从一个时钟域进入另一个时钟域时可能产生亚稳态，需要同步器、异步 FIFO 或握手机制。CDC bug 可能仿真不容易复现，但硅上随机出现。

## RDC

Reset Domain Crossing，复位域跨越。不同复位信号或复位释放顺序导致的问题。软件背景的人容易低估 reset，因为软件进程重启和硬件复位不是一回事。

## DFT

Design for Test，可测性设计。通过 scan chain、MBIST、LBIST、JTAG 等结构让制造后的芯片可测试。DFT 影响良率筛选、测试时间和量产质量。

## Scan Chain

扫描链。把触发器串接起来，使 ATE 可以控制和观察内部状态。scan 会增加面积、功耗和时序约束，但没有 scan 很难做制造测试。

## MBIST

Memory Built-In Self-Test，存储器内建自测试。用于测试 SRAM 等片上存储器。AI 芯片含大量 SRAM，MBIST 通常非常重要。

## Synthesis

综合。把 RTL 转换为门级网表。常见工具包括 Synopsys Design Compiler、Cadence Genus。综合需要标准单元库和时序约束。

## Netlist

网表。描述逻辑门、触发器、宏单元及其连接关系。综合后网表进入后端物理设计。

## SDC

Synopsys Design Constraints，时序约束文件格式。定义 clock、input/output delay、false path、multi-cycle path 等。错误约束会让 STA 结果失真。

## STA

Static Timing Analysis，静态时序分析。检查所有时序路径在各种 PVT corner 下是否满足 setup/hold 要求。STA 是芯片 signoff 核心之一。

## Floorplan

布局规划。决定 die size、macro 位置、IO 位置、电源网格、区域划分和主要数据流。错误 floorplan 会导致拥塞、时序失败、IR drop 或面积浪费。

## Placement

布局。把标准单元放到物理位置。Placement 会影响线长、拥塞、时序和功耗。

## CTS

Clock Tree Synthesis，时钟树综合。构建时钟分发网络，控制 skew、latency、功耗和时序。时钟网络通常是高功耗和高风险结构。

## Routing

布线。连接所有信号线和电源网络。先进节点布线受 pin access、金属层规则、SI、DRC、多重图形化/EUV 约束影响。

## DRC

Design Rule Check，设计规则检查。确认版图符合 foundry 工艺规则。DRC clean 是 tapeout 基本条件之一。

## LVS

Layout Versus Schematic，版图与网表一致性检查。确认物理版图实现与电路网表一致。LVS 不通过意味着版图可能不是你想要的电路。

## IR Drop

电源网络上的电压下降。IR drop 过大可能导致时序失败或功能异常。AI 芯片峰值电流大，电源完整性尤其关键。

## EM

Electromigration，电迁移。长期大电流会造成金属迁移和可靠性问题。EM signoff 关系到寿命和量产可靠性。

## ECO

Engineering Change Order，工程修改。用于在后期修复 bug 或时序问题。ECO 可以是 RTL ECO、netlist ECO、metal ECO。越晚 ECO 成本越高。

## Signoff

签核。某阶段达到可进入下一阶段的证据集合。例如 verification signoff、DFT signoff、physical signoff。Signoff 不是简单盖章，而是明确风险是否可接受。

## 流片 Tapeout

把最终 GDSII/OASIS 数据交给 foundry 制造 mask 和晶圆的里程碑。Tapeout 后修改成本剧增，严重 bug 可能需要 respin。

别名：Tapeout、流片、交付 GDS。

## GDSII

常见版图数据格式，用于把物理版图交付给 foundry。先进流程也可能使用 OASIS。GDSII/OASIS 是 tapeout package 的核心之一。

## OASIS

Open Artwork System Interchange Standard，常见版图数据格式之一。相比 GDSII，OASIS 对大规模先进节点版图通常更紧凑。Foundry tapeout package 可能接受 GDSII、OASIS 或指定格式。

## LEF/DEF

Library Exchange Format / Design Exchange Format。LEF 描述标准单元、macro、routing layer 等物理抽象；DEF 描述设计实例、位置、连线等实现结果。后端实现和 IP 集成高度依赖 LEF/DEF 版本一致性。

## Liberty

`.lib` 时序/功耗库格式。描述 standard cell、macro、IO 等在不同 PVT corner 下的 timing、power、constraint 信息。综合、STA、功耗分析都依赖 Liberty 文件。

## SPEF

Standard Parasitic Exchange Format，标准寄生参数交换格式。后端抽取 routing 后的电阻电容，STA 和功耗分析使用 SPEF 得到更真实的 delay 和功耗。

## UPF

Unified Power Format，IEEE 1801 标准功耗意图格式。描述 power domain、isolation、retention、level shifter、power state 等。低功耗验证、综合、后端实现和 signoff 需要保持 UPF 与 RTL 一致。

## RC Tech File

寄生抽取技术文件。描述工艺金属层、电阻、电容、via 等抽取模型。StarRC、Quantus 等工具会使用它从版图提取寄生参数。

## Mask Cost

掩模版成本。Foundry 根据版图制作光罩用于光刻。先进节点 mask 数量多、复杂度高，full mask 成本通常达到百万美元以上量级，具体取决于节点和商务条件。

别名：mask、光罩、掩模版成本。

## Wafer

晶圆。芯片在晶圆上批量制造，之后经过测试、切割和封装。单颗成本与 wafer price、die size 和良率相关。

## Yield

良率。可销售良品占比。良率受工艺缺陷、die size、设计鲁棒性、封装、测试和量产成熟度影响。良率直接决定毛利。

别名：yield、良率。

## OSAT

Outsourced Semiconductor Assembly and Test，外包封装测试厂。负责封装、组装、wafer sort、final test、部分可靠性或物流服务。OSAT 能力会影响成本、良率、交期和质量。

## ATE

Automatic Test Equipment，自动测试设备。用于 wafer sort、final test、量产筛选、部分 characterization 和失效复测。ATE test time 是量产成本的重要变量。

## Probe Card

探针卡。wafer sort 时连接晶圆上 die pad/bump 的测试硬件。高 pin count 或高速测试会提高 probe card 成本和复杂度。

## Package

封装。把 die 连接到外部系统，并提供机械保护、散热和电气连接。AI 芯片可能使用 BGA、2.5D、CoWoS、fan-out 等方案。

## HBM

High Bandwidth Memory，高带宽存储器。常用于高端 AI 加速器。HBM 提供高带宽，但带来先进封装、供应链和成本复杂度。

## Chiplet

小芯片/芯粒。把大 SoC 拆成多个 die，通过封装互连集成。优点可能包括良率、复用和异构节点，代价是封装、互连、测试和软件复杂度。

## MPW Multi Project Wafer

多项目晶圆。多个设计共享一片晶圆和 mask 成本，适合原型验证和小面积 test chip。MPW 不等于量产流片，面积、节点、封装和时间窗口受限制。

## PDK

Process Design Kit，工艺设计套件。Foundry 提供的工艺规则、模型、库和参考文件集合。没有 PDK 很难进行真实物理设计和 signoff。

## Open Source Silicon

开源芯片/开源硅。通常指开源 RTL、验证环境、EDA flow、编译器、固件或部分 PDK 生态。它不等于所有制造文件公开；商业 PDK、IP、rule deck 和 signoff collateral 常受 NDA 限制。

## Turnkey

一站式设计或制造服务。供应商承担后端、DFT、tapeout、封装测试、制造管理等一揽子工作。Turnkey 能降低执行门槛，但不能替代芯片公司自己的产品判断和质量责任。

## Test Chip

测试芯片。用于验证某个 IP、工艺、EDA flow、封装、DFT 或架构假设的小规模芯片。Test chip 的目标是学习和降风险，不一定直接成为产品。

## OpenROAD

开源 RTL-to-GDS EDA 项目和工具集合。常用于开放 PDK、教育、研究、小型设计和部分成熟节点探索。它对降低入门门槛很有价值，但先进节点量产 signoff 通常仍依赖 foundry 认可的商业工具链。

## OpenLane

基于开源工具构建的自动化 ASIC flow，常与开放 PDK 和 OpenROAD 生态一起使用。适合学习、原型和部分成熟节点实验，但不应直接等同于先进节点商业 signoff flow。

## RISC-V

开放指令集架构。RISC-V ISA 开放不等于所有实现免费或已验证；具体 core、SoC、验证环境、调试、软件和商业支持仍需要工程评估。

## Standard Cell Library

标准单元库。包括 NAND、NOR、触发器、mux、clock gate 等基础逻辑单元及其时序、功耗、物理信息。综合和后端依赖它。

## SRAM Compiler

SRAM 编译器。根据容量、位宽、端口和工艺生成 SRAM macro。AI 芯片大量使用 SRAM，SRAM macro 选择会影响面积、功耗、时序和 floorplan。

## IP

Intellectual Property，芯片可复用模块。可以是软核 RTL、硬核版图、PHY、controller、VIP 或软件包。IP 购买不是即插即用，集成和验证成本必须纳入计划。

## PHY

Physical Layer，物理层 IP。常见于 DDR、HBM、PCIe、Ethernet、USB 等高速接口。PHY 强依赖工艺、封装、板级信号完整性和 vendor 支持。

## Foundry

晶圆代工厂。负责制造晶圆，例如 TSMC、Samsung Foundry、GlobalFoundries、SMIC 等。Foundry 关系影响 PDK 获取、节点选择、产能、价格和支持质量。

## Fabless

无晶圆厂芯片公司。自己设计芯片，把制造外包给 foundry，把封装测试外包给 OSAT。多数芯片创业公司属于 fabless。

## IDM

Integrated Device Manufacturer，垂直整合芯片公司。既设计也制造芯片，例如 Intel 的传统模式。IDM 与 fabless 在资源和流程上差异很大。

## EDA

Electronic Design Automation，电子设计自动化工具。覆盖仿真、综合、验证、后端、物理验证、功耗分析和测试生成等环节。商业 EDA 是先进节点芯片开发的基础设施。

## NRE

Non-Recurring Engineering，一次性工程成本。包括工程人力、EDA、IP、mask、后端服务、测试开发、样片、认证等。NRE 不随销量线性变化，但必须通过未来销量摊销。

## ASP

Average Selling Price，平均销售价格。用于估算收入和毛利。芯片商业模型必须同时看 ASP、单颗成本、良率、销量和 NRE 摊销。

## BOM

Bill of Materials，物料清单。系统级产品中所有物料成本。芯片公司若销售加速卡或整机，还要考虑 PCB、电源、散热、连接器、内存等 BOM。

## Bring-up

硅后启动调试。首硅回来后让芯片从上电、时钟、复位、JTAG、boot 到基本功能运行。Bring-up 成功不代表量产 ready，但失败会阻断后续验证。

## Characterization

特性化。测量芯片在不同电压、温度、频率、负载下的性能、功耗和 margin。结果用于 datasheet、binning、客户导入和量产测试。

## Qualification

资格认证/可靠性验证。用代表性样品和规定的 stress test 证明芯片、封装和制造流程适合目标市场。JEDEC JESD47 是集成电路可靠性资格测试的公开标准之一。Qualification 不是功能测试，而是进入量产和客户导入前的质量证据。

## Respin

重新流片。发现硬件 bug 或物理问题后修改设计并再次制造。Respin 会带来额外 mask、晶圆、封装、测试和时间成本。

## Reliability

可靠性。芯片在规定环境、时间和负载下保持功能和性能的能力。常见关注点包括高温寿命、湿热、温度循环、ESD、latch-up、电迁移、封装疲劳和现场失效率。

## HTOL

High Temperature Operating Life，高温工作寿命测试。芯片在高温和偏置条件下长时间运行，用于加速暴露与长期使用相关的失效机制。

## ESD

Electrostatic Discharge，静电放电。芯片 IO、pad、bump、电源和保护结构需要满足 ESD 要求，否则制造、封装、测试、运输或使用中可能损坏。

## Latch-up

闩锁效应。CMOS 结构中寄生器件被触发后形成低阻通路，可能导致大电流和永久损伤。Latch-up 测试是芯片可靠性认证的重要项目之一。

## JEDEC

JEDEC Solid State Technology Association，制定半导体存储器、封装、可靠性和产品变更等标准的行业组织。芯片 qualification、PCN/PDN 和封装相关流程经常引用 JEDEC 标准。

## Volume Ramp

量产爬坡。从工程样品或小批试产逐步扩大到稳定量产出货的过程。核心不是简单增加订单，而是同步爬升良率、测试覆盖、供应链产能、客户认证和质量监控。

## Wafer Sort

晶圆测试，也称 CP test。晶圆切割前用 probe card 和 ATE 测试 die，筛掉明显失效 die，并收集 wafer map 和良率数据。

## Final Test

封装后最终测试。芯片完成封装后在 ATE 上进行功能、性能、功耗、接口和 binning 测试，是量产出货前的关键质量门禁。

## Binning

分档。根据测试结果把芯片分到不同频率、功耗、功能或质量等级。Binning 影响可售规格、库存结构、ASP 和客户体验。

## Wafer Start

晶圆投片。Foundry 开始制造某批晶圆的动作或产能单位。Wafer start 决策直接影响几个月后的可出货数量、库存和现金占用。

## Lead Time

交期/前置时间。从下单、投片、封装、测试到可交付产品所需的时间。芯片供应链 lead time 通常以周到月计，先进封装和稀缺材料可能更长。

## PCN

Product Change Notification，产品变更通知。供应商或芯片公司对工艺、封装、材料、测试、产地、规格或软件支持等变化向客户发出的正式通知。

## Traceability

追溯性。把出货产品追溯到 wafer lot、die location、package lot、test program、bin、date code、客户和软件版本的能力。没有追溯，现场问题会扩大成不可控质量风险。

## RMA

Return Material Authorization，退料授权/客诉退回流程。客户把疑似失效产品退回供应商进行确认、分析、替换或赔付的质量流程。

## Failure Analysis

失效分析。对失效芯片、封装、板卡或系统进行电性、物理和材料分析，以找出根因。常见手段包括 ATE retest、X-ray、SAT、decap、SEM、FIB 和 emission microscopy。

## Errata

已知问题说明。记录芯片或软件中的已知缺陷、影响条件、规避方法和修复计划。Errata 不是失败本身，隐瞒或管理混乱才会变成客户信任问题。

## FAE

Field Application Engineer，现场应用工程师。连接客户和研发团队，负责导入支持、问题复现、应用调优、文档解释和现场 issue triage。

## EOL

End of Life，产品生命周期结束。产品停止新设计导入、停止接单、最后采购、最后发货和支持退出的受控流程。

## Last Time Buy

最后采购。EOL 流程中客户可下最后订单的窗口。芯片 last time buy 需要考虑库存、合同、供应商停产、软件支持和客户系统生命周期。

## Revision

版本/修订。可指 silicon revision、package revision、board revision、firmware revision 或 software release。芯片项目必须明确不同 revision 的兼容性和追溯关系。

## Design Partner

设计合作客户。早期参与产品定义、样片验证和问题反馈的客户。Design partner 通常比普通客户更能接受 engineering sample 的限制，但需要清晰的边界、支持承诺和信息共享机制。

## Engineering Sample

工程样品。用于 bring-up、characterization、客户早期评估和软件开发的非最终量产芯片或板卡。Engineering sample 不应被当作完全 qualified 的量产产品销售。

## Safe Mode

安全模式/保守模式。芯片在异常、bring-up 或调试时进入的低风险配置，例如低频、关闭部分功能、使用保守电压或绕过高风险路径。Safe mode 能显著提高硅后 debug 和现场恢复能力。

## Telemetry

遥测/运行状态采集。芯片或系统持续输出温度、电压、频率、错误计数、性能计数器、功耗和 firmware 状态等信息，用于 bring-up、现场支持和可靠性分析。

## STDF

Standard Test Data Format，ATE 测试数据常见格式。STDF 记录 wafer sort/final test 的测试项、bin、fail 信息和统计数据，是良率分析、量产监控和 RMA 追溯的重要输入。

## EVB

Evaluation Board，评估板。用于首硅 bring-up、软件开发、客户评估和系统验证的板卡。EVB 的电源、时钟、复位、JTAG、接口和散热设计会直接影响硅后调试效率。

## Boot ROM

启动只读存储器。芯片复位后最早执行或参与启动流程的固化代码/逻辑之一，负责基础初始化、启动介质选择、安全检查或加载后续 firmware。Boot ROM bug 往往难以修复，需要谨慎验证。

## Diagnostic Test

诊断测试。用于 bring-up、量产筛选或现场支持的测试程序，目标是快速定位电源、时钟、存储器、接口、NPU、DMA、firmware 或系统集成问题。

## Verification

验证。确认设计是否符合规格，通常发生在 tapeout 前，重点是“设计有没有按 spec 做对”。常见手段包括仿真、UVM、formal、coverage 和 emulation。

## Validation

确认/验证产品是否满足真实使用需求，常发生在硅后和客户场景中，重点是“产品是否解决真实问题”。软件背景的人容易混用 verification 和 validation，芯片项目中两者责任不同。

## Wafer Test

晶圆测试，也叫 wafer sort。芯片还在晶圆上时用 probe card 和 ATE 做初筛。它用于识别坏 die，减少后续封装浪费。

## MMMC

Multi-Mode Multi-Corner，多模式多工艺角时序分析。现代 SoC 会在 functional、scan、低功耗等模式，以及不同工艺、电压、温度 corner 下检查 STA。

## PVT Corner

Process、Voltage、Temperature corner，工艺、电压、温度组合。芯片必须在定义的 PVT 范围内满足时序和可靠性要求。

## WNS/TNS

Worst Negative Slack / Total Negative Slack。WNS 表示最差路径 slack，TNS 表示所有违反路径负 slack 总和。STA closure 不能只看 WNS，还要看 violation 分布和路径类型。

## AOCV/POCV/LVF

Advanced On-Chip Variation、Parametric On-Chip Variation、Liberty Variation Format。用于建模先进节点工艺和片上变异对时序的影响。具体采用哪种模型由 foundry、EDA flow 和 signoff methodology 决定。

## Signal Integrity

信号完整性，后端中常指串扰、噪声、毛刺、delay shift 等风险。高频、长线、并行宽总线和低电压先进节点更容易出现 SI 问题。

## Antenna Effect

天线效应。制造过程中长金属线可能积累电荷并损伤栅氧。后端通常通过 diode、jumper 或改线修复 antenna violation。

## Metal Fill

金属填充。为满足制造密度和 CMP 均匀性要求，在空白区域加入 dummy metal。Metal fill 会改变寄生参数，因此通常需要重新抽取并回归 STA/power。

## ERC

Electrical Rule Check，电气规则检查。常用于检查电源连接、well/tap、floating node、ESD/latch-up 等电气合法性。

## DFM

Design for Manufacturability，可制造性设计。通过符合 foundry 规则、密度、pattern、冗余 via、可制造布局等方式提高制造窗口和良率。

## PERC

Programmable Electrical Rule Checking，可编程电气规则检查。常用于复杂电气拓扑检查，例如 ESD、power domain、level shifter、特殊可靠性规则。

## 后续阅读

- [01_full_lifecycle.md](./01_full_lifecycle.md)
- [02_roles_and_teams.md](./02_roles_and_teams.md)
- [03_cost_structure.md](./03_cost_structure.md)

## 参考公开来源

- [Accellera Standards](https://accellera.org/downloads/standards)
- [Accellera UVM Working Group](https://www.accellera.org/activities/working-groups/uvm)
- [JEDEC JESD47 overview via TI reliability testing reference](https://www.ti.com/quality-reliability/reliability/testing.html)

## 内容可信度说明

- **公开信息（高可信）**：术语定义、标准组织名称、EDA/制造/封测基本概念。
- **行业惯例（中可信）**：术语在项目沟通中的常见用法、各概念之间的工程关联。
- **经验性观察（中低可信）**：对软件背景读者的解释角度、常见误解提示。
- **不确定/需向资深工程师确认（低可信）**：不同公司内部术语缩写、特定 foundry 或 IP vendor 的专有定义。
