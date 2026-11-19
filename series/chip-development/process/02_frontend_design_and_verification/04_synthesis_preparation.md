# 综合准备需要哪些输入与检查

<span class="micro-legacy-anchor" id="综合准备"></span>

## 前置知识

先了解[微架构设计](02_microarchitecture_design.md)和 [RTL 设计](01_rtl_design_practices.md)。

## 综合准备的目标

逻辑综合将 RTL 展开并映射到目标库的单元。在 RTL 仍可修改时用试综合回答资源是否实例化正确、约束是否覆盖设计、路径与面积是否接近预算。后续物理反馈更新线长、负载和场景。 [OpenROAD Flow](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html)

## 输入物

| 输入 | 用途 |
| --- | --- |
| 文件集、顶层、宏定义、参数和 RTL | 确定本次展开的设计 |
| 单元、存储宏及 I/O 的时序、功能与物理视图 | 定义映射目标和实现接口 |
| SDC、功耗与测试意图 | 描述时钟、模式、边界和例外 |
| 面积、功耗和布局范围 | 给出优化目标与估算条件 |

## SDC 不是形式文件

先核对各主时钟、生成时钟、I/O 延迟、模式和不确定度。报告未约束端点、未生效的约束以及时序例外实际命中的路径。相关时钟和真异步时钟采用各自的分析方式。对于 multicycle，设计必须实现相应的采样规则，并检查相邻边沿的 hold 关系。 [OpenSTA 输入及例外](https://github.com/parallaxsw/OpenSTA/blob/master/README.md) · [CDC 与 RDC](06_cdc_and_rdc.md)

## Early Synthesis

检查 elaboration、宏映射、寄存器与组合逻辑规模、时钟门控识别、面积和关键路径。保留可复现的库、版本和脚本。试综合的物理效果取决于库和寄生估算。换目标库、布局或约束时，比较需要重新运行。

## 层次、报告和 LEC

保留层次便于界定接口与调试。展平给工具更多跨边界优化机会，可能增加调试和回归难度。综合输出网表、面积、时序、约束检查和映射结果。等价检查的结论绑定参考、实现、功能模式、复位和黑盒假设。时序、覆盖和功能规格各有检查。重定时需要匹配的时序关系及适用的比较方法。 [YosysHQ 等价与 X 传播](https://yosyshq.readthedocs.io/projects/eqy/en/latest/xprop.html)

<span class="micro-legacy-anchor" id="创业公司视角"></span>

## 典型场景

**教学假设。** DMA 有一个以数组方式描述的 SRAM。合成报告显示该数组被映射成大量触发器，原本预期绑定 SRAM 宏。先确认读写端口、地址和复位语义，再使用与行为匹配的宏或调整 wrapper。复查面积、时序、等价与 MBIST 接口。

## 角色和典型节奏

综合、RTL、STA、DFT 和物理负责人共同审核结果。交付注明版本、约束与未决事项。在接口、宏或时钟域变更后复查其影响。

## 后续阅读

- [前端交接评审](08_signoff_criteria.md)
- [可测性设计与制造测试](05_dft_introduction.md)
- [静态时序分析](../03_backend_physical_design/05_static_timing_analysis.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 综合与时序输入以及等价检查边界见工具文档。
- **行业做法。** 试综合、约束审查和交接以工程流为准。
- **教学假设。** SRAM 映射场景用于说明报告可以暴露的接口问题。
- **待项目核实。** 支持的 IP、库、约束语义与等价检查条件。
