# 前端交接评审需要哪些证据

<span class="micro-legacy-anchor" id="前端签核标准"></span>

## 前置知识

先从[功能验证](03_verification_methodology.md)和[综合准备需要哪些输入与检查](04_synthesis_preparation.md)理解证据的来源。

## Signoff 的含义

本页的签核指设计基线的交接评审。评审对象是一套有版本的 RTL、约束、IP 视图和检查结果。交接结论声明下游可使用的范围、仍开放的问题，以及变更后的复验责任。物理签核和流片决策使用各自的交付对象。 [OpenTitan 硬件阶段](https://opentitan.org/book/doc/project_governance/development_stages.html)

## 前端 Signoff Checklist

| 审查项 | 评审时查看 |
| --- | --- |
| 规格和接口 | 版本、需求到测试的映射、寄存器表和软件标头 |
| 功能 | 回归、属性、覆盖缺口、停用或延后功能的条件 |
| CDC／RDC 与低功耗 | 域、跨域、复位、电源状态及评审过的例外 |
| 综合及实现约束 | 顶层、参数、目标库、时钟和 I/O 时序，检查未约束端点 |
| DFT | 测试模式、存储测试访问、设计规则检查及后续向量交接 |
| 等价 | 参考与实现基线、模式与黑盒、已完成检查或计划 |
| 发布风险 | 已知问题、验证欠项、负责人与下游接受条件 |

OpenTitan 有公开的分阶段签核清单。内部项目可用自己的模板，按产品和阶段明确哪些项目必须关闭。 [OpenTitan 签核清单](https://opentitan.org/earlgrey_1.0.0/book/doc/project_governance/checklist/index.html)

## Bug 和 Waiver 管理

先区分真实缺陷、约束遗漏和已知工具限制。豁免应具体到报告项、设计版本、启用模式及证据，注明审批人和需要重新审核的变更。对真实缺陷，记录影响范围、缓解方案、剩余风险及接受人。

## 进入后端的交付包

交付带标记的版本、RTL 或综合网表的产生方式、约束、低功耗和测试意图、配套库与 IP 视图、报告及豁免记录。明确哪个团队负责重新产生结果。下游用同一版本、参数和库复现交接时至少运行一次基础检查。

## 与 ECO 和 Agent 工作流的关系

签核后有工程修改时，列出影响范围，再运行相关的功能、等价、时序、物理和测试检查。生成式 RTL 还需记录生成源版本、参数和可重现的输出。若改动涉及规格或参考行为，先更新批准的参考版本及验收条件。

<span class="micro-legacy-anchor" id="创业公司视角"></span>

## 典型场景

**教学假设。** DMA 功能回归通过，但跨域报告没有涵盖复位取消，工具还发现未约束的生成时钟。先查时钟关系和约束覆盖，补做取消时序的结构与功能检查。评审结果记录重新生成的报告版本与下游适用条件。

## 后续阅读

- [物理设计与签核](../03_backend_physical_design/README.md)
- [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md)

<span class="micro-legacy-anchor" id="典型时长和节奏"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** OpenTitan 的成熟度与交接条目提供可查看的项目示例。
- **行业做法。** 清单是数字 ASIC 的交接示例。通过条件与责任划分依项目而定。
- **待项目核实。** 签字权限、豁免政策、覆盖目标、IP 使用条件与流片前最终检查。
