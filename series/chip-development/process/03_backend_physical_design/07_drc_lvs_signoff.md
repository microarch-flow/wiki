# DRC 与 LVS 在流片前各检查什么

<span class="micro-legacy-anchor" id="drclvs-signoff"></span>

## 前置知识

先了解[布线与寄生提取](04_routing.md)和[工艺规则与 PDK](../../FAB/wiki/02-front-end-fabrication/design-rule-and-pdk.md)。

## 核心概念

DRC 检查版图几何是否符合选定工艺规则。LVS 抽取版图中的器件和连线，并与参考电路比较。DRC clean 的范围由输入版图、运行的规则和批准的豁免确定。LVS clean 的范围由参考网表、匹配、抽取和黑盒配置确定。物理签核还需按工艺与产品选择适用的密度、天线、电气、可靠性等检查。 [Siemens DRC](https://www.siemens.com/en-us/products/ic/calibre-design/physical-verification/design-rule-checking/) · [Siemens LVS 与电路验证](https://www.siemens.com/en-us/products/ic/calibre-design/circuit-verification/)

## 关键活动顺序

1. 冻结待检查的版图、参考网表、工艺、规则集、层映射和工具配置。
2. 在模块和全芯片层级执行适用的 DRC、LVS 与其他检查。
3. 将结果归为真实版图问题、输入或配置错误、以及有依据的豁免。明确外部接受要求。
4. 修复后重跑受影响的检查。填充、改线或过孔变动可改变寄生和供电，需要同步回归。
5. 归档最终提交版图的校验值、检查报告、规则和批准记录。 [SkyWater 规则示例](https://skywater-pdk.readthedocs.io/en/main/rules/periphery.html)

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

实现工具的局部检查适合早期调试。最终接受标准应来自适用的工艺和提交规范。硬 IP 的版图、抽象、参考电路及黑盒规则需要使用匹配版本。对于跳过或无法覆盖的对象，明确补充检查及其负责人。

## 典型场景

**教学假设。** 版图用合规形状把两个应独立的网络接到一起。若所跑几何规则未报错，LVS 仍可检测到抽取网络被合并。反过来，如果参考电路已经接错，版图与它匹配仍可通过 LVS。对产品行为应回到规格和功能验证证据。

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="成本视角"></span>

## 上下游接口

上游是版图、工艺规则和参考电路。下游使用检查结果、豁免和校验值判断候选是否可提交。任何晚期改动都需重新确认签核覆盖与候选版本一致。 [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md)

## 后续阅读

- [流片交接](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [静态时序分析](05_static_timing_analysis.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** DRC、LVS 的用途和检查示例见工具及 PDK 文档。
- **教学假设。** 短接示例用于比较两种检查的边界。
- **待项目核实。** 签核规则集、黑盒范围、其他必查项与豁免批准方。
