# 代工接入与交接需要确认什么

<span class="micro-legacy-anchor" id="foundry-relationshipsfoundry-关系"></span><span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="关系建立路径"></span>

## 核心概念

代工接口连接工艺、设计生态、制造与产能。设计公司需要从候选制程出发，分别确认设计资料、可用配套 IP、接收规则、可验证的终端产品条件和实际排期。 [TSMC 开放创新平台](https://www.tsmc.com/english/dedicatedFoundry/oip)

## 关键活动顺序

1. 明确候选工艺、应用和预期的面积、批量、封装与 I/O。
2. 按适用合同获取工艺模型、甲方要求和接入权限，核对设计与外部服务能使用的资料。
3. 确认可用标准单元、SRAM、I/O 与模拟或接口 IP。对齐规则、工具版本和配套视图。
4. 对照提交规范，从早期样例获得反馈。约定制版、晶圆筛测、切割和封装测试的责任。
5. 约定量产、排期、异常、报废、失效分析、批次信息和变更通知。 [TSMC 共享掩模服务](https://www.tsmc.com/english/dedicatedFoundry/services/cyberShuttle)

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

区分「工艺平台存在」「项目有权使用 PDK 与配套 IP」「指定工艺和封装窗口可供应」三项证据。早期原型、资格鉴定与量产可能需要不同时间和配置。报价按[成本结构](../00_overview/03_cost_structure.md)列明项目边界。

<span class="micro-legacy-anchor" id="角色周期和成本"></span><span class="micro-legacy-anchor" id="典型场景"></span>

## 上下游接口

产品与采购提供应用、批量和规格。代工接口将获得的工艺、工艺变更、接收清单和供应风险传给架构、物理、封测与质量。 [工艺规则与 PDK](../../FAB/wiki/02-front-end-fabrication/design-rule-and-pdk.md) · [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md)

## 后续阅读

- [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)
- [供应与批次追溯](../05_production_and_lifecycle/03_supply_chain.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** 工艺与合作伙伴的生态以及原型服务有厂商公开资料。
- **行业做法。** 接入顺序和交接方式参考阶段及风险组织。
- **待项目核实。** 实际权限、IP、接收工具和规则、供应承诺、报价与排期。
