# 软件背景人在前端容易踩的坑

## 前置知识

- 建议先读 [RTL 设计工程实践](./01_rtl_design_practices.md)。
- 建议先读 [前端验证方法学](./03_verification_methodology.md)。
- 建议先读 [CDC 与 RDC](./06_cdc_and_rdc.md)。
- 建议理解 [RTL](../00_overview/05_glossary.md#rtl)、[C Model](../00_overview/05_glossary.md#c-model)、[Synthesis](../00_overview/05_glossary.md#synthesis)、[Signoff](../00_overview/05_glossary.md#signoff)。

## 坑 1：把 RTL 当并发软件

软件并发通常是线程、锁、队列和内存模型。RTL 是电路结构。每个寄存器、mux、比较器、加法器、RAM 端口都真实存在。你写的每个条件和位宽都会影响面积、时序和功耗。

典型错误是用软件式控制流写硬件：大量嵌套 if、动态数组、复杂循环、隐式共享状态。仿真看起来像程序执行，综合后可能变成巨大组合逻辑或不可综合结构。正确心智是：先画寄存器、数据路径、控制状态机和时钟边界，再写 RTL。

## 坑 2：相信 C model 等于硬件规格

[C Model](../00_overview/05_glossary.md#c-model) 很适合定义算法结果，但硬件还需要定义时序、并发、资源冲突、异常、reset、功耗状态和可调试性。C model 没定义的行为，RTL 和验证就会各自猜。

常见遗漏包括 backpressure、pipeline latency、定点舍入、非法配置、buffer overflow、DMA 边界、interrupt 顺序、reset during transaction。建议把 C model 拆成 reference model 和 cycle-aware model，并为每个未定义行为做规格决策。

## 坑 3：过度相信 agent 生成 RTL

Agent 生成代码的最大价值是提高草稿速度和样板一致性，不是替代 RTL owner。它容易生成看似合理但工程不合格的 RTL：裸 CDC、隐式 latch、位宽错误、不可综合语法、reset 不完整、协议 corner case 缺失、test mode 不可用。

如果要用 agent，应把它放在受控流程里：输入必须是结构化微架构规格；输出必须经过 lint、仿真、formal、synthesis smoke；生成器和 prompt 必须版本管理；所有人工修改必须回灌到生成源；标准接口、FIFO、CDC、寄存器、clock gating 用模板库，不让 agent 自由发挥。

## 坑 4：把“仿真通过”当完成

仿真只覆盖你跑到的场景。硬件 bug 常藏在没跑到的组合：并发、异常、reset、低功耗、跨域、满空、边界值、软件误配置。没有 coverage 的回归只是安慰剂。

你需要问：需求是否映射到 test 或 assertion；coverage hole 是否解释过；random test 是否覆盖 backpressure 和并发；formal 是否覆盖仿真难穷尽的协议；gate-level、LEC、CDC/RDC、DFT 是否检查过。

## 坑 5：低估 reset 和 X

软件初始化失败通常很快崩溃，硬件 reset 问题可能表现为偶发启动失败。X 在 RTL 仿真中既可能暴露未初始化问题，也可能被仿真语义掩盖或放大。不要用“仿真里没看到 X”证明 reset 安全。

控制状态、valid bit、software-visible register、interrupt、FSM 必须有明确 reset 行为。数据路径可以不全部 reset，但必须证明无效数据不会被消费。

## 坑 6：不尊重 clock domain

跨时钟域不是普通函数调用。两个模块频率不同、相位不定，信号不能直接传。单 bit、pulse、多 bit bus、stream、counter、reset 都需要不同同步结构。

软件背景的人常在顶层 glue logic 里“顺手连一下”。这类代码可能让仿真全过，但硅上随机失败。工程规则应是：任何跨域必须通过标准 primitive，并由 CDC 工具签核。

## 坑 7：忽视 DFT 和量产测试

软件产品可以通过日志和线上监控定位问题。芯片出厂前要靠 scan、MBIST、ATE pattern 筛坏片。没有 [DFT](../00_overview/05_glossary.md#dft)，你甚至不知道失败芯片坏在哪里。

RTL 早期如果乱用 gated clock、异步 reset、latch、不可控 black box，会让 DFT 后期非常痛苦。即使第一版是开源原型，也要为基本 scan、MBIST、JTAG/test mode 留接口。

## 坑 8：把性能指标写成峰值

软件 benchmark 常可持续迭代，芯片峰值一旦写进市场叙事就会变成产品承诺。AI 芯片尤其容易用 TOPS 掩盖真实瓶颈。真实性能取决于 memory bandwidth、tiling、utilization、host-device traffic、batch size、compiler、runtime 和热限制。

在前端阶段，应让性能计数器和 stall reason 成为微架构的一部分。没有硬件可观测性，硅后无法解释为什么真实 workload 跑不满。

## 坑 9：把参数化当复用

软件里泛型和配置常提高复用。RTL 参数化会放大验证矩阵。每个参数组合可能改变位宽、FIFO 深度、状态空间、timing path 和 CDC 结构。

创业早期应少量固定配置，优先验证闭环。等 generator、验证和综合流程成熟后再扩大参数空间。

## 坑 10：低估工具和流程

软件工具链通常开源且可本地复现。先进 ASIC 依赖昂贵商业 EDA、PDK、IP model、license server、foundry signoff deck 和 vendor support。工具版本差异会影响综合、仿真、formal、CDC 和 DFT 结果。

不要以为开源 RTL 就能开源完整先进节点量产流程。可以开源设计意图、可综合 RTL、仿真环境和部分开源 flow，但先进节点 signoff 仍离不开商业工具和 foundry 数据。

## 典型场景

软件背景创始人实现了一个 C++ NPU 模型，并让 agent 生成 RTL。demo 在 Verilator 中跑通，融资材料展示 benchmark。引入资深 DV 后发现：没有 reset during operation 测试，没有 backpressure，寄存器 side effect 没定义，DMA 与 NPU 跨时钟，性能计数器会读清零但文档没写，综合后 address decoder 成关键路径，DFT 无法处理手写 gated clock。

这个项目不是“差一点工程化”，而是缺少前端设计纪律。修复路径是补微架构规格、接口协议、验证计划、lint/CDC/DFT 规则、early synthesis 和 signoff gate。Agent 仍可用，但只能在规则内生成。

## 给 Biao 的行动建议

你已有系统软件、工具链和 C model 背景，这是优势，适合建立架构探索、生成器、回归系统、trace、差分验证和自动化 dashboard。但第一阶段必须补齐硬件负责人：资深 RTL lead、DV lead、DFT/physical-aware advisor。不要让团队文化停留在“软件能跑就行”。

你的自动化方向应聚焦在可验证生成：spec-to-RTL、spec-to-assertion、spec-to-test、spec-to-doc、spec-to-register model 一致生成，而不是只生成 Verilog。硬件自动化真正值钱的部分是把错误挡在签核前。

## 角色、节奏、成本与接口

软件背景创始人的关键职责不是亲自写所有 RTL，而是建立正确 owner 结构：架构 owner 对产品和模型负责，RTL lead 对硬件实现负责，DV lead 对验证证据负责，DFT/后端/硅后顾问对制造和调试可行性负责。早期每周应有一次跨角色 design review，检查接口变化、验证缺口、CDC/DFT/综合风险和软件可见行为。

上游输入是你的产品假设、workload、C model、编译器/runtime 计划和融资约束；下游输出是可执行的微架构合同、RTL 生成规则、验证 dashboard、signoff gate 和招聘/外包决策。成本上，最不该省的是资深判断力；最可以自动化的是重复生成、回归、文档一致性和报告汇总。把判断权外包给 agent 或设计服务公司，通常会在后端、硅后或客户现场以更高成本偿还。

## 后续阅读

- [招聘优先级](../07_for_software_background_founders/03_recruitment_priorities.md)
- [第一颗芯片的务实建议](../07_for_software_background_founders/04_first_chip_pragmatics.md)
- [快速迭代的真实约束](../07_for_software_background_founders/05_fast_iteration_realities.md)
- [开源芯片策略](../06_cross_cutting_topics/03_open_source_silicon.md)

## 参考公开来源

- [IEEE 1800-2023 SystemVerilog 标准页面](https://standards.ieee.org/standard/1800-2023.html)
- [Verilator](https://github.com/verilator/verilator)
- [OpenROAD](https://github.com/The-OpenROAD-Project/OpenROAD)
- [Accellera Standards](https://accellera.com/downloads/standards)
- [Synopsys SpyGlass CDC](https://www.synopsys.com/verification/static-and-formal-verification/spyglass/spyglass-cdc.html)

## 内容可信度说明

- **公开信息（高可信）**：SystemVerilog、Verilator、OpenROAD、Accellera 标准和 CDC/verification 工具生态公开可查。
- **行业惯例（中可信）**：reset、CDC、DFT、coverage、synthesis、signoff、工具版本管理是 ASIC 前端工程基本要求。
- **经验性观察（中低可信）**：软件背景团队常过度相信 C model、仿真和代码生成，低估 reset/CDC/DFT/验证闭环；可验证生成比单纯生成 RTL 更重要。
- **不确定/需向资深工程师确认（低可信）**：具体团队招聘顺序、自动生成器架构、开源与商业 EDA 混合流程、第一颗芯片 signoff 阈值需要结合资金、节点和产品目标确认。
