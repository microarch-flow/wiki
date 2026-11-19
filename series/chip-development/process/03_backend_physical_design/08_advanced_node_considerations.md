# 工艺选择怎样影响物理实现

<span class="micro-legacy-anchor" id="advanced-node-considerations"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

当工艺变化时，器件、库、互连、电源和物理规则可能同时变化。物理实现组需要将平台差别转化成设计可检查的风险，并给架构和 RTL 返回约束。工艺选择的商业与系统取舍见[工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)。

## 关键活动顺序

| 关注点 | 做什么 | 交付证据 |
| --- | --- | --- |
| SRAM、模拟和 I/O | 核对宏、库、层与封装限制 | 可用视图、布局和工作边界 |
| 互连和过孔 | 试放置与布线，估算寄生与拥塞 | 同条件的路径及局部资源报告 |
| 变异和时钟 | 定义 PVT、RC 和变异场景 | 受约束端点、裕量和例外 |
| 供电、热和 EM | 对齐芯片、封装与板卡的活动和边界 | 电压、电流、温度和限制 |
| 签核工艺规则 | 确认版图版本、规则集和工具要求 | 已检查内容、批准豁免及变更影响 |

<span class="micro-legacy-anchor" id="7nm-以下与-2816nm-的核心差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

「7 nm 以下」可用于描述讨论范围，具体要求依据目标平台和层。EUV 或多重图形化的选择会影响可用工艺规则。金属互连延迟、引脚接入和电源网络也随几何与设计变化。用目标库、模型和布局检查变化最大的路径。 [TSMC N7+ 资料](https://pr.tsmc.com/english/news/2010) · [ASML EUV 与 DUV](https://www.asml.com/en/products/euv-lithography-systems) · [FAB 工艺规则与 PDK](../../FAB/wiki/02-front-end-fabrication/design-rule-and-pdk.md)

## 典型场景

**教学假设。** 新节点上逻辑面积下降，但 SRAM 宏不能按同一比例缩小，几条长线绕宏后仍超过时间预算。选项包括修改宏布局、调整 SRAM bank、修改流水线或规格。用当前工艺的早期走线、供电和时序结果比较。 [片内互连与 BEOL](../../FAB/wiki/02-front-end-fabrication/interconnect-stack-beol.md)

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="respin-成本边界"></span>

## 上下游接口

架构和工艺组选取候选。物理组提交试实现、规则适用范围和可收敛风险，反馈 RTL、测试与封装。成本与供应风险进入[成本结构](../00_overview/03_cost_structure.md)及[代工交接](../06_cross_cutting_topics/02_foundry_relationships.md)评审。

## 后续阅读

- [布局规划](01_floorplanning.md)
- [静态时序分析](05_static_timing_analysis.md)
- [DRC 与 LVS 签核](07_drc_lvs_signoff.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 特定平台的 EUV 例子与按层使用的原理有厂商来源。
- **教学假设。** 绕宏例子说明为何需要试实现。
- **待项目核实。** 实际工艺文件、签核配置、宏与封装可得性。
