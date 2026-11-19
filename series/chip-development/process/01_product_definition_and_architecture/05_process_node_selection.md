# 工艺节点选择需要比较哪些条件

<span class="micro-legacy-anchor" id="工艺节点选择"></span><span class="micro-legacy-anchor" id="7nm-及以下的特殊考虑"></span><span class="micro-legacy-anchor" id="28nm16nm-的现实价值"></span><span class="micro-legacy-anchor" id="典型场景"></span>

## 前置知识

先固定[产品规格](02_spec_definition.md)和[架构候选](03_architecture_exploration.md)。工艺节点的物理背景见 [FAB 工艺节点与 PPA](../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)。

## 工艺节点选择的本质

工艺选型的输入是应用要求、候选架构、库和 IP、封装与测试条件、采购和排期。输出是可复核的候选比较与待确认清单。节点名称描述平台和代际，库、SRAM、模拟、金属栈和可实现目标各自变化。例如 TSMC 将 N4 描述为 N5 的增强版本，并在 N2 采用 nanosheet 器件。这些厂商事实要绑定具体工艺。 [TSMC 工艺平台](https://www.tsmc.com/english/dedicatedFoundry/technology/platform_smartphone_tech_advancedTech) · [TSMC 2025 年报](https://investor.tsmc.com/static/annualReports/2025/english/pdf/2025_tsmc_ar_e_ch2.pdf)

## 工艺节点影响什么

| 维度 | 同条件比较时需核查 |
| --- | --- |
| 数字逻辑 | 用同功能、约束及负载对照库、门延迟、面积和功耗 |
| SRAM 和模拟 | 宏尺寸、端口、工作电压、表征条件和已验证范围 |
| 布线与供电 | 金属栈、DRC、线阻、过孔、电压裕量和电源网 |
| IP 与工具流 | 代工方、工艺版本、授权、配套视图和签核工具要求 |
| 封装与测试 | I/O、凸点、热路径，能否供应、组装和覆盖测试 |
| 单位经济 | 掩模、晶圆、裸片面积、分档、后续封测及可能返工 |

性能数据需说明等功耗或等频率等比较条件。工艺平台给出的逻辑密度收益只适用于定义的比较对象。估算 SoC 面积时，分开建模逻辑、SRAM、模拟、I/O 和实现开销。 [FAB PPA 取舍](../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)

## AI 芯片为什么倾向先进节点

高计算密度或严格能量预算可能推动采用先进逻辑平台。若目标负载主要受外部内存、软件或封装散热限制，只增加算力可能没有吞吐收益。分析应对照相同工作负载、服务质量及板级功耗限制，再看特定工艺方案能否解除主限制。

## 节点选择流程

1. 定义工作负载、频率、可交付规格和成本目标。
2. 建立各候选的逻辑、SRAM、互连、I/O 和封装预算。
3. 检查 PDK、可用库和 IP 的版本，确定关键宏与接口是否可得。
4. 用相同约束做代表性综合和试布局，给出余量和待解决问题。
5. 根据目标分档、批次、报价和供应条件估算成本，提交阶段评审。

<span class="micro-legacy-anchor" id="角色和典型时长"></span>

## 成本量级

用项目报价比较掩模、晶圆、IP、EDA、封装、测试及返工。量产分母使用目标规格和分档。历史数据和示例集中在[芯片项目成本结构](../00_overview/03_cost_structure.md)。

## MPW 与 full mask

试验要先定义能验证的风险。较小的 MPW 试片可检查目标库、接口、宏或工作条件。量产方案另行确认目标晶圆、封装、测试、客户与供给条件。 [MPW 多项目晶圆策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)

## 后续阅读

- [工艺选择怎样影响物理实现](../03_backend_physical_design/08_advanced_node_considerations.md)
- [工艺规则与 PDK](../../FAB/wiki/02-front-end-fabrication/design-rule-and-pdk.md)
- [架构到工艺与封装选型](../../FAB/wiki/06-cross-cutting-engineering/from-architecture-to-process-selection.md)

<span class="micro-legacy-anchor" id="关键决策点"></span><span class="micro-legacy-anchor" id="常见错误"></span><span class="micro-legacy-anchor" id="创业公司视角下的取舍"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 工艺家族、器件结构和版本例子来自 TSMC 公开资料。
- **行业做法。** 同负载比较、拆分面积和试实现用于说明工程取舍。
- **待项目核实。** 当前供给、平台 PPA、配套 IP、报价、良率、资格鉴定和合同。
