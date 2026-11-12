# 各角色和团队职责

## 前置知识

- 建议先读 [01_full_lifecycle.md](./01_full_lifecycle.md)。
- 术语参考 [05_glossary.md](./05_glossary.md)。

## 为什么角色划分重要

芯片项目失败常常不是因为没人聪明，而是因为接口没人负责。软件团队可以靠强工程师跨层救火，但芯片项目里，架构、RTL、验证、DFT、后端、封装、测试、硅后、软件、供应链之间存在真实交付边界。边界不清会导致典型事故：架构 spec 没冻结，RTL 边写边猜；RTL 没考虑 DFT，后期 scan 插不进去；后端拿到不现实的频率目标，反复 ECO；硅后才发现 debug 寄存器不够，无法定位问题。

对创始人来说，理解角色的目标不是画组织架构图，而是知道每个关键风险应该由谁 owner。一个岗位可以多人合并，一个人可以承担多个角色，但不能出现“没人真正负责”的接口空洞。

## 产品与系统团队

产品负责人定义客户、场景、价格、功耗、形态和交付节奏。系统架构师把需求转成可验证的系统指标，例如 TOPS、tokens/s、batch size、latency、memory bandwidth、TDP、PCIe/CXL 带宽和软件兼容性。

对 AI 芯片公司来说，系统团队必须同时理解 workload、编译器、runtime、内存系统和硬件约束。只懂模型算法但不懂数据搬运，会低估 SRAM、DMA、NoC 和外部带宽的重要性。只懂硬件但不懂软件栈，会做出理论性能很高但编译器难以利用的架构。

交付物包括 PRD、architecture spec、performance model、power/area budget、software programming model 和版本路线图。产品团队还要定义哪些功能是 tapeout 必须项，哪些可以由软件 workaround、后续版本或外部系统承担。

## 架构与建模团队

架构团队负责探索设计空间。典型成员包括首席架构师、性能建模工程师、AI workload 工程师、内存系统架构师、NoC/互连架构师、安全/虚拟化架构师。工具可能是 Python/C++/SystemC 模拟器、trace analyzer、roofline model、内部 DSE 框架。

他们的关键责任不是写一个漂亮 C model，而是回答“为什么这个架构在目标约束下最合理”。输出必须能让 RTL、验证、编译器和后端使用，包括寄存器定义、接口协议、异常行为、性能约束和可配置项。

架构团队也是快速迭代公司最能发挥自动化价值的地方。Agent 可以帮助生成模型变体、跑设计空间搜索、整理实验报告和发现 spec 不一致。但最终架构取舍仍然需要人判断，因为模型假设、客户需求、软件成熟度和制造成本很难完全自动化。

## RTL 设计团队

RTL 工程师把微架构实现成可综合逻辑。职责包括模块划分、时序 pipeline、状态机、仲裁、缓存/队列、寄存器文件、接口协议、低功耗逻辑、reset 策略和可观测性设计。常见语言是 SystemVerilog/Verilog。

软件背景创始人要理解：RTL 工程师不是“硬件版程序员”。他们写的每一行代码最终会映射成触发器、组合逻辑、RAM、mux、clock gate 和连线。一个看似自然的循环、数组或 if-else，在综合后可能变成巨大面积或关键路径。优秀 RTL 工程师会持续思考时钟周期、面积、功耗、物理布局和验证可控性。

如果团队使用 AI agent 基于 C model 生成 RTL，RTL lead 的责任不会消失，反而更重。需要定义编码规范、review checklist、lint/CDC 门禁、等价性检查、综合试跑、可测性约束和 debug 约定。否则生成代码可能功能上接近，但工程上不可维护、不可收敛、不可测试。

## 验证团队

验证团队负责证明设计符合规格，且在足够多的异常场景下不出错。角色包括验证架构师、UVM testbench 工程师、formal 工程师、覆盖率负责人、仿真基础设施工程师、emulation/prototyping 工程师。UVM 是 Accellera/IEEE 体系中的通用验证方法学，用于构建可复用 testbench 和 verification IP。

验证团队的输出不是“跑了很多 test”，而是可审计的证据：test plan、coverage closure、assertion、scoreboard、reference model 对比、bug 趋势、风险 waiver。创业团队最容易低估验证，因为验证不直接产生“功能”。但前端验证不足会把 bug 推到硅后，代价最高。

验证团队还要管理仿真成本。大型 AI SoC 的回归可能消耗大量 license 和云计算资源。好的验证基础设施会区分 smoke test、block-level regression、SoC regression、emulation workload 和 tapeout signoff regression，而不是把所有测试混在一起。

## DFT 与测试团队

[DFT](./05_glossary.md#dft) 团队负责让芯片在制造后可测试。活动包括 scan chain、MBIST、LBIST、JTAG、boundary scan、test compression、ATPG pattern、fault coverage 和测试模式约束。测试工程师负责 wafer sort、final test、ATE 程序、binning、测试时间优化和量产测试数据分析。

DFT 必须早进入项目。如果等 RTL 完成后才补测试结构，可能会破坏时序、面积和低功耗设计。AI 芯片中大量 SRAM、NoC 和高速接口也会让测试策略更复杂。

创业公司容易认为 DFT 是量产才需要的工作。这个判断通常危险。即使第一颗芯片只做样片，如果没有 scan、MBIST、JTAG 和足够的可观测性，硅后 debug 会很慢，无法区分设计 bug、制造缺陷、板级问题和封装问题。

## 后端物理设计团队

后端团队负责把门级网表变成符合工艺规则、时序、电源完整性和可制造性的版图。角色包括 floorplan 工程师、placement/routing 工程师、STA 工程师、power integrity 工程师、physical verification 工程师、ECO 工程师。

他们依赖前端提供干净 RTL、约束、macro list、clock/reset 结构和功耗意图。若架构阶段没有考虑 floorplan，例如大 SRAM macro 分布不合理，后端可能无法达到频率或功耗目标。

后端团队和前端团队的接口很关键。后端不是项目末尾的“自动处理步骤”，而是应该从架构和微架构阶段就参与面积、功耗、macro 摆放、clock plan 和 timing budget 讨论。

## 模拟、混合信号与高速接口团队

即使是 AI 数字芯片，也通常需要 PLL、SerDes、PCIe/CXL/Ethernet PHY、DDR/HBM PHY、电源管理、温度传感器、eFuse、ADC 等模拟或混合信号 IP。很多创业公司会购买这些 IP，但仍需要内部有人能做集成、约束、bring-up 和供应商管理。

高速接口 IP 的风险不仅是授权费，还包括验证环境、封装约束、SI/PI、board 设计、固件调参和兼容性测试。IP vendor 交付了文档和模型，不代表你的 SoC 集成已经安全。

## 软件团队

软件团队包括编译器、runtime、driver、firmware、SDK、性能库、工具链和客户支持。对 AI 芯片来说，软件不是 tapeout 后再做的“配套”。架构能否被编译器利用，决定实际性能。软件团队需要在架构阶段参与 ISA、memory model、调度粒度、profiling、debug 和 fallback 策略。

第一颗芯片如果软件不可用，客户不会因为硬件指标漂亮而采用。软件团队也经常承担硅后 bring-up 的关键工作，例如 boot loader、firmware、driver、diagnostic tests。

对开源芯片策略而言，软件团队还承担社区接口。开源 RTL 只能降低一部分信任成本，真正让开发者采用的是可运行工具链、清晰文档、稳定 SDK、可复现实验和可调试的开发板。

## 项目管理、质量与供应链

芯片项目需要强项目管理，因为很多任务有硬依赖。项目经理或 program manager 要维护 milestone、risk register、issue tracking、signoff checklist、foundry schedule、IP delivery 和 tapeout readiness。

供应链/运营角色负责 foundry、OSAT、封装基板、ATE、实验室、样片物流、出口管制和客户交付。创业早期可以兼职，但不能无人负责。

质量负责人不一定在早期是专职岗位，但质量责任必须存在。它包括文档版本、release 管理、signoff 证据、waiver 审批、bug triage、客户问题闭环和供应商交付验收。

## 创业早期招聘优先级

对快速迭代 AI 芯片创业公司，早期核心不是把所有岗位招满，而是保证关键判断不外包。建议优先拥有：

- 一个能把 workload、软件和硬件连起来的系统/芯片架构负责人。
- 一个真正做过 ASIC tapeout 的 RTL lead。
- 一个强验证 lead，最好经历过 coverage closure 和硅后 bug。
- 一个懂后端约束的 physical design advisor 或 part-time expert。
- 一个能落地编译器/runtime 的软件负责人。
- 一个懂 foundry/IP/EDA 商务的运营或顾问。

可以较早外包的是部分后端执行、部分 IP 集成、封装设计、ATE 测试程序和部分验证组件。不能完全外包的是架构决策、规格控制、关键 RTL ownership、验证策略、signoff 判断和硅后问题归因。

这里是总览层判断，详细招聘顺序、候选人画像和阶段性取舍会放到 [../07_for_software_background_founders/03_recruitment_priorities.md](../07_for_software_background_founders/03_recruitment_priorities.md)。

## 典型协作场景

架构团队决定 NPU 支持新的稀疏格式。RTL 团队认为控制逻辑复杂，验证团队指出 corner case 暴增，编译器团队说模型覆盖率不足，后端顾问提醒新增 metadata SRAM 会影响 floorplan。正确流程是开 design review，量化性能收益、面积功耗代价、验证成本和软件可用性，再决定是否进入本代芯片。

错误流程是架构师直接改 spec，RTL 赶工实现，最后验证收不住，tapeout 前被迫砍功能或带风险出片。这个例子说明角色分工不是为了制造流程，而是为了让不同风险在正确时间暴露。

## 后续阅读

- [03_cost_structure.md](./03_cost_structure.md)
- [04_startup_vs_bigcompany.md](./04_startup_vs_bigcompany.md)
- [../07_for_software_background_founders/03_recruitment_priorities.md](../07_for_software_background_founders/03_recruitment_priorities.md)

## 参考公开来源

- [Accellera UVM Working Group](https://www.accellera.org/activities/working-groups/uvm)
- [Siemens Calibre Physical Verification](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/)

## 内容可信度说明

- **公开信息（高可信）**：UVM 标准组织、DFT/后端/硅后等角色类别、EDA 工具分工。
- **行业惯例（中可信）**：团队接口、交付物、review/signoff 责任划分。
- **经验性观察（中低可信）**：创业早期招聘优先级、哪些责任不能外包、软件背景创始人的管理盲点。
- **不确定/需向资深工程师确认（低可信）**：具体团队规模、人力配比、不同国家和供应链环境下的岗位设置。
