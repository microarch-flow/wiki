# 流片与硅后

<span class="micro-legacy-anchor" id="04_tapeout_and_post_silicon流片与硅后"></span>这一组文章从最终设计交接开始，跟踪晶圆和封装样片如何产生，硅后怎样启动、定位与测量，何时需要更新工作范围或修订硅片。

## 主流程

设计候选通过约定的签核后，提交代工方规定的版图与辅助数据。制造、筛测和封装形成工程样品。硅后团队用与版本匹配的板卡、固件及测试程序验证样片。工作范围、良率及可靠性证据汇入[量产与生命周期](../05_production_and_lifecycle/README.md)的放行评审。完整依赖见[生命周期导读](../00_overview/01_full_lifecycle.md#阶段之间的回环)。

<span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="本目录的作用"></span><span class="micro-legacy-anchor" id="文件索引"></span><span class="micro-legacy-anchor" id="角色和接口"></span><span class="micro-legacy-anchor" id="后续阅读"></span>

## 阅读顺序

1. [流片交接](01_tapeout_process.md)准备并核对数据包。
2. [掩模制作与晶圆制造](02_mask_making_and_wafer_fab.md)跟踪代工交接与晶圆状态。
3. [封装如何进入芯片项目](03_packaging.md)在流片前确定接口与测试路径。
4. [首硅启动](04_post_silicon_bringup.md)从受控上电走到最小事务。
5. [硅后调试](05_post_silicon_debug.md)用对照实验隔离故障。
6. [硅片特性化](06_characterization.md)从样片和条件矩阵确定工作范围。
7. [量产良率分析](07_yield_analysis.md)用分档与批次数据定位损失。
8. [硅版本修订](08_silicon_revision.md)决定规避、局部改版或重新投片。

这些步骤的准备工作会重叠。样片和产线验证所依赖的封装、测试、板卡与固件应在约定节点前可用。 [OpenTitan 流片和硅后里程碑](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html)

<span class="micro-legacy-anchor" id="典型周期和成本"></span><span class="micro-legacy-anchor" id="关键决策点"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司视角"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 顺序按依赖关系组织。测试路线、样片批次和放行要求以项目为准。
- **待项目核实。** 供应商交期、实际提交件、工程样片的限制和客户放行条件。
