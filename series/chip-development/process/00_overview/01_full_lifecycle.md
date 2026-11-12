# 完整芯片生命周期总览

## 前置知识

- 建议先读 [README.md](./README.md)。
- 遇到术语可查 [05_glossary.md](./05_glossary.md)。

## 一句话总览

芯片开发生命周期是把一个市场假设逐步约束成可制造、可测试、可销售的物理产品。它通常经过产品定义、架构探索、规格冻结、[RTL](./05_glossary.md#rtl) 设计、[Verification](./05_glossary.md#verification)、[Synthesis](./05_glossary.md#synthesis)、[DFT](./05_glossary.md#dft)、后端物理设计、[Signoff](./05_glossary.md#signoff)、[流片](./05_glossary.md#流片-tapeout)、[Wafer](./05_glossary.md#wafer) 制造、[Package](./05_glossary.md#package) 与测试、硅后 [Bring-up](./05_glossary.md#bring-up)、[Characterization](./05_glossary.md#characterization)、可靠性 [Qualification](./05_glossary.md#qualification)、量产爬坡和现场支持。

软件项目可以频繁发布补丁，芯片项目则必须在 tapeout 前尽量把不可逆错误消灭掉。先进节点的一次完整 mask set 可能达到百万到千万美元量级，晶圆制造和封装排期也会把错误修复周期拉长到数月。因此芯片流程的本质不是“慢”，而是“用大量前置验证降低物理世界返工概率”。

## 生命周期阶段速查表

| 阶段 | 主要角色 | 典型时长量级 | 关键交付物 | 错误决策的典型后果 |
|---|---|---:|---|---|
| 产品定义 | 创始人、产品、系统架构、销售/BD、财务 | 数周到数月 | PRD、目标 PPA、目标 ASP/BOM、客户场景 | 做出客户不需要或卖不动的芯片 |
| 架构探索 | 芯片架构、建模、编译器、软件、后端顾问 | 数月，且持续迭代 | Architecture spec、C model、性能/功耗/面积预算 | RTL 团队在错误假设上开工，后期大改 |
| 前端设计验证 | RTL、验证、DFT、低功耗、软件 | 数月到一年以上，取决于规模 | RTL、testbench、coverage、CDC/RDC、UPF、DFT plan | bug 进入硅后，或综合/DFT 无法收敛 |
| 后端物理设计 | PD、STA、IR/EM、physical verification、DFT | 数月量级，先进节点更长 | Netlist、DEF、GDSII/OASIS、STA/DRC/LVS/IR reports | 频率、功耗、面积或物理规则无法 signoff |
| 制造封测 | Foundry、OSAT、test、封装、供应链 | 数月量级 | Wafer、封装样片、ATE program、yield report | 样片延迟、成本失控、测试覆盖不足 |
| 硅后与量产 | 硅后、软件、测试、质量、供应链、FAE | 数月到更久 | Bring-up report、datasheet、qualification、production release | 首硅无法 demo、客户导入失败、量产质量风险 |

## 阶段 1：产品定义与商业假设

核心问题是：这颗芯片为什么值得做。活动包括目标市场选择、客户场景访谈、竞品拆解、workload 分析、性能/功耗/成本目标设定、软件栈边界、供应链约束和商业模型估算。AI 芯片尤其要明确目标 workload，例如 Transformer 推理、推荐系统、视频处理、边缘视觉或训练加速，因为不同 workload 对 SRAM、HBM、NoC、数据类型和编译器的要求完全不同。

参与角色包括创始人、产品负责人、系统架构师、算法/编译器工程师、销售或 BD、财务负责人。交付物通常是 MRD/PRD、目标 [PPA](./05_glossary.md#ppa)、目标 ASP/BOM、竞品矩阵、风险清单和初版项目计划。

典型时长因公司而异。创业公司可能用 4 到 8 周完成第一版判断，但真正可靠的定义往往需要持续迭代。错误决策的后果很直接：如果 workload 判断错，后面即使 RTL 完美，也可能做出客户不需要的芯片。

## 阶段 2：架构探索与规格冻结

架构团队把产品目标转成可实现的系统结构。活动包括性能模型、带宽模型、存储层级设计、片上互连选择、ISA 或指令接口定义、精度支持、host interface、功耗预算、面积估算和 IP 选型。工具可能包括 Python/C++ simulator、SystemC、gem5、内部架构探索框架、性能 trace 分析工具和功耗估算表。

输出物包括 architecture spec、programmer model、memory map、接口协议、性能模型、功耗面积预算、IP list 和 verification plan 初稿。这里的 signoff 不是形式主义，而是防止下游 RTL 团队在模糊需求上开工。

软件背景的人容易把 [C Model](./05_glossary.md#c-model) 当成“黄金实现”。更准确的说法是，C model 是 reference model 和探索工具，但它没有天然表达时钟周期、资源冲突、背压、复位、CDC、综合约束和物理面积。架构冻结时必须把这些硬件约束写入 spec。

主要角色包括芯片架构师、性能建模工程师、编译器/runtime 工程师、RTL lead、验证 lead 和后端顾问。典型时长通常是数月量级，并且会在 RTL 和软件开发中持续校准。关键决策是哪些功能进入本代芯片、哪些交给软件或下一版；错误后果是微架构反复推倒、验证计划失效，或者做出编译器无法有效利用的硬件。

## 阶段 3：前端设计与验证

前端把架构变成 RTL，并证明 RTL 符合规格。活动包括微架构设计、SystemVerilog/Verilog RTL 编写、[Lint](./05_glossary.md#lint)、[CDC](./05_glossary.md#cdc)/[RDC](./05_glossary.md#rdc)、仿真、[UVM](./05_glossary.md#uvm) testbench、[Formal Verification](./05_glossary.md#formal-verification)、覆盖率收敛、功耗意图 UPF、DFT 约束准备和综合试跑。常见工具包括 Synopsys VCS、Cadence Xcelium、Siemens Questa、Verdi、SpyGlass、JasperGold、VC Formal、Design Compiler、Genus，以及 Accellera/IEEE UVM 方法学。

输出物包括 RTL、testbench、coverage report、lint/CDC/formal 报告、约束文件、UPF、DFT plan、前端 signoff checklist。典型时长高度依赖规模。一个小型控制芯片可能数月，大型 AI SoC 的前端和验证可能是项目最长部分之一。

关键决策是验证深度和设计冻结标准。错误地认为“仿真跑过主要 demo 就可以”是重大风险。芯片 bug 的难点不是已知路径，而是异常交互：背压、重试、中断、复位、低功耗切换、跨时钟域、错误注入和极端并发。

主要角色包括 RTL designer、verification engineer、formal engineer、DFT engineer、low-power engineer、firmware/driver engineer。交付物必须能被后端和硅后消费：RTL 代码、约束、寄存器文档、coverage、waiver、debug feature 和 test mode 定义。错误后果包括综合失败、CDC bug、DFT 插入困难、硅后不可观测。

## 阶段 4：综合、DFT 与后端物理设计

综合把 RTL 转成门级网表，DFT 加入 scan、MBIST、JTAG 等可测试结构，后端把门级网表变成版图。活动包括 floorplan、power grid、placement、[CTS](./05_glossary.md#cts)、routing、STA、[IR Drop](./05_glossary.md#ir-drop)、[EM](./05_glossary.md#em)、SI、[DRC](./05_glossary.md#drc)、[LVS](./05_glossary.md#lvs) 和 [ECO](./05_glossary.md#eco)。常见工具包括 Synopsys Design Compiler/Fusion Compiler/PrimeTime/IC Validator、Cadence Genus/Innovus/Tempus/Voltus、Siemens Calibre 等。

输出物包括 gate-level netlist、SDC、DEF、GDSII/OASIS、signoff reports、test patterns、ECO 记录和 tapeout package。先进节点下，后端不是“把网表自动布线一下”。pin access、routing congestion、多模式多角 STA、OCV、IR drop、EM、thermal、EUV/multi-patterning 规则都会影响能否收敛。

创业公司常见取舍是后端外包或 co-design。可以外包执行，但不能外包责任。内部必须有人能审 floorplan、timing exception、IR drop waiver、DRC waiver 和 tapeout checklist。

主要角色包括 synthesis engineer、DFT engineer、physical design engineer、STA engineer、power integrity engineer、physical verification engineer 和后端项目负责人。典型时长通常是数月量级，先进节点或大 SoC 会更长。关键决策是频率目标、floorplan、macro 摆放、电源网络、timing exception 和 waiver 是否可接受；错误后果是 tapeout 延期、PPA 大幅偏离，或把物理风险带到硅上。

## 阶段 5：流片、晶圆制造、封装与测试

Tapeout 后，foundry 根据 GDSII/OASIS 制作 mask 并制造晶圆。先进节点晶圆可能需要数百道工艺步骤，周期常以数月计。晶圆完成后进入 wafer sort，再切割、封装、final test。封装可能是传统 BGA，也可能是 2.5D/CoWoS/扇出等高级封装。AI 芯片如果使用 [HBM](./05_glossary.md#hbm)，封装和基板可能成为成本与供应链瓶颈。

输出物包括 wafer、known good die、封装样片、ATE 测试程序、良率报告和失效分析样本。这个阶段的关键不是“等待制造”，而是提前准备测试板、bring-up 软件、ATE pattern、实验室设备和 debug plan。

主要角色包括 foundry interface、OSAT interface、封装工程师、test engineer、supply chain/operations、硅后负责人。典型时长受 foundry、节点、封装和排期影响，通常以数月计。关键决策是使用 MPW 还是 full mask、选择什么封装、测试覆盖率和测试时间如何平衡；错误后果是样片延迟、封装/板级问题阻塞 bring-up，或量产测试成本过高。

## 阶段 6：硅后 bring-up、特性化与量产

首硅回来后，硅后团队验证电源、时钟、复位、JTAG、boot flow、存储接口、PCIe/CXL/Ethernet 等高速接口、NPU 功能、性能、功耗和温度。若发现问题，需要判断是板级问题、封装问题、测试程序问题、软件问题、配置问题、RTL bug、物理实现问题还是工艺问题。

特性化会测 PVT corner、频率电压曲线、功耗模型、热行为、margin 和长期可靠性。量产前还要完成 qualification，例如 JEDEC JESD47 相关可靠性测试。量产爬坡关注良率、测试时间、binning、供应链、客户认证和现场反馈。

主要角色包括 post-silicon lead、firmware/driver、validation、test、quality/reliability、FAE、supply chain。典型时长从数月到更久，取决于 bug 数量、客户认证、可靠性要求和供应链准备。关键决策是哪些 bug 可以软件 workaround，哪些必须 respin；错误后果是客户 demo 失败、datasheet 不能承诺、量产良率或现场质量失控。

## 阶段之间的回环

真实项目不是线性瀑布。架构性能模型与编译器不一致时，会回到架构定义；RTL 综合频率达不到时，会回到微架构 pipeline；后端 routing congestion 严重时，可能回到 floorplan 或模块接口；硅后发现 corner case 时，可能回到 firmware workaround、metal ECO 或 full respin。

因此每个阶段都要产出可被下游验证的证据，而不是只交一个文件。Spec 要能导出验证计划，RTL 要能综合和插 DFT，后端约束要能被 STA 审计，硅后 debug 需要前端预留观测点。

## 典型流程场景

一家核心团队约 20 人的创业公司准备做先进节点 AI 推理芯片，但它没有试图第一版完成完整旗舰 SoC，而是用内部核心团队、外部后端顾问和设计服务伙伴做一个范围收缩的评估芯片。团队先完成 workload 和架构模型，发现外部带宽是瓶颈，于是把算力目标下调，把 SRAM 和压缩策略上调。随后进入 RTL 和验证，并让后端服务公司提前参与 floorplan 评估。第一次综合后发现 NoC 拥塞和 SRAM macro 摆放导致频率目标过激，团队降低频率并调整 pipeline。

Tapeout 后数月拿到首硅，bring-up 发现 DMA 一个 corner case 会 hang，但软件 driver 可以规避；另一个 PCIe equalization 问题需要 board 和 firmware 调参。公司决定不 respin，先做客户评估版，同时把硬件修复放进下一版。

这个场景说明：快速迭代不是跳过流程，而是把每次迭代目标缩小，把可观测性、可配置性和软件 workaround 设计进去。

## 上下游接口

产品定义输出目标和边界，架构阶段把目标转成 spec，前端阶段把 spec 转成 RTL 和验证证据，后端把 RTL 转成可制造版图，制造封测把版图转成物理样片，硅后把样片转成可发布产品。任何阶段输出模糊，都会把不确定性传递给下游，并在更昂贵的位置爆炸。

## 后续阅读

- [02_roles_and_teams.md](./02_roles_and_teams.md)
- [03_cost_structure.md](./03_cost_structure.md)
- [../02_frontend_design_and_verification/README.md](../02_frontend_design_and_verification/README.md)
- [../03_backend_physical_design/README.md](../03_backend_physical_design/README.md)

## 参考公开来源

- [Accellera UVM Working Group](https://www.accellera.org/activities/working-groups/uvm)
- [Cadence Innovus Implementation System](https://www.cadence.com/content/cadence-www/global/en_US/home/tools/digital-design-and-signoff/hierarchical-design-and-floorplanning/innovus-implementation-system.html)
- [Synopsys Design Compiler](https://www.synopsys.com/Tools/Implementation/RTLSynthesis/DesignCompiler/Pages/default.aspx)
- [Siemens Calibre Physical Verification](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/)

## 内容可信度说明

- **公开信息（高可信）**：ASIC 生命周期、UVM 标准、常见 EDA 工具类别、tapeout 到制造封测的基本流程。
- **行业惯例（中可信）**：各阶段典型活动、signoff checklist、创业公司采用外包后端的模式。
- **经验性观察（中低可信）**：快速迭代芯片公司的流程压缩策略、首硅 bug triage 策略。
- **不确定/需向资深工程师确认（低可信）**：具体项目阶段时长、foundry 排期、先进封装交期和不同客户认证要求。
