# 07_for_software_background_founders：给软件背景芯片创业者

## 前置知识

- 建议先读 [完整生命周期](../00_overview/01_full_lifecycle.md)。
- 建议先读 [RTL 设计工程实践](../02_frontend_design_and_verification/01_rtl_design_practices.md)。
- 建议先读 [快速迭代相关横向主题](../06_cross_cutting_topics/README.md)。
- 建议理解 [RTL](../00_overview/05_glossary.md#rtl)、[Signoff](../00_overview/05_glossary.md#signoff)、[Respin](../00_overview/05_glossary.md#respin)、[NRE](../00_overview/05_glossary.md#nre)、[Yield](../00_overview/05_glossary.md#yield)。

## 本目录的作用

本目录不是芯片基础课，而是面向你这种系统软件架构师转向芯片创业的风险地图。你的优势是抽象能力、工具链经验、AI 芯片建模和自动化意识；短板是 RTL 工程纪律、验证文化、物理实现、封测量产、供应链和芯片商业成本。

核心目标是把软件世界的有效经验迁移到芯片世界，同时明确哪些直觉必须重写。软件可以持续发版、灰度、回滚、日志观测；芯片在 tapeout 后反馈周期变长、修改成本陡增、可观测性受限，错误会以 mask、wafer、封装、RMA 和客户信任的形式付费。

## 文件索引

- [01_common_misconceptions.md](./01_common_misconceptions.md)：软件背景创始人最常见的错误假设。
- [02_critical_mindset_shifts.md](./02_critical_mindset_shifts.md)：从软件工程思维切换到芯片工程思维。
- [03_recruitment_priorities.md](./03_recruitment_priorities.md)：创业初期招聘优先级、关键岗位和反模式。
- [04_first_chip_pragmatics.md](./04_first_chip_pragmatics.md)：第一颗芯片的务实范围、节点、IP、验证和客户策略。
- [05_fast_iteration_realities.md](./05_fast_iteration_realities.md)：快速迭代芯片公司的真实可压缩环节和不可压缩物理约束。

## 你最该建立的判断力

第一，区分模型正确、RTL 正确、可综合、可签核、可流片、可 bring-up、可量产、可客户交付。这些不是同义词，而是不同证据门槛。

第二，区分自动化能加速的环节和物理/商业不能跳过的环节。C model、RTL 生成、仿真、lint、coverage、文档、数据分析和 bring-up 脚本可以高度自动化；mask、wafer fab、封装、可靠性、客户 qualification、供应链 lead time 不能靠 agent 消失。

第三，区分“能外包执行”和“能外包责任”。后端、DFT、封装、测试、FA 可以外包或借助 turnkey，但产品定义、验证标准、质量门禁、客户承诺和现金风险必须由公司自己承担。

第四，区分 demo 和产品。Lab demo 证明可能性，量产产品需要 datasheet、test limits、qualification、yield、RMA、软件支持、客户文档和供应链承诺。

## 推荐阅读顺序

1. 先读 [常见误区](./01_common_misconceptions.md)，建立风险雷达。
2. 再读 [思维转换](./02_critical_mindset_shifts.md)，校准工程判断。
3. 然后读 [招聘优先级](./03_recruitment_priorities.md)，决定哪些能力必须内部建立。
4. 接着读 [第一颗芯片务实建议](./04_first_chip_pragmatics.md)，约束 V1 范围。
5. 最后读 [快速迭代真实约束](./05_fast_iteration_realities.md)，把愿景转成可执行路线。

## 创业公司底线

第一颗芯片不应同时承担太多目标：验证公司愿景、追求先进节点、全栈开源、复杂 AI workload、先进封装、高性能接口、量产交付、客户收入。目标越多，失败模式越难归因。

更务实的路径是把 V1 定义为“可信的学习和客户验证平台”：选择清晰 workload、成熟的可获得 IP、可管理封装、足够 debug/DFT、可运行软件栈、明确客户试点边界。V2 再基于硅后和客户数据扩大野心。

## 后续阅读

- [常见误区](./01_common_misconceptions.md)
- [关键思维转换](./02_critical_mindset_shifts.md)
- [招聘优先级](./03_recruitment_priorities.md)
- [第一颗芯片务实建议](./04_first_chip_pragmatics.md)
- [快速迭代真实约束](./05_fast_iteration_realities.md)

## 参考公开来源

- [OpenROAD GitHub repository](https://github.com/The-OpenROAD-Project/OpenROAD)
- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [CHIPS Alliance about page](https://www.chipsalliance.org/about/who-we-are/)

## 内容可信度说明

- **公开信息（高可信）**：芯片生命周期、signoff、respin、EDA、foundry、MPW、turnkey、开源工具的基本事实。
- **行业惯例（中可信）**：芯片创业早期的角色配置、V1 scope、验证/后端/量产门禁和外包治理。
- **经验性观察（中低可信）**：软件背景创始人的常见误区、组织反模式和快速迭代边界。
- **不确定/需向资深工程师确认（低可信）**：具体招聘市场、薪酬、节点成本、客户导入要求、foundry/OSAT 商务条款。
