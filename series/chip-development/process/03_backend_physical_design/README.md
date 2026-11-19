# 物理设计与签核

<span class="micro-legacy-anchor" id="03_backend_physical_design后端物理设计"></span>物理设计把映射到目标工艺库的逻辑网表实现成版图。团队需要在规定条件下同时满足时序、供电、布线和物理规则。布局和签核结果会反馈给架构、RTL、DFT 和封装。

<span class="micro-legacy-anchor" id="典型时长与角色"></span>

## 关键输入与输出

| 输入 | 用途 |
| --- | --- |
| 网表、SDC、功耗意图、DFT 约束 | 定义逻辑、时序关系、电源和测试模式 |
| Liberty、LEF、工艺规则、宏视图和 RC 模型 | 描述单元功能时序、可用几何资源与寄生 |
| 封装、I/O 和电源连接约束 | 定义端口、凸点、供电和设计边界 |

输出包括可继续实现的检查点、最终版图、寄生提取数据和检查结果。流片交接绑定同一候选版本的输入、输出及批准的例外。 [OpenROAD Flow](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html)

## 后端主流程

布局规划决定宏、引脚、通道和电源网。放置阶段迭代单元位置和合法化。时钟树阶段将时钟送到接收点。布线阶段选择金属层、线段和过孔，随后提取寄生参数。各步使用逐渐具体的模型检查时序、拥塞和供电。签核过程中，修复布线或金属填充会改变寄生，需要重跑受影响的检查。

<span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="本目录的作用"></span><span class="micro-legacy-anchor" id="文件索引"></span><span class="micro-legacy-anchor" id="典型场景"></span><span class="micro-legacy-anchor" id="后续阅读"></span>

## 阅读顺序

1. [布局规划](01_floorplanning.md)确定宏、I/O、面积和供电骨架。
2. [标准单元放置](02_placement.md)在时序、线长和局部拥塞之间迭代。
3. [时钟树综合](03_clock_tree_synthesis.md)控制时钟到达差、转换时间和功耗。
4. [布线与寄生提取](04_routing.md)把逻辑连接映射到物理线与过孔。
5. [静态时序分析](05_static_timing_analysis.md)读取模式、角落与路径裕量。
6. [功耗、压降与电迁移](06_power_analysis.md)检查活动、供电路径和可靠性限值。
7. [DRC 与 LVS 签核](07_drc_lvs_signoff.md)解释几何规则和电路一致性。
8. [工艺选择怎样影响物理实现](08_advanced_node_considerations.md)把风险反馈到方案选择。

项目外包的输入、交付和责任见[后端外包交接](09_backend_outsourcing.md)。工具查找见 [EDA 工具版图](../06_cross_cutting_topics/01_eda_tools_landscape.md)。

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="关键决策点"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="成本视角"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** OpenROAD 文档给出一种可追踪的 RTL 到版图流程。
- **行业做法。** 工程项目按工艺和设计确定分工、工具、报告与签核条件。
- **待项目核实。** 采用的库、规则集、模式／角落和代工方接受条件。
