# IP 策略：自研、购买与集成

## 前置知识

- 建议先读 [规格定义](./02_spec_definition.md)。
- 建议先读 [架构探索](./03_architecture_exploration.md)。
- 成本背景可参考 [芯片项目成本结构总览](../00_overview/03_cost_structure.md)。

## IP 策略的核心

[IP](../00_overview/05_glossary.md#ip) 策略不是采购清单，而是芯片公司能力边界、风险边界和商业边界的定义。芯片项目里，一个 IP 可以是软核 [RTL](../00_overview/05_glossary.md#rtl)、硬核 layout、PHY、controller、verification IP、firmware、driver、compiler component、analog macro 或封装参考设计。购买 IP 不等于即插即用，自研 IP 也不等于更可控。

对创业公司，IP 策略的关键问题是：哪些模块构成公司差异化，必须掌握；哪些模块是行业基础设施，购买更理性；哪些模块虽然可以买，但集成、验证和商务风险很高，必须提前管理。

## IP 类型

| 类型 | 示例 | 特点 |
|---|---|---|
| 软 IP | CPU core RTL、[NoC](../00_overview/05_glossary.md#noc) RTL、controller RTL | 可综合、可配置，但后端实现由团队负责 |
| 硬 IP | [SerDes](../00_overview/05_glossary.md#serdes) PHY、DDR PHY、HBM PHY、PLL、ADC/DAC | 与工艺强绑定，通常交付 GDS/LEF/lib/model |
| Verification IP | PCIe VIP、AXI VIP、DDR VIP | 用于验证协议行为，不是产品硬件 |
| 软件 IP | firmware、driver、compiler backend、runtime | 决定硬件能否被客户使用 |
| 安全 IP | crypto engine、secure boot、TRNG、PUF | 可能涉及认证和出口管制 |
| 存储 IP | SRAM compiler、eFuse、OTP、ROM | 与 foundry 和工艺相关 |
| 封装/接口 IP | UCIe、die-to-die、HBM PHY | 同时牵涉封装、测试和生态 |

其中 [PHY](../00_overview/05_glossary.md#phy) 类 IP 风险特别高。高速接口不是单纯 RTL 问题，它涉及模拟电路、版图、封装、板级信号完整性、jitter、电源噪声、ESD、测试模式和 vendor 支持。软件背景团队不应低估 PHY 集成。

## 哪些适合买，哪些适合自研

通常适合购买的 IP 包括 PCIe controller/PHY、DDR/HBM controller/PHY、USB/Ethernet SerDes、PLL、PMU、eFuse/OTP、JTAG/debug infrastructure、成熟 CPU core、标准 NoC、security subsystem 和标准 verification IP。

购买理由不是团队写不出来，而是这些 IP 的价值在于多年硅验证、生态兼容、协议认证、foundry 适配和客户信任。自研一个 PCIe controller 也许可行，自研一个先进节点 PCIe PHY 并完成合规和量产支持，对创业公司通常不现实。

AI 芯片创业公司的差异化通常在 [NPU](../00_overview/05_glossary.md#npu) 架构、数据流、编译器映射、kernel library、runtime、性能模型、调度策略和软硬件协同上。这些能力如果完全外包或购买，公司的长期壁垒会很弱。

但自研也要分层。可以自研 tensor engine、scratchpad 管理、command processor、性能计数器和编译器 backend。对于 CPU control plane、标准 interconnect、基础 DMA、标准协议 bridge，可以根据团队能力和进度选择购买、复用开源或自研简化版。

## 授权和商业模式

IP 授权常见模式包括一次性 license fee、按项目授权、按节点授权、按实例授权、royalty、maintenance fee、support fee、source code fee 和 evaluation license。硬 IP 还可能按 [Foundry](../00_overview/05_glossary.md#foundry)、process node、corner、metal stack 或封装条件限制使用。

量级上，公开可讨论的安全表述只能到“范围和计价方式”。评估授权可能是低成本或限时的；成熟软 IP 可能从数万美元到更高量级；复杂 controller、CPU subsystem、NoC、安全 IP、VIP 或高速接口 IP 往往进入数十万到数百万美元量级；HBM、DDR、PCIe/CXL、SerDes PHY 等硬 IP 还会叠加节点、foundry、封装和支持费用。具体报价高度依赖 vendor、节点、区域、客户资质、项目数量、是否含 source access、是否含 royalty 和谈判结果，必须向供应商确认。

还要把集成 [NRE](../00_overview/05_glossary.md#nre) 算进去。IP 授权费之外，团队可能需要投入 wrapper、CDC/RDC、DFT、仿真模型、VIP、low-power integration、后端 hardening、封装/板级约束、firmware 和 bring-up 支持。对高速接口，集成成本和排期风险可能接近甚至超过 license 本身。

需要重点审查以下问题：

| 问题 | 为什么重要 |
|---|---|
| 是否允许目标 foundry 和节点使用 | IP 与工艺强绑定 |
| 是否包含源代码或仅 encrypted RTL | 影响 debug 和修改 |
| 是否包含验证环境和 VIP | 影响集成验证成本 |
| 是否包含 firmware/driver | 影响 bring-up |
| 是否支持目标 EDA flow | 影响综合、仿真、后端 |
| 是否有硅验证记录 | 影响首硅风险 |
| 是否允许开源或公开文档 | 影响开源策略 |
| 是否有出口管制或区域限制 | 影响客户和供应链 |
| bug fix 和 support SLA 如何定义 | 影响项目排期 |
| royalty 如何计算 | 影响毛利模型 |

IP 成本不能只看报价。还要算集成人力、验证时间、EDA license、vendor support、bug 等待、wrapper 开发、CDC/RDC、DFT、低功耗、后端 macro placement、timing exception 和硅后 debug。

## IP 评估流程

第一步是从架构规格生成 IP requirement list。每个 IP 需要写明功能、版本、性能、频率、工艺、接口、功耗、面积、验证需求、交付时间和 owner。

第二步是 vendor shortlist。来源包括 foundry OIP 生态、EDA 厂商、Arm、Synopsys、Cadence、Rambus、Alphawave、SiFive、Andes、Arteris、CEVA、Imagination、eMemory 等。具体选择取决于区域、节点、商务和支持能力。

第三步是技术评估。要求 vendor 提供 datasheet、integration guide、deliverable list、known issues、silicon proof、PPA 数据、EDA 支持矩阵、DFT/test mode、low power 支持、UPF 示例和 verification collateral。

第四步是商务和法务评估。确认授权范围、付款节点、source access、support SLA、开源限制、escrow、termination、indemnification 和出口管制。

第五步是集成试点。不要等主项目启动后才第一次集成。关键 IP 应尽早做 wrapper、仿真、lint、CDC、synthesis smoke test 和 floorplan feasibility check。

## 角色和典型时长

IP 策略需要架构负责人、SoC 集成负责人、RTL lead、验证 lead、DFT/测试负责人、后端/STA 负责人、软件/firmware 负责人、商务、法务和供应链共同参与。对硬 IP 和高速接口，还应让封装、板级 SI/PI 和硅后负责人提前介入。

初版 IP 清单通常应在架构探索早期数周内形成。关键 IP 的技术评估、商务谈判和法务审查常以数周到数月计；HBM、PCIe/CXL、UCIe、先进 SerDes、CPU subsystem 等高风险 IP 应更早启动，因为它们可能决定工艺节点、封装、板级设计和项目排期。

## 与架构、工艺和后端的耦合

IP 策略必须和 [工艺节点选择](./05_process_node_selection.md) 同步。某个 IP 在 7nm 可用，不代表在 5nm、3nm 或另一个 foundry 可用。硬 IP 通常需要特定 [PDK](../00_overview/05_glossary.md#pdk)、metal stack、voltage、ESD 和 package assumptions。

IP 策略也影响 floorplan。HBM PHY、PCIe PHY、DDR PHY、SerDes、PLL、SRAM macro 都有位置、供电、时钟、IO 和 keepout 要求。架构阶段如果不考虑这些硬约束，后端可能无法实现原始规划。

IP 策略还影响验证。标准协议 IP 需要 VIP、compliance test 和 corner case。加速器内部 IP 需要 reference model、assertion、coverage 和系统级场景。购买 IP 可以降低某些风险，但也会引入黑盒风险。

## 开源芯片策略下的特殊问题

如果目标是“RTL + 编译器全栈开源”，需要把 IP 分成三类。

第一类是可开源自研模块，例如 NPU core、编译器 backend、runtime、仿真器和部分 interconnect。这些构成社区可见价值。

第二类是可替换模块，例如 PCIe、DDR、CPU core、SRAM abstraction。开源仓库可以提供接口、stub、仿真模型或 FPGA-friendly 替代实现，商业流片版本使用 vendor IP。

第三类是不可公开模块，例如商业 PHY、foundry SRAM compiler 生成的 macro、PDK 相关文件、某些安全 IP。它们不能进入公开仓库。需要在开源架构中设计清晰边界，避免法律和交付冲突。

否则会出现一个危险状态：对外宣称全栈开源，但真正能流片的版本依赖大量不可公开黑盒，社区无法复现，客户也会质疑开放程度。

## 典型时长和交付物

IP 策略初版应在架构探索早期完成，关键 IP 的商务和技术评估通常需要数周到数月。高风险 IP，如 HBM、PCIe Gen5/Gen6、UCIe、先进 SerDes，应更早启动，因为它们可能决定工艺节点、封装、板级设计和项目排期。

交付物包括 IP 清单、buy/build 决策表、vendor 比较表、授权条款摘要、交付物 checklist、集成计划、验证计划、风险清单、替代方案和开源发布边界说明。

## 常见错误

第一个错误是以为购买 IP 能消除风险。实际上购买 IP 把部分设计风险转移为集成、支持、商务和黑盒 debug 风险。

第二个错误是太晚确认授权。等 RTL 集成后才发现 license 不允许目标节点、客户区域或开源发布，会造成严重返工。

第三个错误是忽略 verification IP。没有 VIP 和协议测试，标准接口也可能在 corner case 下不兼容。

第四个错误是低估硬 IP 的后端影响。PHY、PLL、SRAM macro 的 placement、power、clock 和 timing 约束会影响整个 floorplan。

第五个错误是把开源 IP 当成免费商业 IP。开源 license、维护状态、验证质量、工艺适配和安全漏洞都需要评估。

## 创业公司视角下的取舍

创业公司应把工程资源集中在差异化能力上。对 AI 芯片，最值得投入的是架构、编译器、runtime、性能模型和关键加速单元。对标准接口和模拟/高速物理层，购买成熟 IP 通常更现实。

可以省钱的是先用 FPGA、仿真 stub、开源 soft IP 和低速接口做早期验证。不能省的是关键商业流片 IP 的授权确认、vendor support、交付物完整性和集成验证。一次 IP 决策错误可能导致 [Respin](../00_overview/05_glossary.md#respin) 或产品无法销售。

## 典型场景

团队计划第一颗芯片支持 HBM 和 PCIe Gen5。架构上 HBM 能显著提高 LLM 推理性能，PPT 也更有吸引力。但 IP 评估发现，HBM PHY 依赖特定先进封装和 foundry 生态，封装供应、测试、基板、热设计和采购门槛都很高。PCIe Gen5 PHY 也要求严格的封装和板级 SI 支持。

如果团队忽略这些问题，可能在后端或封装阶段才发现无法落地。更务实的选择可能是第一颗芯片使用更可获得的外部内存方案，保留架构接口，为第二代 HBM 版本做准备。或者做一个小面积 test chip 专门验证 HBM/SerDes 集成，而不是把所有风险压到主芯片。

## 后续阅读

- [05_process_node_selection.md](./05_process_node_selection.md)
- [06_milestones_and_signoffs.md](./06_milestones_and_signoffs.md)
- [开源芯片策略](../06_cross_cutting_topics/03_open_source_silicon.md)
- [Foundry 关系](../06_cross_cutting_topics/02_foundry_relationships.md)
- [Turnkey 服务](../06_cross_cutting_topics/05_turnkey_services.md)

## 参考公开来源

- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [Arm Flexible Access](https://www.arm.com/products/flexible-access)
- [Arm Flexible Access for Startups](https://www.arm.com/products/flexible-access/startup)
- [Synopsys DesignWare IP](https://www.synopsys.com/designware-ip.html)
- [Cadence Design IP](https://www.cadence.com/en_US/home/tools/ip.html)
- [UCIe Consortium Specifications](https://www.uciexpress.org/specifications)

## 内容可信度说明

- **公开信息（高可信）**：IP 类型、公开标准组织、主要商业 IP/EDA/foundry 生态存在；PHY 与工艺和封装强相关。
- **行业惯例（中可信）**：buy/build 决策、vendor 技术评估、license/support 审查、IP 集成试点和交付物 checklist。
- **经验性观察（中低可信）**：创业公司应购买标准高速接口和模拟硬 IP，自研差异化 AI 架构与软件栈；开源芯片需要预先划分不可公开 IP 边界。
- **不确定/需向资深工程师确认（低可信）**：具体 IP 报价、授权条款、vendor 支持质量、特定节点硅验证记录、出口管制和开源发布限制。
