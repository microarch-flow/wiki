# 设计服务与 Turnkey 怎样约定交付

<span class="micro-legacy-anchor" id="turnkey-services设计服务与-turnkey"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

设计服务的工作可以从局部实现延伸到设计、制版、制造、封测等组合交付。范围以合同和技术附件定义。即使使用同一个服务名称，也要确认谁接收、验收以及对变更负责。

## 服务类型

| 服务 | 可能的输入 | 约定产物 |
| --- | --- | --- |
| 专项设计或验证 | 规格、接口、工具与检查条件 | RTL、测试或审核报告与限制 |
| 物理实现 | RTL 或网表、IP、工艺与约束 | 候选版图、日志、脚本和签核证据 |
| 制造及封测协同 | 版图、裸片、封装和测试定义 | 项目约定的晶圆、封装件、测试和良率数据 |
| Turnkey | 端到端的范围和里程碑 | 项目合同规定的设计、制造、测试或出货产物 |

<span class="micro-legacy-anchor" id="工具角色和成本"></span><span class="micro-legacy-anchor" id="上下游接口"></span>

## 关键活动顺序

规格和技术附件写明版本、IP 和数据权限、各关口判据、变更后的复验、异常批与售后支持。先用代表性模块确认服务商可运行所需流程。交付时复核原始记录与最终对象一致。 [TSMC 设计服务生态](https://www.tsmc.com/english/dedicatedFoundry/oip)

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

评估服务的执行能力及项目自身的复核能力。报价需明确是否含 IP、工具、试片、返工、封装工装、测试和量产支持。发生变动时，确认谁提供证据、谁批准、如何回到前一阶段。 [后端外包交接](../03_backend_physical_design/09_backend_outsourcing.md) · [芯片项目成本结构](../00_overview/03_cost_structure.md)

## 典型场景

**教学假设。** 合同包含版图交付与物理验证，未约定测试程序和封装。项目在流片前应指定测试、封装和硅后负责人，以及后端提供引脚图、测试访问和候选版本的日期。

## 后续阅读

- [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [供应与批次追溯](../05_production_and_lifecycle/03_supply_chain.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 表中按交付边界列出服务实例。
- **教学假设。** 示例用于说明技术附件中的职责。
- **待项目核实。** 商务范围、权限、签核、报价和产能。
