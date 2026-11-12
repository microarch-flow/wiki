# Critical Mindset Shifts：关键思维转换

## 前置知识

- 建议先读 [常见误区](./01_common_misconceptions.md)。
- 建议先读 [RTL 设计工程实践](../02_frontend_design_and_verification/01_rtl_design_practices.md)。
- 建议理解 [Verification](../00_overview/05_glossary.md#verification)、[Validation](../00_overview/05_glossary.md#validation)、[Signoff](../00_overview/05_glossary.md#signoff)、[Yield](../00_overview/05_glossary.md#yield)、[Qualification](../00_overview/05_glossary.md#qualification)。

## 转换一：从程序顺序到硬件并行

软件代码默认按控制流顺序执行，性能优化经常是减少复杂度、提高缓存命中和并发调度。RTL 描述的是每个时钟周期同时发生的状态更新。一个 `always_ff` 不是一个函数调用，而是一组寄存器在时钟边界同时采样。

这种差异会改变设计评审方式。软件 review 可以关注 API、异常处理和模块边界；RTL review 必须追问信号在每个 cycle 的有效性、握手协议、backpressure、reset 后状态、组合路径深度、跨时钟同步和可综合性。

## 转换二：从“测试发现 bug”到“证据关闭风险”

软件测试通常通过更多 case 提高信心。芯片验证也需要测试，但更重要的是建立风险覆盖证据：功能 coverage、code coverage、assertion、formal proof、CDC/RDC、lint、emulation、FPGA、post-silicon validation。每种方法覆盖不同风险。

好的芯片项目会把 spec 中的每个需求映射到 verification item、coverage item、owner 和 signoff status。没有这个 traceability，就无法判断“还有哪些风险没关”。

## 转换三：从可观察系统到低可观察系统

软件系统有日志、core dump、metrics、debugger、tracing。芯片内部信号在硅上不可随意观察。你必须在设计阶段决定 scan、JTAG、trace buffer、performance counter、error register、safe mode、boot strap、telemetry 和 firmware hooks。

这意味着 debug 不是硅后活动，而是设计需求。删 debug hooks 省面积，可能会在硅后用数周甚至 respin 还债。

## 转换四：从部署成本低到部署成本高

软件部署成本低，失败可以回滚。芯片部署成本包含 mask、wafer、封装、测试、库存、客户导入和 RMA。硬件 bug 不一定能发补丁；即使能 workaround，也可能牺牲性能、功耗或功能。

所以芯片项目的 gate 更重：architecture review、spec review、verification signoff、DFT signoff、physical signoff、tapeout review、qualification release、production release。它们不是官僚流程，而是避免错误进入高成本阶段。

## 转换五：从单机/服务优化到物理和供应链优化

软件性能最终运行在已有硬件和云基础设施上。芯片产品本身就是物理产品：面积、功耗、热、封装、良率、测试时间、库存和供应链都影响商业成功。一个架构如果 PPA 好但封装/供电/测试不可承受，仍然不是好产品。

对 AI 芯片，memory bandwidth、NoC、SRAM、HBM、散热、开发板和机柜部署会决定持续性能。架构探索必须把这些物理和系统约束纳入模型。

## 转换六：从工程速度到反馈回路质量

快速迭代不等于快写 RTL。真正有价值的是缩短“假设 -> 实现 -> 验证 -> 物理反馈 -> 客户反馈”的闭环。软件背景的优势可以用在工具链、CI、数据平台、自动化测试、编译器和观测系统上，但要接入硬件 signoff 证据。

如果没有质量门禁，自动化只会更快地产生错误。好的自动化应该让错误更早暴露，而不是让团队更快越过 review。

## 角色和组织转换

软件团队常按服务、平台、应用划分；芯片团队还需要按前端、验证、DFT、后端、封装、测试、软件、质量、供应链划分职责。早期团队可以小，但角色责任不能缺。一个人可以兼任多个角色，但不能让某个角色不存在。

CTO/创始人需要从“技术方案 owner”转为“风险闭环 owner”。你不需要亲自懂每个 signoff deck，但要知道每个阶段的证据是什么、谁负责、哪些 waiver 可接受、哪些风险不能带到下一阶段。

## 决策模板

遇到芯片项目关键决策时，建议固定问六个问题：这个决策影响哪个生命周期阶段？它的上游假设是什么？下游谁会为它付费？如果错了，最早在哪个阶段暴露？修复路径是什么？需要谁签字接受风险？

例如决定删掉 trace buffer 省面积。上游假设是验证足够充分；下游影响硅后 debug 和 field support；错误暴露可能在 bring-up 或客户现场；修复路径可能是 firmware 盲调或 respin；接受风险的人不应只是 RTL owner，还应包括验证、硅后、产品和客户支持。

把这个模板变成固定 operating mechanism，而不是临时讨论。每个重大变更都应形成一页 decision record，至少包含：变更摘要、影响阶段、上游假设、受影响文件/模块、验证证据、后端/DFT/软件影响、成本和 schedule 影响、替代方案、waiver、回滚路径、签字人。签字人至少覆盖 architecture、verification、backend/physical、software/firmware、product/program；若影响客户或预算，还应包含 business owner。

这个机制的价值是让创始人看到“谁在承担什么风险”。没有签字机制时，风险会被拆散在 Slack、issue 和会议口头结论里，直到 tapeout 或客户现场才集中爆发。

## 典型场景

团队为了赶进度，希望跳过 formal 和 emulation，只跑 directed simulation。软件直觉是“先发一个版本再修”。芯片直觉应是：如果目标模块涉及协议、仲裁、死锁或长状态空间，仿真很难覆盖；跳过 formal 可能把低概率死锁带到硅上。正确决策是缩小 scope、降低功能，而不是降低验证证据。

## 成本视角

思维转换本身的成本是学习、招聘和流程建设；不转换的成本是 respin、客户失败和组织混乱。早期花数周建立 verification plan、flow checklist 和 review 机制，通常比后期用数月修硅后问题便宜。

## 后续阅读

- [招聘优先级](./03_recruitment_priorities.md)
- [第一颗芯片务实建议](./04_first_chip_pragmatics.md)
- [快速迭代真实约束](./05_fast_iteration_realities.md)

## 参考公开来源

- [Accellera UVM Working Group](https://www.accellera.org/activities/working-groups/uvm)
- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)
- [JEDEC JESD47 standard page](https://www.jedec.org/standards-documents/docs/jesd47)

## 内容可信度说明

- **公开信息（高可信）**：verification、validation、signoff、qualification、硬件可观测性和生命周期成本的基本概念。
- **行业惯例（中可信）**：traceability、gate review、debug hooks、formal/emulation 适用场景和风险闭环。
- **经验性观察（中低可信）**：软件背景创始人应从技术实现 owner 转为风险闭环 owner。
- **不确定/需向资深工程师确认（低可信）**：具体组织设计、各 gate 的签字机制和项目可接受风险阈值。
