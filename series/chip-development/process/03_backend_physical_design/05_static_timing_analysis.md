# 静态时序分析怎样读路径和签核报告

<span class="micro-legacy-anchor" id="static-timing-analysis"></span>

## 前置知识

先读[时钟树综合](03_clock_tree_synthesis.md)和[电路到时序的共用基础](../../../microarchitecture/02-pipeline/electrical-timing-foundations.md)。

## 核心概念

静态时序分析（STA）按网表、时序约束、库与模型计算已覆盖的时序关系。它在给定模式和角落下传播信号最早及最晚到达时刻，再与要求比较。布线后分析使用提取的寄生数据。除了 setup 和 hold，还应按设计检查异步控制端的 recovery／removal、时钟脉宽和其他适用检查。 [OpenSTA 输入和检查](https://github.com/parallaxsw/OpenSTA/blob/master/README.md)

## 关键活动顺序

1. 确认功能、测试和低功耗等模式。为每个分析场景绑定适用的库、PVT、RC 和变异模型。
2. 核对主时钟、生成时钟、I/O 延迟和时序例外。报告未覆盖的端点，并逐项确认原因。
3. 在综合、放置、CTS 和布线提取后更新估算。记录时钟是理想时钟还是传播时钟，防止混用报告。
4. 按最差端点追到时钟、数据、约束和寄生，选择修复方式。同一设计改动可能改善 setup，同时恶化 hold 或功耗。
5. 重新运行受影响的检查。报告与最终网表、版图、约束和例外一同归档。

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

时序例外需要设计依据。False path 可以排除指定的普通时序检查。跨域同步结构和对应的物理约束仍需验证。Multicycle 约束需要真实的采样控制及配套的 setup 和 hold 边沿。 [Intel CDC 约束](https://www.intel.com/content/www/us/en/docs/programmable/683243/25-1/constraining-cdc-paths.html) · [电路与时序基础](../../../microarchitecture/02-pipeline/electrical-timing-foundations.md)

## 典型场景

**教学假设。** 同一标称时钟域的寄存器路径，周期 800 ps。基线的发送、接收时钟到达差取 0。数据到达时间包含 clock-to-Q 和数据路径延迟。setup 和 hold 可使用各自场景，本例单独给出早、晚数据。

| 检查 | 到达时刻 | 要求时刻 | 裕量 |
| --- | ---: | ---: | ---: |
| Setup | 最晚 750 ps | 800 − 45 − 25 = 730 ps | 730 − 750 = **−20 ps** |
| Hold | 最早 35 ps | 25 + 10 = 35 ps | 35 − 35 = **0 ps** |

表中 setup 时间为 45 ps，setup 不确定度为 25 ps。hold 时间为 25 ps，hold 不确定度为 10 ps。若只将捕获时钟推迟 30 ps，setup 要求变成 760 ps，裕量为 +10 ps。hold 要求变成 65 ps，裕量为 −30 ps。实际时钟调整还需检查其他路径和分析条件。 [AMD setup 方程](https://docs.amd.com/r/2026.1-English/ug906-vivado-design-analysis/Setup/Recovery-Relationship?contentId=vOSoXJu3asbkH1uyuWp0Lg) · [AMD hold 方程](https://docs.amd.com/r/2026.1-English/ug906-vivado-design-analysis/Hold/Removal-Relationship?contentId=dZBm6BfVStfa~EyRyUpHjA)

另举一个同一报告范围内的例子。两条路径到同一端点，裕量是 −20 和 −8 ps。另一端点的最差路径是 −5 ps。按 AMD UG906 的端点统计方式，WNS 为 −20 ps，TNS 为 −25 ps，违例端点有 2 个。使用其他工具或报告视图时，先确认 TNS 的聚合方式与非违例时的显示约定。 [AMD UG906，Design Timing Summary](https://docs.amd.com/api/khub/documents/1tipwNqhy1~RxTdCrHCn1g/content)

## SI 与 Noise Signoff

耦合和同时切换可能改变路径延迟，或在受害节点引入噪声。目标流程需要定义所用寄生、工作模式、耦合分析与电源条件。一次改线可能改变多个路径，应复查受影响的物理和时序结果。

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span>

## 上下游接口

STA 接收网表、库、约束、寄生和分析场景。输出报告应包含设计版本、有效约束、未覆盖端点、相关路径和用于根因分析的时钟与数据延迟。若问题来自结构或流水边界，将具体关键路径反馈给 RTL 和架构组。

## 后续阅读

- [功耗、压降与电迁移](06_power_analysis.md)
- [DRC 与 LVS 签核](07_drc_lvs_signoff.md)
- [综合准备需要哪些输入与检查](../02_frontend_design_and_verification/04_synthesis_preparation.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** STA 输入、基本 setup／hold 方程和 AMD 报告口径见所列资料。
- **教学假设。** 裕量、时钟变化和端点数据为可手算示例。
- **待项目核实。** 工具统计口径、例外路径、模式／角落及当前候选版图的覆盖。
