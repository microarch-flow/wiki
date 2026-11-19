# 怎样用证据管理芯片项目决策

<span class="micro-legacy-anchor" id="critical-mindset-shifts关键思维转换"></span><span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="转换一从程序顺序到硬件并行"></span><span class="micro-legacy-anchor" id="转换二从测试发现-bug到证据关闭风险"></span><span class="micro-legacy-anchor" id="转换三从可观察系统到低可观察系统"></span><span class="micro-legacy-anchor" id="转换四从部署成本低到部署成本高"></span><span class="micro-legacy-anchor" id="转换五从单机服务优化到物理和供应链优化"></span><span class="micro-legacy-anchor" id="转换六从工程速度到反馈回路质量"></span>

## 决策模板

在接受一项工程承诺前，把假设变成可复查记录。记录可以很短，每一项应有明确的依据和负责人。

| 字段 | 写法 |
| --- | --- |
| 目标和判据 | 测什么对象，什么条件算通过 |
| 现有证据 | 规格、模型、回归、实现报告、样片或产线记录的版本 |
| 已知缺口 | 哪些环境、接口、批次或失效机理还未覆盖 |
| 处理方式 | 补验证、限制使用范围或交给后续阶段，写明影响 |
| 接受与复验 | 谁批准、何时重新打开、何种变更触发复验 |

## 典型场景

**教学假设。** 仿真通过一个 DMA 搬运例子。工程记录应标明只验证了规定范围内的功能。接下来分别补查跨域和复位、实际时序、芯片制造测试。若封装引脚变化，重开受影响的测试与接口证据。

## 角色和组织转换

项目负责人维护决策与未解决事项。设计、验证、实现、测试和质量人员各自维护可审查结果。下游需要了解使用条件，并能把错误追到版本。OpenTitan 的阶段、评审和版本档案可作例子。 [OpenTitan 里程碑](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html)

## 后续阅读

- [阶段评审与放行证据](../01_product_definition_and_architecture/06_milestones_and_signoffs.md)
- [前端交接评审](../02_frontend_design_and_verification/08_signoff_criteria.md)
- [怎样缩短反馈周期](05_fast_iteration_realities.md)

<span class="micro-legacy-anchor" id="成本视角"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 工程记录及复验机制按项目采用。
- **教学假设。** 搬运案例用于说明不同证据的覆盖边界。
