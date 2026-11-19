# 可靠性鉴定怎样支持产品放行

<span class="micro-legacy-anchor" id="qualification-and-reliability可靠性认证"></span>

## 前置知识

先了解[硅片特性化](../04_tapeout_and_post_silicon/06_characterization.md)和[成品终测](../../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md)。

## 核心概念

可靠性鉴定（qualification）使用代表性样本和规定应力，评估指定的设计、工艺、封装和生产组合。计划从使用环境、工作寿命、预期失效机理和客户要求出发。量产终测使用已验证的限值逐件筛选，按产品策略另行安排筛选性 burn-in。 [TI 可靠性和 JESD47 说明](https://www.ti.com/en-us/quality-reliability/faqs) · [FAB Burn-in 与应力测试](../../FAB/wiki/05-final-test-and-reliability/burn-in-and-stress-test.md)

## 关键活动顺序

1. 记录器件、封装、工艺、生产站点和应用条件，选取适用标准、等级和客户要求。
2. 按试验计划指定有代表性的批次、样本数、应力、读取方式和失效判据。
3. 执行应力和测量。记录异常、失效和实际试验条件。
4. 失效时跟踪样品和试验日志。确认装配、设备和测试条件，必要时进入失效分析。
5. 发布报告，标明覆盖的版本、样本、条件、失效、偏差和评审结论。
6. 当材料、工艺、封装、设计或站点变化时，评估受影响的失效机理，选用补充验证或重新鉴定。

JEDEC JESD47 提供应力驱动的集成电路资格鉴定框架。车规 IC 需按适用 AEC-Q100 版本、等级和客户条款选择测试。具体方法、时长和样本以项目采用的版本为准。试验类型与失效机理见 [FAB 可靠性标准](../../FAB/wiki/05-final-test-and-reliability/reliability-jedec-standards.md)。实际记录格式可参考一份具体料号的 TI 报告。 [TI DRV8847PWRG4 资格鉴定报告](https://www.ti.com/quality-reliability-packaging-download/es-mx/report?opn=DRV8847PWRG4)

## 典型场景

**教学假设。** 产品拟更换封装基板材料。质量和封装团队先对齐材料、结构、组装工艺和应用温度。根据改变的热膨胀与界面行为，选择需重新检查的应力项目。报告记录老版、新版及受影响批次。若应力后出现开路，先确认位置和机理，再评估对生产放行和通知的影响。

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

确认通过结论覆盖哪个配置和使用条件。试验报告用于支持产品放行，并与特性化、终测、试产和客户验收记录一起评审。估算现场寿命时需要适用的加速模型和使用条件。给定样本的通过率只描述所做试验。

<span class="micro-legacy-anchor" id="典型工具和设备"></span><span class="micro-legacy-anchor" id="角色周期和成本"></span>

## 上下游接口

质量团队维护鉴定方案与结论。产品、设计、封装、测试和客户团队核对变更与应用边界。输出供量产放行、批次处置和客户通知使用。 [TI 产品变更通知实例](https://www.ti.com/en-us/quality-reliability/quality/product-change-notification)

## 后续阅读

- [量产爬坡](02_volume_ramp.md)
- [供应与批次追溯](03_supply_chain.md)
- [FAB 失效分析](../../FAB/wiki/05-final-test-and-reliability/failure-analysis-flow.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** JEDEC 资格鉴定实践、样本报告和产品变更流程见厂商资料。
- **行业做法。** 项目根据配置、失效机理和应用条件决定补测范围。
- **教学假设。** 更换基板材料的例子不代表某产品的实际试验方案。
- **待项目核实。** 适用标准及版本、样本、应力、限值、偏差批准和客供条款。
