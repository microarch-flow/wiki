# 产品定义与架构探索

<span class="micro-legacy-anchor" id="01_product_definition_and_architecture产品定义与架构"></span>产品团队定义目标问题和验收条件。架构团队据此比较计算、存储、互连、软件与封装方案。第一版规格形成后，仍需根据模型、IP 可用性和物理实现反馈迭代。

<span class="micro-legacy-anchor" id="前置知识"></span>

## 本目录的作用

从可复现负载出发，得到可测试的规格与工程基线。输出至少包含需求、必要的接口约定、候选与取舍、估算条件、关键 IP 依赖和风险。验证、软件、物理实现、封装和测试团队共同评审他们接收的输入。

<span class="micro-legacy-anchor" id="文件索引"></span><span class="micro-legacy-anchor" id="产品定义阶段主流程"></span><span class="micro-legacy-anchor" id="关键输出物"></span><span class="micro-legacy-anchor" id="对软件背景创始人的特别提醒"></span><span class="micro-legacy-anchor" id="典型场景"></span><span class="micro-legacy-anchor" id="后续阅读"></span>

## 阅读顺序

1. [工作负载与目标场景](01_market_and_workload_analysis.md)固定输入和测量方法。
2. [规格定义](02_spec_definition.md)明确什么条件算通过。
3. [架构探索](03_architecture_exploration.md)比较候选并用早期实现校准假设。
4. [IP 策略](04_ip_strategy.md)核对交付视图、授权和集成风险。
5. [工艺节点选择](05_process_node_selection.md)评估 PPA、配套库、封装与可获供给。
6. [阶段评审与放行证据](06_milestones_and_signoffs.md)把上述交付物纳入可评审基线。

读到制造侧输入时，可进一步查[工艺规则与 PDK](../../FAB/wiki/02-front-end-fabrication/design-rule-and-pdk.md)和[项目封装交接](../04_tapeout_and_post_silicon/03_packaging.md)。

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 这里提供按问题组织的设计路线。各活动可以并行，基线冻结与重开方式以项目约定为准。
- **待项目核实。** 产品的实际负载、验收要求、候选节点和供应合同。
