# 量产爬坡怎样从试产走到稳定出货

<span class="micro-legacy-anchor" id="volume-ramp量产爬坡"></span>

## 前置知识

先读[量产良率分析](../04_tapeout_and_post_silicon/07_yield_analysis.md)与[可靠性鉴定](01_qualification_and_reliability.md)。

## 核心概念

量产爬坡是按证据增加合格产出。每次放量用约定的批次、配置和指标观察良率、设备与人员能力、交付、逃逸风险和异常处置。出货稳定需要共同管理封装、测试、材料和客户要求。

## 关键活动顺序

1. **工程批。** 验证样片、工作范围，开发测试程序和工装。
2. **代表性试产。** 使用拟量产的工艺、组装、测试和追溯配置，观察批间差异、设备时间和分档。
3. **放行评审。** 核对适用的鉴定、数据手册、客户约定、测试版本、批次指标及异常处置。记录批准的范围。
4. **受控放量。** 逐步提高投入和产出，监控过程与测试分布。超限时按规则暂停或隔离，审查、复测后再放行。
5. **持续优化。** 改测试时间、限值或物料时，先评估质量与覆盖，再选择适用的验证、客户通知或重新鉴定。 [TI 变更控制实例](https://www.ti.com/en-us/quality-reliability/quality/product-change-notification)

试产、特性化与鉴定的排期可重叠。放行以已接受的证据和产品条款为前提。

<span class="micro-legacy-anchor" id="先进节点与成熟节点差异"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

按工序查看瓶颈，例如可用裸片、组装合格量、ATE 产能、目标分档和备料。降低测试时间时，要复核屏蔽的向量或条件、复测、过杀及客户逃逸率。变更前后应使用可比的批次和数据定义。 [FAB 测试覆盖与成本](../../FAB/wiki/03-wafer-test-and-cp/test-cost-vs-coverage-tradeoff.md)

## 典型场景

**教学假设。** 首批通过率变好，同时终测版本缩短了若干项目。产品工程先按测试版本匹配同一批样品，再核对删减项发现的失效和样片重复性。没有等价检测证据时，将观察到的通过率变化标为试产结果。

<span class="micro-legacy-anchor" id="工具和数据系统"></span><span class="micro-legacy-anchor" id="角色周期和成本"></span>

## 上下游接口

产品工程、测试、质量和运营共同维护产线版本、分档、异常处置和量产放行范围。输出给供应和现场支持，包括批次、规格、数据留存与变更记录。 [供应与批次追溯](03_supply_chain.md)

## 后续阅读

- [供应与批次追溯](03_supply_chain.md)
- [现场支持与退货分析](04_field_support.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 工程批、试产和阶段放量是项目组织示例。变更流程参考厂商公开实例。
- **教学假设。** 测试版本的例子用于检查通过率是否可比较。
- **待项目核实。** 目标分档、批量、质量限值、产能与客户放行。
