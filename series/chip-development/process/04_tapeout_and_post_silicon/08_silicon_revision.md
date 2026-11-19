# 硅版本修订何时需要重新投片

<span class="micro-legacy-anchor" id="silicon-revision"></span>

## 前置知识

先从[硅后调试](05_post_silicon_debug.md)与[量产良率分析](07_yield_analysis.md)取得可复现的问题和影响范围。

<span class="micro-legacy-anchor" id="上下游接口"></span>

## 核心概念

每种修复都应说明更改对象、验证范围、样件和客户影响。先确认根因与要满足的规格，再评估软件、板卡、封装、金属层或电路设计选项。

## Revision 类型

| 方案 | 适用条件 | 需检查的代价 |
| --- | --- | --- |
| 固件或软件规避 | 已知触发条件且能在允许的场景中隔离 | 性能、功耗、兼容、失效恢复和勘误 |
| 板卡或封装修订 | 根因位于相应边界，现有裸片仍可使用 | 工装、组装、电气热机械和资格复验 |
| 金属层修改 | 在允许层上实现改动。若使用预置备用单元，位置、类型及连接均须可用 | 受影响掩模、在制晶圆、时序、物理和测试回归 |
| 变更器件层或结构后投片 | 修改需要新的器件、宏、版图或超出允许的 ECO 层 | 制造路径、样品、验证和受影响的资格鉴定 |

ECO 是受控工程改动。流片前后均可能发生。改版范围影响可复用的掩模、工艺步骤和签核证据，具体结论由代工方和项目批准。

## 决策依据

列出对数据正确性、可靠性和客户规格的影响。用同样的验收判据比较方案。若问题未充分定位，先补能区分假设的实验或数据，再接受硅改版的代价。报价与排期见[成本结构](../00_overview/03_cost_structure.md)。

## Respin 流程

确定改动版本与影响后，复核规格、功能、等价、时序、物理规则和测试。必要时重新提交版图和制造，拿到样片后确认根因已消除，回归已支持的配置。按产品和工艺影响决定是否需要重新鉴定。更新勘误、识别版本和软件兼容。 [OpenTitan ECO 和流片里程碑](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html) · [TI 变更政策实例](https://www.ti.com/en-us/quality-reliability/quality/product-change-notification)

<span class="micro-legacy-anchor" id="先进节点与成熟节点差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 典型场景

**教学假设。** 某版缺少重复提交保护，可能干扰已接收的事务。若驱动能拒绝该操作，且复位和故障恢复均可验证，可以评审软件规避。若合同允许多个事务在途，则须重新满足并发规格，验证对旧接口、物理实现和生产测试的影响。

## 后续阅读

- [流片交接](01_tapeout_process.md)
- [可靠性鉴定](../05_production_and_lifecycle/01_qualification_and_reliability.md)
- [现场支持与退货分析](../05_production_and_lifecycle/04_field_support.md)

<span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="成本量级"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** ECO 回归、硅版本管理和重新鉴定按影响选择。
- **教学假设。** 规避示例依赖构造的驱动限制与契约。
- **待项目核实。** 能改的掩模层、备用单元、在制状态、供应商排期和客户接受范围。
