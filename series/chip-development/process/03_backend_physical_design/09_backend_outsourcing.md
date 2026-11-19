# 后端外包怎样验收交付

<span class="micro-legacy-anchor" id="backend-outsourcing"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

后端外包交付的是有版本的实现与证据。项目方负责定义输入、接口、接收指标和风险接受。服务商按约定负责实现、分析和问题整改。明确第三方 IP、工艺文件及工具权限可怎样使用。

<span class="micro-legacy-anchor" id="不应完全外包的部分"></span>

## 可以外包的部分

根据合同约定，服务可覆盖综合、布局、布线、时序、IR／EM、物理验证、DFT、测试或流片接口。每项明确责任人、依赖、工具配置、产出、复验流程及交付形式。 [TSMC 设计服务生态](https://www.tsmc.com/english/dedicatedFoundry/oip)

<span class="micro-legacy-anchor" id="工具名"></span><span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="成本与合同量级"></span><span class="micro-legacy-anchor" id="上下游接口"></span>

## 关键活动顺序

1. 定义目标工艺、签核范围、时钟、功耗、I/O、封装边界和责任。
2. 为初次合作选择代表子系统，验证工具／规则版本、宏、时钟及数据交接。
3. 按阶段评审输入、尝试和结果。保存候选版本、脚本、报告和需要审批的例外。
4. 验收最终交付时核对版图和报告、时序例外、已批准豁免及重现方式。
5. 约定量产前后支持、改动审批、追加工作和硅后问题的追踪。

<span class="micro-legacy-anchor" id="先进节点与-2816nm-差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 关键决策点

若服务商对 PPA 或期限作承诺，记录对应的网表、时序、模式和角落。IP 和需求变化时确定哪些工作重来、谁承担成本。费用与回归、工具和供给条件一同评估。 [芯片项目成本结构](../00_overview/03_cost_structure.md)

## 典型场景

**教学假设。** 试实现报告称时序通过。项目方复核发现一个测试时钟未分析。在接受之前补齐约束并约定重跑范围。对设计方无法直接读取的材料，预先约定可查看的签核和保密交接方式。

## 后续阅读

- [物理设计与签核](README.md)
- [设计服务与 Turnkey](../06_cross_cutting_topics/05_turnkey_services.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 清单为合同与技术验收的组织示例。
- **教学假设。** 测试时钟的例子用于说明报告范围。
- **待项目核实。** 工具、资料授权、接收阈值、交付时间、价格与责任。
