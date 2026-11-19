# 硅后调试怎样隔离故障

<span class="micro-legacy-anchor" id="post-silicon-debug"></span>

## 前置知识

先按[首硅启动](04_post_silicon_bringup.md)记录样品、板卡、固件和失败条件。

<span class="micro-legacy-anchor" id="决策点"></span>

## 核心概念

硅后调试的输出是可复现的现象、足以排除部分解释的证据，以及可验证的根因或缓解措施。先定位系统边界，再选择合适的寄存器、波形、测试器或失效分析手段。

## Debug Flow

1. 保存原始证据。记录样片、批次、板卡、频率、电压、温度、软件与测试版本。
2. 最小化失败。用能复现的一条事务、一个端口或一种工作模式替换复杂业务。
3. 建立对照。每次改变一个变量，例如交换已知良好的板与样片，或使用两版固件。确认现象跟随哪一项。
4. 按供电、时钟、复位、封装、接口、软件和设计逐层解释。用硅前结果或已知好样品交叉检查。
5. 用明确机理解释观察，验证修复和边界。给出影响范围、适用条件和残余风险。

## Debug 手段

工程固件、状态寄存器、追踪与示波器观察行为。ATE 可复核制造测试、分档或结构诊断。失效分析可用无损或破坏性手段验证物理假设。选择手段前先写出它能区分哪两个解释。 [FAB 失效分析流程](../../FAB/wiki/05-final-test-and-reliability/failure-analysis-flow.md)

<span class="micro-legacy-anchor" id="常见问题类型"></span><span class="micro-legacy-anchor" id="先进节点与成熟节点差异"></span><span class="micro-legacy-anchor" id="常见坑"></span><span class="micro-legacy-anchor" id="创业公司取舍"></span>

## 典型场景

**教学假设。** SRAM 数据正确，偶尔没有 DMA 中断。先比较数据写响应、DMA 完成状态、中断汇聚器状态和软件屏蔽位。若设备状态已完成，而中断汇聚器看不到事件，再检查跨域、目的时钟及复位。若换软件配置即可重现，则测试原配置和恢复方案。温度或频率影响复现只是一条线索，还要用对照实验区分时序裕量、复位、电源和软件竞态。

## Software Workaround 的边界

规避应说明覆盖哪批硅片、哪些状态和工作条件。验证启动、更新、失败恢复、持续性能与用户可见限制。影响规格时更新勘误和验收条件。超过可接受边界时，进入[硅版本修订](08_silicon_revision.md)评审。

<span class="micro-legacy-anchor" id="角色与典型时长"></span><span class="micro-legacy-anchor" id="成本视角"></span>

## 上下游接口

硅后、设计、板卡、测试和软件团队共同复核现象。对物理失效，质量与失效分析团队接收可追溯样品。输出包括复现步骤、因果证据、缓解条件和待查风险。 [OpenTitan 硅后验证结项示例](https://opentitan.org/book/doc/project_governance/project_milestone_definitions.html)

## 后续阅读

- [硅片特性化](06_characterization.md)
- [量产良率分析](07_yield_analysis.md)
- [硅版本修订](08_silicon_revision.md)

<span class="micro-legacy-anchor" id="参考公开来源"></span>

## 内容可信度说明

- **行业做法。** 调试使用分层隔离、对照实验与复验。证据可用性依芯片及实验条件。
- **教学假设。** DMA 中断案例用于说明如何定位哪一段丢了事件。
- **待项目核实。** 实际故障、影响范围、根因与规避条件。
