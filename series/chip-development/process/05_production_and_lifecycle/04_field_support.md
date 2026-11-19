# 现场问题怎样追到批次并闭环

<span class="micro-legacy-anchor" id="field-support现场支持"></span>

## 前置知识

先建立[供应与批次追溯](03_supply_chain.md)的数据关联。实验室隔离方法见[硅后调试](../04_tapeout_and_post_silicon/05_post_silicon_debug.md)。

## 核心概念

现场支持要复现问题、确认影响范围、保护在用客户，并把结果反馈给质量、测试与设计。退货记录需关联产品、应用条件、使用时间与观察到的失败。退货、确认失效和失效率的分母分别定义。

## 关键活动顺序

1. 收集器件和板卡版本、运行条件、日志、批次及软件配置。保留失败样品状态。
2. 复核适用规格，并按最小重现步骤隔离软件、板卡、供电、封装和芯片。
3. 对照产线记录和已知良品。若需退货分析，记录接收、复测、封存和必要的失效分析。
4. 确定暂行措施、所涉批次和风险。按质量流程确认是否需要限制出货、通知、补测或改版。
5. 验证纠正措施，对受影响的产品范围和版本留档。将发现补入测试、规格或后续设计。

## 典型场景

**教学假设。** 某客户报告长时间负载后间歇复位。先记录是否超过数据手册温度或供电条件，复现并对比相同批号和另一批号。若问题随板卡版本走，继续检查板上电源及控制。若随样片或组装批走，核对晶圆和终测记录，再做失效分析。由同一观察期的出货与现场记录估计事件范围。

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

临时规避必须验证软件、工作条件、性能和可靠性边界。尤其在降低工作电压或改变频率时，应在已评估的允许范围内复验。对真实规格缺陷应更新勘误，审核受影响批次并决定避免再次发生的工程改动。 [FAB 失效分析](../../FAB/wiki/05-final-test-and-reliability/failure-analysis-flow.md) · [硅版本修订](../04_tapeout_and_post_silicon/08_silicon_revision.md)

<span class="micro-legacy-anchor" id="工具和基础设施"></span><span class="micro-legacy-anchor" id="角色周期和成本"></span>

## 上下游接口

输入为客户重现数据、产线记录、批次与规格。输出为现场沟通、退货和失效分析记录、纠正措施、测试或硅版本变更。变更通知要按合同和适用规范评估。 [TI 产品变更通知实例](https://www.ti.com/en-us/quality-reliability/quality/product-change-notification)

## 后续阅读

- [停产与产品支持](05_end_of_life.md)
- [故障隔离与失效分析](../../FAB/wiki/05-final-test-and-reliability/failure-analysis-flow.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 复现、追溯、变更与纠正流程应按客户和质量协议执行。
- **教学假设。** 间歇复位案例提供排查顺序。
- **待项目核实。** 客户服务条款、数据范围、退货统计、具体根因与批次影响。
