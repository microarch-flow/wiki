# 一颗芯片怎样从规格走到量产

<span class="micro-legacy-anchor" id="完整芯片生命周期总览"></span>

## 前置知识

本文覆盖典型的数字 ASIC/SoC 项目。涉及词义时可查[开发流程术语表](05_glossary.md)。

## 一句话总览

规格定义芯片必须满足的条件。设计团队把规格变成实现，验证和签核团队为该实现提供证据。制造与封测团队把版图变成可追溯的样品和成品。产品放行还要结合工作范围、生产测试、可靠性鉴定及适用的客户要求。

## 生命周期阶段速查表

| 阶段 | 主要输入 | 供下游使用的输出 |
| --- | --- | --- |
| 产品定义与架构探索 | 工作负载、系统接口、价格与供电约束 | 可测规格、候选方案、PPA 预算、参考模型和验证计划 |
| RTL、验证与集成 | 架构和微架构规格、IP、时钟复位及功耗意图 | 有版本的 RTL 和约束、回归与覆盖证据、DFT 计划、综合交接 |
| 综合与物理实现 | RTL 或综合网表、工艺和库、SDC、封装接口 | 门级网表、版图、提取寄生参数、时序与物理签核结果 |
| 流片与制造封测 | 提交版图、代工交接清单、封装与测试方案 | 晶圆、筛测记录、封装样片、测试日志 |
| 硅后与放行 | 工程样片、板卡、固件、测试程序和产品规格 | 工作条件、分档及测试限值、勘误、资格鉴定报告和放行记录 |
| 量产与现场支持 | 放行配置、供应计划、批次和客户要求 | 可追溯的成品、产线统计、质量闭环和版本管理 |

## 阶段 1：产品定义与商业假设

产品和系统团队定义目标场景、工作负载、输入范围和系统边界。验收指标需要测量方法。例如「延迟不超过 X」还要写明测量起点和终点、工作频率、并发、数据长度和背压条件。架构、验证和软件团队共同评审这些条件。 [规格定义](../01_product_definition_and_architecture/02_spec_definition.md)

## 阶段 2：架构探索与规格冻结

架构团队比较可实现的方案。功能参考模型可检查结果，分析或周期模型可估算被建模的资源和等待时间，试综合和早期布局可校准物理估算。评审时提交同一套负载下的比较、关键假设和未关闭问题。将冻结的接口和参数记录为有版本的基线。 [架构探索](../01_product_definition_and_architecture/03_architecture_exploration.md) · [阶段评审](../01_product_definition_and_architecture/06_milestones_and_signoffs.md)

## 阶段 3：前端设计与验证

设计团队将状态、接口、时钟和复位规则写成 RTL。验证团队将需求落实为参考结果、测试、属性和覆盖目标。低功耗、DFT 和物理实现团队应在此期间提供可实现性反馈。集成时交付可复现的版本、约束、IP 视图和验证证据。 [RTL 设计与集成](../02_frontend_design_and_verification/README.md) · [前端交接评审](../02_frontend_design_and_verification/08_signoff_criteria.md) · [OpenTitan 硬件开发阶段](https://opentitan.org/book/doc/project_governance/development_stages.html)

## 阶段 4：综合、DFT 与后端物理设计

综合把 RTL 映射到目标库的单元。DFT 团队在微架构阶段规划 scan、存储测试和测试访问，具体插入与组合方式取决于工具流和设计。物理实现团队迭代布局规划、放置、时钟树、布线和检查。签核应绑定同一发布候选的版图、网表、规则集、约束与工作条件。 [物理设计与签核](../03_backend_physical_design/README.md) · [OpenROAD Flow](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html) · [Synopsys DFT 综合](https://training.synopsys.com/learn/course/external/view/classroom/1109/fusion-compiler-dft-synthesis)

## 阶段 5：流片、晶圆制造、封装与测试

代工方接收版图和要求的辅助资料，进行数据检查与制版。制造完成后，按项目路线做晶圆筛测、切割、封装和封装后测试。设计公司通常在流片前并行准备测试程序、板卡、固件和实验方案。封装或测试接口涉及版图时，更早确定引脚、电源和观测路径。 [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md) · [从晶圆到成品](../../FAB/wiki/01-overview/from-wafer-to-product.md) · [OCP 多芯粒集成流程](https://www.opencompute.org/documents/chiplet-integration-workflows-1-pdf)

## 阶段 6：硅后 bring-up、特性化与量产

启动验证先确认样片可控、可观测，再运行最小功能。特性化在给定样品、温度、电压、频率和负载下测量功能范围与裕量。资格鉴定对代表性样本施加规定应力。量产测试用经验证的限值对产品筛选和分档。产品团队汇总这些证据，结合试产、供应和客户要求决定放行。 [硅后启动](../04_tapeout_and_post_silicon/04_post_silicon_bringup.md) · [硅片特性化](../04_tapeout_and_post_silicon/06_characterization.md) · [可靠性鉴定](../05_production_and_lifecycle/01_qualification_and_reliability.md) · [TI 资格鉴定说明](https://www.ti.com/en-us/quality-reliability/faqs)

## 阶段之间的回环

<figure class="chip-lifecycle-flow">
  <div class="chip-flow-step"><strong>产品与架构规格</strong></div>
  <div class="chip-flow-arrow" aria-hidden="true">↓</div>
  <div class="chip-flow-pair" role="group" aria-label="并行推进设计与封测准备">
    <div class="chip-flow-step"><strong>设计实现</strong><small>RTL、验证、布线、签核与流片交接</small></div>
    <div class="chip-flow-step"><strong>并行准备</strong><small>封装、测试、板卡与固件</small></div>
  </div>
  <div class="chip-flow-arrow" aria-hidden="true">↓</div>
  <div class="chip-flow-step"><strong>制造、封测与工程样品</strong></div>
  <div class="chip-flow-arrow" aria-hidden="true">↓</div>
  <div class="chip-flow-pair" role="group" aria-label="两类放行证据">
    <div class="chip-flow-step"><strong>硅后验证</strong><small>样片启动、工作范围与测试限值</small></div>
    <div class="chip-flow-step"><strong>试产与鉴定</strong><small>分档、批次追溯与可靠性证据</small></div>
  </div>
  <div class="chip-flow-arrow" aria-hidden="true">↓</div>
  <div class="chip-flow-step"><strong>产品放行评审</strong><small>按批准条件受控放量与出货</small></div>
  <figcaption>封装和测试约束会反馈到设计。硅后问题和量产异常会触发相应的复验或修订。</figcaption>
</figure>

这张图表示主要依赖。试布局发现连线拥塞时可回到布局规划或微架构。硅后问题若可由固件规避，则补做回归并更新勘误。若需要修改硅，受影响的实现、验证和签核重新闭合，再决定是否投片。 [OpenTitan 里程碑](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html)

<span class="micro-legacy-anchor" id="典型流程场景"></span>

## 典型场景

**教学假设。** 一个小型 DMA 模块接受搬运请求，将数据写入片上 SRAM，然后从 DMA 时钟域发出完成事件。控制域一次只允许一个事务未完成。规格规定目标 SRAM 的写入响应必须先于完成事件。两侧按约定复位，所有未完成事务视为取消，软件在重新初始化后提交新请求。

1. **规格与设计。** 记录输入、完成和取消条件。限制首版支持的地址范围和并发，定义何时可以提交下一笔请求。
2. **验证与交接。** 检查 SRAM 背压、复位取消和每个请求最多完成一次。审查完成事件的跨域握手及对应约束。记录参考模型、属性、测试和网表版本。
3. **硅后。** 先核对控制寄存器、时钟和复位，再搬运一段已知数据。检查 SRAM 内容、完成状态和中断。若数据正确而完成状态缺失，先区分跨域事件、复位和中断配置。
4. **量产。** 制造测试使用规定的测试访问与分档限值。功能小例继续用于工程验证和故障复现。若产品还依赖高带宽接口、更多并发或其他工作范围，应为这些要求单独建立证据。

## 上下游接口

评审记录至少能追到规格条款、实现基线、检查条件、结果和未关闭事项。下游若无法复现结论，先补齐输入和版本，再据此上报风险。

## 后续阅读

- [各角色和团队职责](02_roles_and_teams.md)
- [芯片项目成本结构](03_cost_structure.md)
- [逻辑前端、晶圆前道和封装后道](../../FAB/wiki/01-overview/front-end-vs-back-end.md)

## 参考公开来源

- [OpenTitan 阶段和签核](https://opentitan.org/book/doc/project_governance/development_stages.html)
- [OpenROAD 物理实现工具流](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html)
- [TI 产品资格鉴定及可靠性](https://www.ti.com/en-us/quality-reliability/faqs)

## 内容可信度说明

- **公开事实。** 设计与验证可分开跟踪成熟度。RTL 到版图可通过具体工具流复现。资格鉴定使用规定样本和条件。
- **行业做法。** 表和图采用典型数字 ASIC/SoC 的交付对象。阶段名称、团队分工和先后以目标项目为准。
- **教学假设。** 文中 DMA 事务及复位约定用于解释跨阶段证据，参数由例题给定。
- **待项目核实。** 代工方接收件、测试策略、资格鉴定方案、放行权限和排期。
