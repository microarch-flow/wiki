# EDA 工具版图

<span class="micro-legacy-anchor" id="eda-tools-landscapeeda-工具版图"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

按交付物理解工具。一个工具可能覆盖多个步骤。同一步骤也可由多个工具完成。应记录输入格式、模型、配置、输出、适用限制和下游复核。

## 工具链分层

| 工程问题 | 输入 → 输出 | 可查阅的实例 |
| --- | --- | --- |
| RTL 是否处理了规定场景 | 规格、RTL、测试和属性 → 仿真结果、覆盖与反例 | [OpenTitan 验证环境](https://opentitan.org/book/doc/contributing/dv/methodology/index.html) |
| 如何把 RTL 映射到库 | RTL、库和约束 → 网表、面积与时序报告 | [Yosys 文档](https://yosyshq.readthedocs.io/projects/yosys/en/latest/) |
| 综合或改动后是否等价 | 参考、实现与假设 → 等价结果或反例 | [YosysHQ EQY](https://yosyshq.readthedocs.io/projects/eqy/en/latest/) |
| 怎样放置、布线与提取 | 网表、工艺、约束和宏 → 版图与寄生 | [OpenROAD Flow](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html) |
| 版图是否满足指定检查 | 网表、版图、库、约束和规则 → STA、DRC、LVS 等报告 | [OpenSTA](https://github.com/parallaxsw/OpenSTA/blob/master/README.md) · [Siemens Calibre](https://www.siemens.com/en-us/products/ic/calibre-design/circuit-verification/) |
| 怎样获得制造测试向量 | 可测网表、测试模式和故障模型 → 向量、故障分类和覆盖 | [Synopsys TestMAX ATPG](https://www.synopsys.com/implementation-and-signoff/test-automation/testmax-atpg.html) |

## 关键活动顺序

选择最小代表设计，跑通所需文件和报告，并记录工具版本、设置、模型及限制。确定每个关口的复现步骤，分清早期探索、实现检查和正式签核使用的配置。试跑之后再评估授权、并发、供应商支持及升级、回归代价。

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

开源工具能复现一部分设计流程，具体可用步骤由工艺、库、配置和项目要求决定。开放 PDK 的发布状态与相同制程的商业设计套件可能不同。正式交付核对目标工艺认可的工具、规则和方法。 [开放芯片与开放 PDK](03_open_source_silicon.md) · [SkyWater 开放 PDK 状态](https://skywater-pdk.readthedocs.io/en/main/status.html)

<span class="micro-legacy-anchor" id="角色周期和成本"></span><span class="micro-legacy-anchor" id="典型场景"></span>

## 上下游接口

设计与验证提供可构建输入。CAD／实现团队负责可复现的运行环境。签核和制造接口确认运行方式与接收条件。工具推荐、报价或支持范围应在项目时点复查。

## 后续阅读

- [综合准备需要哪些输入与检查](../02_frontend_design_and_verification/04_synthesis_preparation.md)
- [物理设计与签核](../03_backend_physical_design/README.md)
- [芯片项目成本结构](../00_overview/03_cost_structure.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 表中用途和示例范围以项目或厂商资料为准。
- **行业做法。** 代表设计试跑、版本固定和交付验收按项目执行。
- **待项目核实。** 目标工艺支持、工具版本、签核认可、授权及价格。
