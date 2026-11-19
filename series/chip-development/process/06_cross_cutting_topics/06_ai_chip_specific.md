# AI 芯片的工作负载怎样约束实现

<span class="micro-legacy-anchor" id="ai-chip-specificai-芯片特有考虑"></span><span class="micro-legacy-anchor" id="前置知识"></span>

## 核心概念

AI 芯片的产品指标依赖模型、输入形状、并发、精度、软件和测量边界。架构团队需要把这些指标落实到计算、存储、搬运、封装与测试。峰值算力和原始内存带宽可以解释上界，实际吞吐和延迟还要用目标负载验证。 [MLCommons 数据中心推理基准](https://mlcommons.org/benchmarks/inference-datacenter/)

## 关键活动顺序

1. 定义模型、版本、精度要求、输入分布、并发和测量范围。通过条件包含必要的质量或正确性要求。
2. 让编译器与运行时团队确认映射、访存、异常和数据格式。验证结果与软件配置一起留档。
3. 估算计算、SRAM、内存带宽、片上互连和主机接口的需求，找出主限制。
4. 将内存、封装、供电、散热和制造测试能力纳入候选评审。
5. 在硅后用与待发表数字一致的条件测量，并在试产验证可复现范围。

<span class="micro-legacy-anchor" id="创业公司取舍"></span><span class="micro-legacy-anchor" id="常见坑"></span>

## 关键决策点

比较专用数据通路和可编程资源时，固定同一负载及精度，查工作集、访存、映射效率和实现代价。若选择 HBM，区分器件接口峰值、系统可达带宽、封装和供给条件。跨芯片和多设备扩展还需目标协议、平台、软件与验证。 [存储系统选型](../../../storage/06-system-integration/README.md) · [FAB HBM 制造与集成](../../FAB/wiki/04-back-end-packaging/hbm-as-case-study/README.md)

## 典型场景

**教学假设。** 同一模型在小批解码下测出外存受限。增加算力后，要先检查权重、KV 和数据通路是否仍占据瓶颈。记录有效吞吐、请求延迟、准确率和功耗测量点。若增加带宽或复用数据的方案更能改变结果，继续验证它的布局、热边界和成本。 [推理运行时系列](../../../inference-runtime/README.md)

<span class="micro-legacy-anchor" id="工具和基础设施"></span><span class="micro-legacy-anchor" id="角色周期和成本"></span>

## 上下游接口

上游提供工作负载、接收指标和软件约定。下游得到带宽与功率预算、有效配置、运行时和验证用例。封测及硅后给出工作范围、质量和实际性能，反向校准模型。

## 后续阅读

- [工作负载与目标场景](../01_product_definition_and_architecture/01_market_and_workload_analysis.md)
- [工艺节点选择](../01_product_definition_and_architecture/05_process_node_selection.md)
- [功耗、压降与电迁移](../03_backend_physical_design/06_power_analysis.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** MLCommons 公布了特定场景、规则和结果。接口及封装信息以对应产品和平台为准。
- **行业做法。** 分阶段校准与系统验证由项目目标决定。
- **教学假设。** 小批解码瓶颈仅为说明因果的设定。
- **待项目核实。** 客户负载、目标质量、延迟、带宽、持续功耗、良率及供给。
