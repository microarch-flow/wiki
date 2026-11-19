# 阶段评审需要哪些放行证据

<span class="micro-legacy-anchor" id="里程碑与签核"></span>

## 前置知识

先读[规格定义](02_spec_definition.md)和[架构探索](03_architecture_exploration.md)。

## 为什么早期也需要 Signoff

阶段评审确认一套可供下游使用的基线。高风险假设仍可能需要验证。评审记录应说明负责人、变更影响、接收条件和下一步的可检验输出。

<span class="micro-legacy-anchor" id="m0概念立项"></span><span class="micro-legacy-anchor" id="m1workload-冻结-v0"></span><span class="micro-legacy-anchor" id="m2产品规格草案"></span><span class="micro-legacy-anchor" id="m3架构候选收敛"></span><span class="micro-legacy-anchor" id="m4ip-和节点预签核"></span><span class="micro-legacy-anchor" id="m5架构规格冻结"></span><span class="micro-legacy-anchor" id="m6项目执行批准"></span>

## 推荐里程碑

| 决策 | 最少需要的输入 | 通过后交付 |
| --- | --- | --- |
| 概念立项 | 目标客户或场景、有待验证的价值主张 | 探索范围、负责人、按期可完成的验证任务 |
| 工作负载和初版规格 | 输入集、版本、参考结果、测量边界 | 可复现工作负载、需求编号和验收表 |
| 架构候选收敛 | 性能与 PPA 估算、模型假设和反例 | 候选比较、软件及验证代价、待做的试实现 |
| IP 与节点可行性 | 候选工艺、可得工艺文件、IP 交付视图、封装和测试约束 | 供给与技术条件、物理风险、采购和验证计划 |
| 架构基线与执行批准 | 版本化接口、预算分配、验证映射、残余风险 | RTL 启动的输入、变更机制、资源承诺和风险接受记录 |

这些决策可分批进行。例如，接口冻结前可以先验证 SRAM 宏的位置和布局压力，稳定的部分可以先进入 RTL。OpenTitan 分别记录设计和验证阶段，并给出诸如「最终 ECO」「流片签核」和「开始硅后验证」等录入和退出条件。本文表格是数字 ASIC 项目的一种评审组织。 [OpenTitan 开发阶段](https://opentitan.org/book/doc/project_governance/development_stages.html) · [OpenTitan 里程碑定义](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html)

<span class="micro-legacy-anchor" id="常见错误"></span><span class="micro-legacy-anchor" id="创业公司视角下的取舍"></span>

## 典型场景

**教学假设。** DMA 模块的 SRAM 宏尚未确定端口数。规格允许的输入和完成语义已清楚。产品组可以同意接口方向，物理组仍需提交两种端口与 banking 方案的面积、拥塞和延迟比较。评审记录端口部分待确认，限制依赖它的并行度承诺。确认后再更新基线和回归范围。

<span class="micro-legacy-anchor" id="签核会议应该怎么开"></span><span class="micro-legacy-anchor" id="指标与证据"></span>

## 上下游接口

规格和验证计划是设计评审的输入。进入后端还需可复现的 RTL 或网表、约束与前端证据包。流片签核使用的是最终版图与关联报告。三个决策各自指定可继续推进的范围。

## 后续阅读

- [前端交接评审](../02_frontend_design_and_verification/08_signoff_criteria.md)
- [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [芯片项目成本结构](../00_overview/03_cost_structure.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** OpenTitan 的里程碑和设计／验证状态记录可查阅。
- **行业做法。** 表格给出一组评审和交付物示例。固定顺序、人数、历时和批准权以项目计划为准。
- **教学假设。** SRAM 端口的决策场景只说明如何有条件地接收基线。
- **待项目核实。** 实际的标准、工具、验收门槛和评审签字人。
