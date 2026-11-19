# 从软件开发转向芯片项目的常见误区

<span class="micro-legacy-anchor" id="common-misconceptions软件背景人的常见误区"></span><span class="micro-legacy-anchor" id="误区一c-model-正确rtl-就只是翻译"></span><span class="micro-legacy-anchor" id="误区二仿真通过就能流片"></span><span class="micro-legacy-anchor" id="误区三硬件也可以像软件一样快速修"></span><span class="micro-legacy-anchor" id="误区四开源和自动化可以绕过商业生态"></span><span class="micro-legacy-anchor" id="误区五外包可以解决自己不懂的问题"></span><span class="micro-legacy-anchor" id="误区六第一颗芯片要证明所有愿景"></span>从一项承诺出发，找到批准它所需的证据。以下问题适合用于第一次项目评审。

| 容易下的结论 | 评审时要查 |
| --- | --- |
| C 模型已经正确，可以直接确定 RTL | 模型是否描述了时钟、状态、背压、复位和可综合的资源成本？ [微架构设计](../02_frontend_design_and_verification/02_microarchitecture_design.md) |
| 回归通过，可以流片 | 交付版本、覆盖、例外、DFT、时序、物理与供电证据分别是什么？ [前端交接评审](../02_frontend_design_and_verification/08_signoff_criteria.md) · [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md) |
| 出现问题可以像软件一样更新 | 修改软件、板卡、封装和版图分别需要哪些验证？现有样片可否继续使用？ [硅版本修订](../04_tapeout_and_post_silicon/08_silicon_revision.md) |
| 开放工具能覆盖所有项目条件 | 工艺、设计套件、IP、规则与实际发布版本是否可用？ [开放芯片与开放 PDK](../06_cross_cutting_topics/03_open_source_silicon.md) |
| 外包完成就能接受交付 | 验收谁负责，怎样复现，如何追到规则、约束和版本？ [外包交接](../03_backend_physical_design/09_backend_outsourcing.md) |
| 首次上电成功即可接受客户交付 | 还需要哪些目标规格、测试、资格鉴定及试产记录？ [量产与生命周期](../05_production_and_lifecycle/README.md) |

<span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="典型流程场景"></span>

## 后续阅读

- [决策记录与反馈](02_critical_mindset_shifts.md)
- [第一颗芯片的范围](04_first_chip_pragmatics.md)

<span class="micro-legacy-anchor" id="成本视角"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **工程建议。** 表格为项目评审问题索引。具体判据与批准权查相应项目。
