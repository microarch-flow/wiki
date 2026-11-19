# 第一颗芯片应该验证什么

<span class="micro-legacy-anchor" id="first-chip-pragmatics第一颗芯片的务实建议"></span>

## 第一颗芯片的正确问题

先选一个结果能改变下一步决策的问题。例如，目标是验证架构行为、硅上工作点，还是交付给一组客户。三个目标需要不同的样品、可观测性、供应和验证证据。

## Scope 控制

| 目标 | 所需证据 | 可考虑的载体 |
| --- | --- | --- |
| 验证功能和软件接口 | 可重复测试、时序及资源假设 | 模型、仿真、FPGA 或仿真加速 |
| 验证物理实现 | 指定工艺和测试条件的测量 | 代表性 test chip 或 MPW |
| 交付产品 | 按合同完成工作范围、试产、资格鉴定、供货与支持 | 面向生产的器件与封装 |

列出每个新接口、新工艺、新 IP 和新封装的风险。若首版同时引入多个未知因素，增加能够分别通过和分别出错的观测。将客户结果和工程学习结果各自写入目标。

<span class="micro-legacy-anchor" id="常见坑"></span>

## 决策门禁

1. 确定可以检验的交付目标和停止条件。
2. 选节点、IP、封装和软件边界，检查可获取选项。
3. 证明试验或产品能被驱动、观察和追溯。
4. 对首次制造、失败定位及需要再迭代的投入分别估算。
5. 记录通过条件、供应商和评审人。 [芯片项目成本结构](../00_overview/03_cost_structure.md) · [MPW 多项目晶圆策略](../06_cross_cutting_topics/04_mpw_shuttle_strategy.md)

<span class="micro-legacy-anchor" id="前置知识"></span><span class="micro-legacy-anchor" id="节点选择"></span><span class="micro-legacy-anchor" id="ip-策略"></span><span class="micro-legacy-anchor" id="验证策略"></span><span class="micro-legacy-anchor" id="硅后和软件准备"></span><span class="micro-legacy-anchor" id="客户策略"></span><span class="micro-legacy-anchor" id="典型-v1-策略"></span><span class="micro-legacy-anchor" id="后续阅读"></span>

## 典型场景

**教学假设。** 先做 SRAM＋DMA 试片，验证时钟、存储访问和完成事件，并测量指定条件下的工作范围。系统级 HBM、多事务和量产质量另有验证条件。将实际结果与原规格对照，再决定是否扩大规模。

## 参考公开来源

- [TSMC 共享掩模原型服务](https://www.tsmc.com/english/dedicatedFoundry/services/cyberShuttle)
- [ChipFoundry chipIgnite](https://chipfoundry.io/chipignite)

<span class="micro-legacy-anchor" id="成本模型"></span>

## 内容可信度说明

- **工程建议。** 首版范围由目标、可观测性、成本与供应条件共同决定。
- **教学假设。** 试片案例用于比较能取得的证据。
- **待项目核实。** 工艺、预算、供应、软件与客户验收条件。
