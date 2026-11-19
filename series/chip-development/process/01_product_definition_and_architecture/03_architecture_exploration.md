# 架构探索怎样比较可实现的方案

<span class="micro-legacy-anchor" id="架构探索"></span>

## 前置知识

先固定[工作负载](01_market_and_workload_analysis.md)与[验收规格](02_spec_definition.md)。

## 架构探索的目标

在同等产品条件下比较候选。输入包括可复现负载、功能规格、PPA 和系统预算、IP 及工艺候选。输出包括带假设的比较、限制所在、估计误差和需要做的验证。将功能参考、性能估计和实际物理实现分别记录。

## 从 Architecture 到 Microarchitecture

架构规格定义软件可见的接口和行为。微架构选择状态、流水线、缓存、队列、银行和仲裁。相同功能可有多个实现。若资源共享、执行重叠或背压影响结果，模型就要写出相关约束。

## 建模层次

| 方法 | 适合回答 | 需要的输入 |
| --- | --- | --- |
| 功能参考 | 结果及边界语义 | 数据、操作、舍入及错误规则 |
| 分析估算 | 带宽、算力或面积下界 | 计算量、搬运量、端口、容量与工作点 |
| 事件或周期模型 | 等待、争用、流水发射与调度 | 依赖、事件定义、队列、仲裁与时钟 |
| 试综合及布局 | 实际库映射、宏位置、时序和拥塞风险 | RTL 原型、库、约束、宏与供电条件 |

闭合模型的方式是用相同假设复算小用例，再用实现报告或测量校准。关键路径、功耗活动、时序与物理条件影响适用范围。 [OpenROAD Flow](https://openroad-flow-scripts.readthedocs.io/en/latest/mainREADME.html) · [微架构的建模验证与校准](../../../interconnect/NOC/08-simulator-construction/verification-and-calibration.md)

## 探索流程

1. 固定工作负载、基线和评价范围。
2. 选择能解释瓶颈的设计变量。例如 SRAM 端口、bank、队列、总线或目标频率。
3. 先估上下界，再用运行模型复查重叠、争用或背压。只比较同一单位、时钟和测试条件下的结果。
4. 对关键路径或宏用代表库和试布局校准。若换工艺或换宏，重新检查。
5. 记录选择、未选候选的理由、估计误差和下一步验证。

<span class="micro-legacy-anchor" id="关键探索维度"></span><span class="micro-legacy-anchor" id="关键决策点"></span><span class="micro-legacy-anchor" id="常见错误"></span><span class="micro-legacy-anchor" id="创业公司视角下的取舍"></span>

## 典型场景

**教学假设。** 把 SDRAM 或主机时延先排除，比较一段 16 B 数据在同组 SRAM 内部搬运的资源下界。每次访问 4 B，需发出 4 次读和 4 次写。若源与目的争用同一单端口 bank，发出 8 次访问至少需要 8 个发射周期。若两边各有独立 bank，每个周期可各发一次，则 8 次访问的资源下界为 4 个发射周期。是否能重叠取决于数据依赖和缓冲。还要计入读延迟、缓冲、地址冲突和尾部写响应，才能得到事务完成时间。 [SRAM 物理端口](../../../storage/02-sram/foundations/single-port-dual-port-multi-port.md)

比较两种方案时，补测 bank 映射、连续负载、拥塞和总面积。用模型结论更新[规格](02_spec_definition.md)和待交付的微架构约束。

## 与上下游接口

系统与软件共同定义负载和观测范围。架构组输出可复现模型、规格及预算。RTL 和物理实现反馈资源开销和无法收敛的约束。验证组复核边界场景，确保采用的结构有可验证的承诺。

## 后续阅读

- [IP 策略](04_ip_strategy.md)
- [工艺节点选择](05_process_node_selection.md)
- [阶段评审与放行证据](06_milestones_and_signoffs.md)

<span class="micro-legacy-anchor" id="工具和基础设施"></span><span class="micro-legacy-anchor" id="角色和典型时长"></span><span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **公开事实。** RTL 到物理实现的工具流和端口机制见引用资料。
- **行业做法。** 模型层次和候选比较按项目预算组织。
- **教学假设。** SRAM 算例只计算端口发射下界，时钟、bank 和访问粒度由题设给定。
- **待项目核实。** 库参数、映射、测试负载的代表性和实际 PPA。
