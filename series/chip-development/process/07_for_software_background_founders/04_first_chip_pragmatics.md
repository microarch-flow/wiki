# First Chip Pragmatics：第一颗芯片的务实建议

## 前置知识

- 建议先读 [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)。
- 建议先读 [MPW 策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)。
- 建议先读 [招聘优先级](./03_recruitment_priorities.md)。
- 建议理解 [PPA](../00_overview/05_glossary.md#ppa)、[MPW](../00_overview/05_glossary.md#mpw-multi-project-wafer)、[IP](../00_overview/05_glossary.md#ip)、[DFT](../00_overview/05_glossary.md#dft)、[Bring-up](../00_overview/05_glossary.md#bring-up)。

## 第一颗芯片的正确问题

第一颗芯片不应该问“我们能不能做出最强 AI 芯片”，而应该问“我们需要用最小可承受风险验证哪些公司级假设”。这些假设可能包括：目标 workload 是否有客户价值，架构是否比通用方案有优势，RTL 自动生成 flow 是否可靠，编译器能否稳定映射，团队能否完成 tapeout 和硅后，客户是否愿意导入。

V1 的目标应是最大化学习质量和客户可信度，而不是最大化规格表。你要避免把 V1 设计成 V3 的野心版本。

## Scope 控制

第一颗芯片应限制功能范围。选择少数关键 workload，明确不支持的模型/算子/接口/场景。对 AI 芯片，建议定义 end-to-end 指标：目标模型、batch/latency、功耗范围、软件 API、开发板形态、客户试点场景。

避免在 V1 同时引入太多新风险：新架构、新生成器、新验证方法、新节点、新 PHY、新封装、新软件栈、新客户场景。每增加一个“第一次”，都会降低问题可归因性。

## 节点选择

先进节点能带来性能和能效，但成本、EDA、IP、后端、mask、良率和封装风险都高。成熟节点或较保守节点可能不能达到终局性能，但更适合验证架构和软件闭环。第一颗芯片是否用 7nm 以下，应由客户价值、融资能力、团队经验和必须达到的 PPA 决定。

务实选择可能是分两步：先用成熟节点 MPW/test chip 验证自动生成 flow、NPU tile、SRAM/NoC/DFT/bring-up；再用更接近商业目标的节点做完整 SoC。这样会增加一个中间步骤，但能降低一次性失败概率。

## IP 策略

第一颗芯片应尽量购买成熟且必要的非差异化 IP：CPU subsystem、基础 debug、安全、PLL、IO、DDR/PCIe/Ethernet 等接口 IP、NoC 或部分基础设施。自研重点应放在真正差异化的 AI 架构、数据流、编译器和 runtime。

不要因为开源理想而自研所有 IP。开源 RTL 可以降低某些成本，但 PHY、SRAM、PLL、ESD、high-speed IO、test collateral 和 silicon-proven IP 的价值在于降低风险。买 IP 也不是即插即用，需要 integration、verification、license、support 和后端 collateral。

HBM、PCIe Gen5/Gen6、CXL、先进 SerDes 和先进封装相关 IP 不能简单归入“买成熟 IP 就好”。它们只有在 workload、客户系统和产品定位强制需要时才应进入 V1，因为它们会显著增加封装、板级 SI/PI、验证、供应链和 bring-up 风险。若 V1 的核心假设可以用 DDR、较低速接口或更简单封装验证，优先选择低风险路径。

## 验证策略

V1 最重要的投资之一是验证。至少要有 block-level test plan、SoC-level integration plan、C/golden model 对照、assertion、coverage、CDC/RDC、lint、synthesis smoke test、DFT plan 和 software-driven tests。对于 agent 生成 RTL，每次生成都必须进入自动检查，不允许人工直觉判断“应该没问题”。

验证目标不是证明所有东西完美，而是把不可接受风险提前暴露。若验证资源不足，应缩小功能，而不是保持 scope 并降低验证标准。

## 硅后和软件准备

首硅回来前必须准备 EVB、power sequence、clock/reset plan、JTAG、boot ROM/firmware、driver、diagnostic tests、memory tests、NPU smoke tests、trace/error registers、bring-up checklist 和 issue tracker。硅片到货后才开始写这些，是典型浪费。

AI 芯片还要准备 compiler/runtime 的最小闭环：能把目标模型子集映射到硬件，能采集性能和错误，能复现客户场景。没有软件闭环，硅后只能证明硬件局部功能，不证明产品可用。

## 客户策略

第一批客户应是 design partner，不是普通买家。他们应理解样片边界，愿意提供 workload、参与 debug、接受限制和共同定义 V2。不要把 V1 当成完全成熟产品卖给支持要求极高、信息不透明、合同惩罚重的客户。

客户承诺要分级：simulation/FPGA demo、engineering sample、alpha board、beta board、production release。每一级能承诺的性能、稳定性、供货和支持不同。

## 成本模型

第一颗芯片预算要包含工程人力、EDA、IP、MPW/full mask、wafer、封装、测试、板卡、实验室设备、可靠性、FA、软件团队、外包和至少一次应急 reserve。不要只算 mask 和 wafer。

量级上，成熟节点 MPW/test chip 可以在较低预算内获得学习；先进节点 full SoC 会迅速进入数百万到千万美元级 NRE 区间，具体取决于节点、IP、EDA、封装和外包。创业公司应把 V1 预算设计成“失败后仍有 V2 能力”，而不是孤注一掷。

更实用的预算拆分如下：EDA license 和计算资源可能是数十万到数百万美元量级；商业 IP 从单个较小 IP 的数万/数十万美元到复杂 PHY/子系统的更高量级不等；MPW/test chip 可能是数万美元到数十万美元量级，先进节点或复杂封装更高；full mask、wafer、封装和测试在先进节点会成为百万到千万美元级核心支出；EVB、load board、probe card、socket、实验室仪器、可靠性和 FA 常被低估，可能从数万美元到数十万美元甚至更高；顾问和 turnkey 服务也可能达到数十万到数百万美元。所有数字都只能作为粗量级，实际要以供应商报价为准。

应急 reserve 不应低于“能处理一次重大延期或硅后问题”的水平。若预算只够一次 tapeout 且没有 debug、FA、retest、软件补救和小改版空间，V1 风险过高。

## 决策门禁

建议建立以下 gate：PRD/Workload gate、Architecture gate、Microarchitecture gate、Verification plan gate、RTL freeze gate、DFT gate、Backend trial gate、Tapeout readiness gate、Bring-up readiness gate、Customer sample gate、Production release gate。

每个 gate 必须有证据和 owner。比如 RTL freeze 不只是“不再改 RTL”，而是 lint/CDC 基本清洁、关键功能 coverage 达标、known issues 可接受、DFT/后端输入稳定、软件接口冻结。Tapeout readiness 不只是 GDS 出来，而是 signoff、waiver、test、bring-up 和 respin plan 都准备好。

一个可执行 gate 包应包含：输入 artifact、owner、退出标准、可接受 waiver、下游消费者和失败处理。PRD/Workload gate 的输入是客户场景、模型 trace、性能/功耗/成本目标，owner 是 product/architecture，消费者是架构和软件；Architecture gate 的输入是模型结果、IP/节点/封装假设，消费者是 microarchitecture、verification、backend；Verification plan gate 的输入是 spec 和风险列表，退出标准是 test/coverage/assertion/formal/emulation plan 有 owner；Backend trial gate 的输入是早期 RTL/netlist、SDC、macro/IP collateral，退出标准是频率、拥塞、IR/power 无明显红线；Tapeout readiness gate 的输入是 signoff reports、waiver、DFT/test、bring-up plan、ECO/respin budget，签字人应覆盖 architecture、verification、DFT、backend、software、product、operations。

如果某个 gate 失败，默认动作应是缩小 scope、修复证据或推迟，而不是用会议压力“批准通过”。Waiver 可以存在，但必须写清楚风险、影响范围、owner 和硅后验证计划。

## 典型 V1 策略

一个现实 V1 可以是：选定一个推理 workload 子集；使用成熟 CPU/IO/DDR/PCIe IP；自研 NPU tile 和编译器；采用可管理封装；保留充分 debug/DFT；先用 MPW 或小 test chip 验证生成 flow 和 tile；完整 SoC 面向 design partner 送样，不承诺大规模量产收入。

如果融资和客户窗口要求直接做先进节点，也应把风险限制在最少变量：购买 silicon-proven IP，使用成熟后端/turnkey 团队，减少自研 PHY/封装复杂度，提前准备软件和 bring-up。

## 常见坑

- 为了融资叙事选择过先进节点，但团队和资金不匹配。
- 自研太多非差异化 IP。
- 省掉 DFT/debug，硅后不可调。
- V1 客户承诺过重，样片问题变成商业违约。
- 没有 reserve，任何延期都变成公司级危机。
- 把 MPW/test chip 结果过度外推到 full SoC。

## 后续阅读

- [快速迭代真实约束](./05_fast_iteration_realities.md)
- [AI 芯片特有考虑](../06_cross_cutting_topics/06_ai_chip_specific.md)
- [Volume Ramp](../05_production_and_lifecycle/02_volume_ramp.md)

## 参考公开来源

- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [Efabless chipIgnite](https://efabless.com/chipignite)
- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)

## 内容可信度说明

- **公开信息（高可信）**：MPW、IP、EDA、tapeout、bring-up、volume ramp 的基本流程和成本类别。
- **行业惯例（中可信）**：V1 scope 控制、gate review、buy vs build、design partner 和 bring-up readiness。
- **经验性观察（中低可信）**：第一颗芯片应最大化学习质量而非规格表，避免一次引入过多新风险。
- **不确定/需向资深工程师确认（低可信）**：具体节点选择、IP 报价、客户试点条款、融资约束和 V1 是否需要量产。
