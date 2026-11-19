# 流片交接需要哪些数据与证据

<span class="micro-legacy-anchor" id="tapeout-process"></span>

## 前置知识

先读[物理设计与签核](../03_backend_physical_design/README.md)及 [DRC 与 LVS](../03_backend_physical_design/07_drc_lvs_signoff.md)。

<span class="micro-legacy-anchor" id="tapeout-前必须完成的签核"></span>

## 核心概念

流片交接将已批准的设计候选送入制版和晶圆制造。版图、签核报告、约束和例外应指向同一候选。代工方接收后按对应工艺检查数据。发生重提时，设计团队按变更影响重新评审。 [TSMC 掩模服务](https://www.tsmc.com/english/dedicatedFoundry/services/mask_services) · [OpenTitan 流片里程碑](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html)

## 流片前的签核证据

检查候选的功能与等价、时序、物理规则、供电和可靠性、DFT 与测试模式、封装及 I/O 边界。适用项目、模式和规则版本由项目与供应商共同确定。每个例外记录影响区域、可接受条件、证据和批准人。核对最终版图与签核所用版图的校验值。

## Tapeout Package

| 交接谁 | 一组典型输入 | 关键核对 |
| --- | --- | --- |
| 代工或制版接口 | OASIS 或 GDSII、顶层名称、制程选项、版图层和提交表单 | 具体清单、数据结构与接收规则取自项目提交规范 |
| 内部实现与签核归档 | 网表、约束、提取数据、库和规则版本、运行脚本、报告、变更与豁免 | 能复现签核，清楚记录黑盒与报告范围 |
| 封装与测试团队 | 裸片尺寸和标记、端口与凸点图、测试时钟和模式、向量或测试计划 | 与发布候选一致，明确封装后访问、分档与追溯接口 |

同一个文件可以出现在多份交接清单。代工方接收哪些报告、网表或辅助件要查当次项目要求。 [SkyWater GDS 接收规则示例](https://skywater-pdk.readthedocs.io/en/main/rules/errors.html)

<span class="micro-legacy-anchor" id="典型工具"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="上下游接口"></span>

## 关键活动顺序

1. 冻结候选与配套工具配置。
2. 运行规定的最终检查，完成开放风险与豁免评审。
3. 对已检查的版图生成交接清单、校验值与可复现归档。
4. 提交后确认接收状态。若收到数据或规则问题，按影响范围修改、复核并重提。
5. 同步封装、测试和版本状态，供后续样件追溯。

## ECO 边界

改变布线、填充、网表、功能或 IP 的 ECO 影响不同。先辨认改变了哪些检查输入，补做相应签核。若已开始制版或生产，向代工方确认在制状态、可变更范围和新投片路径。 [硅版本修订](08_silicon_revision.md)

<span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 典型场景

**教学假设。** 报告中 LVS clean 对应候选 A。随后补了金属填充，得到候选 B。即使功能网表未改，也要确认填充对物理检查、寄生和时序的影响。交接清单仅接受报告与候选版本关系明确的一套产物。

## 后续阅读

- [掩模制作与晶圆制造](02_mask_making_and_wafer_fab.md)
- [封装如何进入芯片项目](03_packaging.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 代工服务、部分接收规则和公开项目的签核里程碑可查阅。
- **行业做法。** 表格和版本核对流程为工程示例。
- **待项目核实。** 必交材料、允许的工具和规则、豁免权限、制版时点及排期。
