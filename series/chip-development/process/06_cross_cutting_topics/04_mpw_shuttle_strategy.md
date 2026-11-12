# MPW Shuttle Strategy：MPW 多项目晶圆策略

## 前置知识

- 建议先读 [Tapeout 流程](../04_tapeout_and_post_silicon/01_tapeout_process.md)。
- 建议先读 [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)。
- 建议理解 [MPW](../00_overview/05_glossary.md#mpw-multi-project-wafer)、[Mask Cost](../00_overview/05_glossary.md#mask-cost)、[Wafer](../00_overview/05_glossary.md#wafer)、[Package](../00_overview/05_glossary.md#package)、[Test Chip](../00_overview/05_glossary.md#test-chip)。

## 核心概念

MPW 是多个设计共享一套 mask 和晶圆制造成本的方式，适合 test chip、IP 验证、工艺学习、教学和低成本原型。它的价值在于降低第一次拿到硅反馈的成本，不在于直接形成量产产品。

对于快速迭代芯片公司，MPW 可以成为架构和物理实现之间的低成本反馈环。但要明确边界：MPW 面积、封装、IO、样品数量、排期、工艺节点、IP 可用性和测试条件受限制；它不能替代完整量产 flow。

## 适合 MPW 的内容

适合放进 MPW 的包括 SRAM/compiler wrapper 验证、小型 NPU tile、NoC slice、clock/reset/power island、DFT/scan/MBIST flow、标准单元/宏集成、AI 数据路径关键单元、片上监控电路、bring-up infrastructure 和 EDA flow validation。SerDes/PHY test structure 也可以做 MPW，但它不是简单数字 test chip：需要 PHY IP 授权、封装/板级 SI、测试设备、foundry 支持和专业模拟/高速接口经验，成本和难度会明显上升。

不适合 MPW 的包括需要完整客户软件栈验证的大型 SoC、依赖复杂封装/HBM 的系统、需要大量样品做客户 qualification 的产品、对 IO/封装/散热有量产级要求的芯片。MPW 可以验证局部风险，不能证明完整产品 ready。

## 关键活动顺序

第一步是定义 MPW 学习目标。不要为了“有流片经验”而流片。目标应具体到要验证哪个假设：某 SRAM macro 是否可靠、某数据路径能否达到频率、某 DFT flow 是否可用、某 agent 生成 RTL 是否能走到 GDS。

第二步是选择 shuttle。要看工艺节点、PDK 可用性、面积上限、IO 数量、封装选项、提交日期、样品数量、EDA 要求、测试支持和成本。成熟节点 MPW 成本低，先进节点 shuttle 成本和门槛高。

第三步是设计 test vehicle。MPW 芯片应包含可观测性和可控性：JTAG、scan、MBIST、状态寄存器、pattern generator、signature checker、clock controls、voltage monitors 和测试 pad。没有测试结构，硅片回来也无法回答学习目标。

第四步是 tapeout 和 bring-up。MPW 也需要 DRC/LVS、STA、DFT、封装和测试计划。小芯片不代表可以跳过工程纪律。

第五步是提取可复用结论。把硅后数据回写到 RTL generator、EDA flow、IP integration guideline、验证计划和下一版架构。MPW 的成功标准是获得决策信息，而不是“芯片能亮灯”。

## 工具、角色和成本

工具与常规芯片类似，但可以更轻量：Verilator/Yosys/OpenROAD/OpenLane/KLayout/Magic/Netgen 适合部分开放 PDK 或成熟节点项目；商业 flow 则仍可能使用 Genus/Design Compiler、Innovus/Fusion Compiler、PrimeTime/Tempus、Calibre/IC Validator/Pegasus。测试侧需要 probe/board、示波器、逻辑分析仪、JTAG、ATE 或简化 tester。

角色包括架构/RTL、verification、physical design、DFT/test、board/firmware、project owner 和供应商接口。周期通常是数月量级，因为 shuttle 有固定窗口，制造和封装仍有物理周期。错过提交窗口可能意味着延后数月，而不是下周重跑。

成本要分层看：开放/教育 shuttle 可能非常低成本或由项目资助；商业成熟节点 MPW 常见为数万美元到数十万美元量级，取决于面积、封装、样品和服务；先进节点 shuttle 或包含复杂 IP/封装的 test chip 可能更高。不要把开放 shuttle 的成本经验外推到 7nm 以下或先进封装。

## 关键决策点

第一个决策是 MPW vs FPGA。FPGA 更适合软件 bring-up、功能验证和快速迭代；MPW 更适合验证物理实现、真实 SRAM/clock/power/analog/IO/DFT 风险。两者互补，不应互相替代。

第二个决策是 MPW vs full mask。若目标是量产产品并且需要大量样品、真实封装和客户 qualification，full mask 或 dedicated wafer 更合适。若目标是学习特定物理风险，MPW 更合适。

第三个决策是测试结构投入。为节省面积删掉 debug/test hooks 是 MPW 最大浪费，因为它会让硅片无法解释。

第四个决策是节点选择。用 130nm/65nm/28nm MPW 可以训练流程和验证某些架构，但不能证明 7nm PPA、时序、IR drop、先进封装和 signoff 风险。

如果 MPW 目标定义错误，后果通常是“花了钱但没有决策信息”。比如没有片上 pattern generator 和 signature checker，硅片回来只能看上电；没有功耗/频率测量结构，就无法验证 PPA 假设；没有足够 IO 或测试模式，就无法隔离模块问题。

## 上下游接口

MPW 上游来自架构假设、IP 风险、EDA flow、验证计划和预算。下游输出是 silicon data、bring-up 经验、flow 修正、下一版 design rule、IP 集成结论和是否进入 full chip 的决策。

## 典型场景

一个 AI 芯片团队想验证自动生成的 systolic tile 是否能从 C model 到 RTL 到 GDS，再到硅上运行。务实 MPW 不是放完整 AI SoC，而是放一个 tile、局部 SRAM、DMA-like test interface、JTAG、pattern generator 和 result checker。硅后测量频率、功耗、错误率和测试可观测性，再决定 full chip 是否采用同样生成框架。

如果团队把完整软件栈、HBM、PCIe 和大 NoC 都塞进 MPW，很可能受面积、封装和样品限制，既无法量产，也无法获得清晰结论。

## 创业公司取舍

MPW 适合训练团队、验证 flow、降低首次硅反馈成本，也适合向投资人展示严肃硬件能力。但 MPW 不能作为商业交付承诺。对快速迭代公司，建议把 MPW 用作“风险烧除工具”：每次 MPW 回答 2-3 个关键问题，而不是试图做缩小版产品。

## 常见坑

- 没有明确学习目标，只是为了流片而流片。
- debug/test hooks 不足，硅片回来无法定位问题。
- 把 MPW 成功当成 full-chip 量产能力证明。
- 低估 shuttle 排期，错过窗口导致项目延迟数月。
- 没有把 MPW 结果回写到架构、验证和 flow。

## 后续阅读

- [Tapeout 流程](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [硅后 Bring-up](../04_tapeout_and_post_silicon/04_post_silicon_bringup.md)
- [开源芯片策略](./03_open_source_silicon.md)
- [第一颗芯片的务实建议](../07_for_software_background_founders/04_first_chip_pragmatics.md)

## 参考公开来源

- [Efabless chipIgnite](https://efabless.com/chipignite)
- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)
- [SkyWater Open Source PDK GitHub](https://github.com/google/skywater-pdk)

## 内容可信度说明

- **公开信息（高可信）**：MPW/shuttle、开放 PDK、OpenROAD/OpenLane、test chip 的基本概念。
- **行业惯例（中可信）**：MPW 适合风险验证而非量产、test vehicle 需要可观测性、shuttle 排期影响项目节奏。
- **经验性观察（中低可信）**：快速迭代芯片公司应把 MPW 用作风险烧除工具，而不是缩小版产品发布。
- **不确定/需向资深工程师确认（低可信）**：具体 shuttle 价格、节点、面积、样品数量、封装选项和提交窗口。
