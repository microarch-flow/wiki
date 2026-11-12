# Fast Iteration Realities：快速迭代的真实约束

## 前置知识

- 建议先读 [第一颗芯片务实建议](./04_first_chip_pragmatics.md)。
- 建议先读 [EDA 工具版图](../06_cross_cutting_topics/01_eda_tools_landscape.md)。
- 建议先读 [MPW 策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)。
- 建议理解 [Tapeout](../00_overview/05_glossary.md#流片-tapeout)、[MPW](../00_overview/05_glossary.md#mpw-multi-project-wafer)、[Respin](../00_overview/05_glossary.md#respin)、[Qualification](../00_overview/05_glossary.md#qualification)、[Volume Ramp](../00_overview/05_glossary.md#volume-ramp)。

## 核心判断

“快速迭代芯片公司”不是把整个芯片周期压缩成软件 sprint。更准确的目标是：把可数字化、可自动化、可前置验证的环节大幅加速；把必须物理制造和客户验证的环节纳入节奏设计；用更小、更频繁、更可解释的硅反馈降低大失败概率。

你能压缩的是认知周期，不是所有物理周期。mask 制造、wafer fab、封装、可靠性、客户 qualification、供应链 lead time 不会因为 agent 更聪明而消失。

## 可以显著加速的环节

架构探索可以加速。用 workload trace、C model、simulator、性能/功耗模型、自动 sweep 和成本模型，可以在 tapeout 前淘汰大量坏设计。AI agent 可以帮助生成实验、分析结果和维护文档。

RTL 生成和重构可以加速。基于 parameterized generator、DSL、C model、Chisel/SpinalHDL/SystemVerilog template 或 agent 生成，可以缩短实现时间。但生成 RTL 必须接入 lint、CDC、formal、仿真、coverage、synthesis smoke test 和 code review。

验证基础设施可以加速。自动生成 test、assertion、scoreboard、coverage report、regression triage、bug clustering 和 waveform 摘要，可以提高验证吞吐。关键是把自动化结果映射到 verification plan，而不是只增加 test 数量。

后端试跑可以加速。早期 floorplan、synthesis QoR、timing/congestion smoke test、power estimate 和 PPA dashboard 可以更早发现物理不可行架构。不要等 RTL 完全冻结才第一次看后端。

硅后数据分析可以加速。bring-up 脚本、实验自动化、telemetry、ATE/STDF 数据分析、RMA triage 和 yield dashboard 可以缩短问题定位时间。

## 难以压缩的环节

Foundry、PDK、IP 和商务路径难以压缩到软件节奏。NDA、PDK access、IP license、EDA license、tapeout slot、wafer start、capacity allocation 都需要外部方配合。

Mask 和 wafer fab 是物理周期。先进节点 mask、光刻、制造步骤、排产和 wafer cycle time 有硬约束。即使设计一次通过，制造仍然以周到月计。

封装和测试有供应链约束。先进封装、基板、HBM、socket、probe card、load board 和 ATE slot 都可能成为瓶颈。软件脚本不能替代封装产能。

Qualification 和客户导入难以压缩。可靠性 stress test、客户系统验证、供应商质量审批和生产 release 需要时间。跳过这些环节不是快速迭代，而是把风险转嫁给客户。

## 快速迭代的正确架构

第一层是纯软件/模型迭代：workload、C model、simulator、compiler、runtime、性能模型。目标是日到周级迭代。

第二层是 RTL/验证迭代：generator、RTL、testbench、formal、coverage、synthesis smoke test。目标是周级迭代。

第三层是物理实现迭代：floorplan、PPA、STA、IR/EM、DRC/LVS trial。目标是周到月级迭代。

第四层是小硅迭代：MPW/test chip、IP shuttle、tile prototype。目标是数月级迭代，每次回答少数关键问题。

第五层是产品硅迭代：full SoC tapeout、bring-up、qualification、volume ramp。目标是年度或多季度节奏，不能按普通软件 sprint 承诺。

层级之间要有晋级标准。模型层进入 RTL 前，应有目标 workload、误差范围、性能/功耗假设和客户价值假设；RTL 进入主线前，应通过 lint、CDC/RDC 基础检查、关键仿真、synthesis smoke test 和 review；架构进入后端 trial 前，应有初步 floorplan、SRAM/NoC/IO 假设和频率目标；MPW 前应写清楚 2-3 个要回答的问题、测试结构和硅后测量计划；产品硅前应有 design partner、软件最小闭环、bring-up plan、qualification 路径和预算 reserve。

## 组织和工具要求

快速迭代要求强配置管理。每个实验必须记录 workload、模型版本、RTL commit、generator 参数、EDA 工具版本、PDK/library 版本、约束、结果和结论。否则自动化产生的是噪声，不是学习。

要求强 signoff culture。自动化不能绕过 gate，只能让 gate 更早、更频繁、更低成本。每次迭代都应回答“这个结果改变了什么决策”，而不是只产生更多曲线。

要求强跨域 owner。架构、RTL、验证、后端、软件、硅后和客户反馈必须进入同一问题系统。快速迭代失败的常见原因是每个团队都很快，但接口很慢。

## 决策点

第一个决策是迭代单位。是模型、RTL block、tile、IP、test chip 还是 full SoC？越靠后成本越高，反馈越慢，问题越难归因。V1 前应尽量把问题拆到更小单位。

第二个决策是哪些风险需要真实硅。功能正确性、编译器映射和很多性能假设可以先在模型/FPGA/仿真中验证；SRAM、power、clock、DFT、物理 PPA、analog/PHY、封装和可靠性通常需要硅或更真实环境。

第三个决策是何时停止迭代并冻结。软件团队习惯持续优化，但芯片必须 freeze RTL、constraints、IP、floorplan 和 tapeout package。freeze 不是停止思考，而是控制变更成本。

第四个决策是如何使用 agent。Agent 应用于生成候选、维护文档、写 tests、分析报告和发现不一致；不应单独拥有 signoff 判断。关键风险必须由有经验工程师签字。

## 成本视角

快速迭代需要前期投入：自动化平台、CI、EDA license、仿真服务器、数据仓库、验证框架、MPW 预算、硅后实验基础设施。它不是免费加速，而是用平台 NRE 换更低的错误发现成本。

如果使用得当，最大收益是避免大错误进入 full chip tapeout。如果使用不当，自动化会让团队更快地产生大量未经验证的设计变体，增加验证和管理负担。

量级上，软件/模型/CI 层主要消耗工程人力和计算资源；RTL/验证层开始消耗商业 EDA license 和仿真/回归资源；物理层消耗后端工具、PDK/IP collateral、服务器和专家时间；MPW 层引入数万美元到数十万美元甚至更高的真实制造预算；产品硅层进入百万美元级 NRE 风险。越靠后，越应该减少变量、提高证据质量。

## 典型路线图

阶段 0：用 workload trace 和 C model 建立性能/功耗/成本模型，筛掉不合理架构。

阶段 1：建立 RTL generator + lint/CDC/synthesis smoke test + basic formal 的闭环，只允许通过门禁的 RTL 进入主线。

阶段 2：做小规模 MPW/test chip，验证 NPU tile、SRAM、clock/reset、DFT、debug 和后端 flow。

阶段 3：做 V1 SoC，范围受控，面向 design partner，目标是端到端可用和工程闭环。

阶段 4：基于硅后、客户、良率、软件数据做 V2，而不是只基于规格表幻想升级。

## 常见坑

- 把快速迭代理解为“更快 tapeout”，而不是“更早发现错误”。
- 每次迭代 scope 太大，问题不可归因。
- 自动生成 RTL 没有验证门禁。
- 频繁改架构，导致后端、验证和软件永远追不上。
- 对客户承诺软件式迭代速度，忽略硬件 supply chain。
- 不做 MPW/test chip，直接把所有风险压到 full SoC。

## 后续阅读

- [EDA 工具版图](../06_cross_cutting_topics/01_eda_tools_landscape.md)
- [MPW 策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)
- [Volume Ramp](../05_production_and_lifecycle/02_volume_ramp.md)

## 参考公开来源

- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)
- [Efabless chipIgnite](https://efabless.com/chipignite)
- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)

## 内容可信度说明

- **公开信息（高可信）**：MPW、tapeout、foundry、qualification、volume ramp、EDA 自动化的基本周期和边界。
- **行业惯例（中可信）**：模型/RTL/物理/MPW/full SoC 多层迭代，freeze gate 和 signoff culture。
- **经验性观察（中低可信）**：快速迭代的核心是提高反馈质量和错误前移，而不是把物理制造压成软件 sprint。
- **不确定/需向资深工程师确认（低可信）**：具体可压缩比例、MPW 节奏、foundry 周期、客户是否接受分阶段样片策略。
