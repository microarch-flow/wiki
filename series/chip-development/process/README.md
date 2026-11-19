# 芯片开发与实现

<span class="micro-legacy-anchor" id="芯片开发流程-wiki"></span>这套资料以数字 ASIC/SoC 为主。主线采用无晶圆厂设计公司的视角，从产品规格走到量产交付。[FAB 制造与封测](../FAB/wiki/README.md)从物料侧解释晶圆、裸片、封装、筛测与失效机理。

## Wiki 目标

读者可以从一个交付物出发，追到上游假设、负责团队和放行证据。例如，一颗首硅跑通演示后，继续检查测试限值能否支撑数据手册、样本是否覆盖资格鉴定要求，以及生产线是否可以稳定分档和追溯。

## 总流程图

[生命周期导读的依赖图](00_overview/01_full_lifecycle.md#阶段之间的回环)给出设计、物理实现、封测准备和硅后放行的关系。制造现场的对象流见 [一片晶圆到成品芯片](../FAB/wiki/01-overview/from-wafer-to-product.md)。

## 推荐阅读顺序

1. [芯片开发生命周期](00_overview/01_full_lifecycle.md)先建立规格、设计、首硅与量产的全局视图。
2. [产品定义与架构探索](01_product_definition_and_architecture/README.md)把工作负载写成可验收的要求。
3. [RTL 设计与集成](02_frontend_design_and_verification/README.md)把规格细化为可实现结构。接着阅读[功能验证](02_frontend_design_and_verification/03_verification_methodology.md)和[前端交接评审](02_frontend_design_and_verification/08_signoff_criteria.md)。
4. [物理设计与签核](03_backend_physical_design/README.md)跟踪网表、约束、版图和签核报告。
5. [流片与硅后](04_tapeout_and_post_silicon/README.md)从设计提交追到样片启动、故障隔离和工作范围测量。
6. [量产与生命周期](05_production_and_lifecycle/README.md)看资格鉴定、工程试产、正式放行和现场反馈。

## 重点阅读路径

| 手头的问题 | 阅读路线 |
| --- | --- |
| 准备第一次架构评审 | [工作负载](01_product_definition_and_architecture/01_market_and_workload_analysis.md) → [规格定义](01_product_definition_and_architecture/02_spec_definition.md) → [架构探索](01_product_definition_and_architecture/03_architecture_exploration.md) → [阶段评审](01_product_definition_and_architecture/06_milestones_and_signoffs.md) |
| 评估首版芯片或原型 | [成本结构](00_overview/03_cost_structure.md) → [工艺节点选择](01_product_definition_and_architecture/05_process_node_selection.md) → [MPW 多项目晶圆策略](06_cross_cutting_topics/04_mpw_shuttle_strategy.md) → [第一颗芯片的范围](07_for_software_background_founders/04_first_chip_pragmatics.md) |
| 从设计追到制造测试 | [可测性设计与制造测试](02_frontend_design_and_verification/05_dft_introduction.md) → [晶圆筛测与 KGD](../FAB/wiki/03-wafer-test-and-cp/README.md) → [成品终测](../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md) |
| 封装影响架构选型 | [封装如何进入芯片项目](04_tapeout_and_post_silicon/03_packaging.md) → [封装与多芯粒集成](../FAB/wiki/04-back-end-packaging/README.md) → [封装供电与热路径](../FAB/wiki/06-cross-cutting-engineering/README.md) |

<span class="micro-legacy-anchor" id="完整文件索引"></span><span class="micro-legacy-anchor" id="00_overview"></span><span class="micro-legacy-anchor" id="01_product_definition_and_architecture"></span><span class="micro-legacy-anchor" id="02_frontend_design_and_verification"></span><span class="micro-legacy-anchor" id="03_backend_physical_design"></span><span class="micro-legacy-anchor" id="04_tapeout_and_post_silicon"></span><span class="micro-legacy-anchor" id="05_production_and_lifecycle"></span><span class="micro-legacy-anchor" id="06_cross_cutting_topics"></span><span class="micro-legacy-anchor" id="07_for_software_background_founders"></span>

## 章节索引

- [开发流程导读与术语](00_overview/README.md)
- [产品定义与架构探索](01_product_definition_and_architecture/README.md)
- [RTL 设计与集成](02_frontend_design_and_verification/README.md)
- [物理设计与签核](03_backend_physical_design/README.md)
- [流片与硅后](04_tapeout_and_post_silicon/README.md)
- [量产与生命周期](05_production_and_lifecycle/README.md)
- [工具、供应商与实现策略](06_cross_cutting_topics/README.md)
- [软件背景创始人导读](07_for_software_background_founders/README.md)
- [FAB 制造与封测](../FAB/wiki/README.md)

## 使用建议

遇到「签核通过」时，先问三个问题。检查的是哪个版本？判据和适用条件是什么？未关闭的风险由谁接受？涉及术语时可查[开发流程术语表](00_overview/05_glossary.md)和 [FAB 术语表](../FAB/wiki/08-reference/glossary.md)。

## 内容可信度说明

- **公开事实**见正文相邻的标准、官方文档或原始报告。不同资料所描述的阶段、工具和产品范围以来源为准。
- **行业做法**按示例项目给出。具体阶段名称、签核责任和活动顺序由项目确定。
- **教学示例**采用正文声明的参数。**待项目核实**的交付清单、限值、排期和报价由对应团队或供应商确认。
