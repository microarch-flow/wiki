# 01_product_definition_and_architecture：产品定义与架构

## 前置知识

- 建议先读 [完整芯片生命周期总览](../00_overview/01_full_lifecycle.md)。
- 建议先读 [角色和团队职责](../00_overview/02_roles_and_teams.md)。
- 涉及成本判断时，配合 [芯片项目成本结构总览](../00_overview/03_cost_structure.md) 阅读。

## 本目录的作用

本目录覆盖芯片项目最早、也最容易被软件背景创始人低估的阶段：从市场假设、真实 workload、产品规格、架构探索、IP 策略、工艺节点选择，到规格冻结和阶段签核。

在芯片项目里，产品定义不是写一份 [PRD](../00_overview/05_glossary.md#prd) 就结束。它会直接约束 [Architecture](../00_overview/05_glossary.md#architecture)、[PPA](../00_overview/05_glossary.md#ppa)、[IP](../00_overview/05_glossary.md#ip)、封装、软件栈、验证计划、后端实现难度和最终 [NRE](../00_overview/05_glossary.md#nre)。早期一个模糊指标，例如“支持大模型推理”“高 [TOPS](../00_overview/05_glossary.md#tops)”“低功耗”，如果没有落到模型集合、batch size、数据精度、内存带宽、延迟、板级功耗和软件接口，后续团队会在 [RTL](../00_overview/05_glossary.md#rtl)、验证、后端和硅后阶段反复补定义。

对 AI 芯片创业公司来说，本目录的核心问题不是“能不能设计出一个很强的架构”，而是“能不能用有限资金定义一颗足够可制造、可验证、可卖、可迭代的第一颗芯片”。

## 文件索引

- [01_market_and_workload_analysis.md](./01_market_and_workload_analysis.md)：如何从市场、客户、模型和 workload 反推芯片需求。
- [02_spec_definition.md](./02_spec_definition.md)：如何把产品目标写成可执行、可验证、可签核的芯片规格。
- [03_architecture_exploration.md](./03_architecture_exploration.md)：如何用模型、仿真和设计空间搜索做架构取舍。
- [04_ip_strategy.md](./04_ip_strategy.md)：哪些 IP 适合买，哪些必须自研，授权模式和集成风险是什么。
- [05_process_node_selection.md](./05_process_node_selection.md)：如何选择 7nm 及以下先进节点，何时应考虑 16nm/28nm。
- [06_milestones_and_signoffs.md](./06_milestones_and_signoffs.md)：从概念到规格冻结的里程碑、评审和交付物。

## 产品定义阶段主流程

```mermaid
flowchart LR
  A[市场与客户场景] --> B[Workload 分析]
  B --> C[产品指标草案]
  C --> D[架构探索]
  D --> E[IP 与工艺节点策略]
  E --> F[成本和进度模型]
  F --> G[规格冻结]
  G --> H[微架构/RTL/验证计划]
```

这个流程不是一次性线性流程。市场输入会修正架构假设，架构探索会暴露产品目标是否过高，IP 和工艺节点选择会改变成本结构，成本结构又会影响融资节奏和产品定位。优秀团队会在早期快速循环几轮，但不会无限循环。进入大规模 RTL 设计前，必须把关键不确定性收敛到可管理范围。

## 关键输出物

| 输出物 | 主要责任人 | 下游消费者 | 为什么重要 |
|---|---|---|---|
| 市场和客户场景假设 | CEO、产品、BD、系统架构 | 架构、软件、融资 | 决定芯片解决什么问题 |
| Workload 集合和 trace | 架构、编译器、应用工程 | 架构探索、验证、benchmark | 防止用错误模型优化芯片 |
| 产品需求规格 PRD | 产品、系统架构 | 架构、软件、销售 | 定义客户可感知指标 |
| 芯片架构规格 | 架构负责人 | 微架构、RTL、验证、编译器 | 定义硬件和软件契约 |
| IP 采购/自研清单 | 架构、SoC、商务、法务 | 集成、验证、后端、财务 | 影响成本、风险和排期 |
| 工艺节点和封装建议 | 架构、后端、供应链、财务 | 后端、封装、融资 | 决定 PPA 上限和 NRE 下限 |
| 规格签核包 | 项目负责人、各技术负责人 | 全项目 | 作为进入执行阶段的边界 |

## 对软件背景创始人的特别提醒

软件产品可以先做粗糙版本上线，再通过监控、A/B test 和快速发布修正。芯片也可以做版本迭代，但迭代粒度不同。你可以快速迭代模型、编译器、仿真器、RTL 生成器和验证环境；你不能快速迭代 [Mask Cost](../00_overview/05_glossary.md#mask-cost)、晶圆制造周期、封装排期、可靠性认证和客户硬件导入。

你的 C/C++ 架构模型很重要，但它不是产品定义的终点。模型必须回答工程问题：哪些 workload 代表目标市场，哪些算子必须在硬件上高效支持，内存层级是否匹配真实数据流，稀疏、量化和动态 shape 是否会破坏利用率，软件栈是否能把模型映射到硬件，以及哪些 corner case 必须在规格里写清楚。

一个常见错误是把“我能自动生成 RTL”当作产品定义优势。自动生成只能加速从架构描述到实现候选的路径，不能替你决定客户是否愿意买、接口是否可生态化、IP 是否能授权、工艺是否排得上、验证是否足够、封装是否能供货。

## 典型场景

假设团队计划做一颗面向边缘服务器的开源 AI 推理芯片。最初愿景是“支持 Transformer 推理，能效高于 GPU”。如果直接开始写矩阵乘阵列和片上 SRAM，很快会陷入无效探索：不知道目标 batch size，不知道模型是 LLM、推荐、视觉还是多模态，不知道客户更关心吞吐、延迟、TCO 还是可编程性，不知道 PCIe、DDR、HBM、以太网接口是否必要，也不知道第一颗芯片是否能承担先进封装风险。

更稳妥的流程是先定义 5 到 10 个代表性 [Workload](../00_overview/05_glossary.md#workload)，例如小 batch LLM decode、prefill、embedding-heavy 推荐模型、视觉 encoder、混合精度算子。然后建立软件可运行的模型和 trace，估计 compute、memory bandwidth、activation footprint、weight reuse、host-device traffic。架构团队用这些输入比较 systolic array、SIMD、tensor core、near-memory buffer、片上 [NoC](../00_overview/05_glossary.md#noc) 和外部内存方案。商务和供应链同步评估工艺节点、IP 授权、封装、foundry 可获得性和预算。

最后团队可能发现，第一颗芯片不应该追求最大 TOPS，而应选择一个验证边界清晰、软件栈能闭环、封装风险可控、能展示差异化的目标。这个结论比“更大的阵列”更有商业价值。

## 后续阅读

- [01_market_and_workload_analysis.md](./01_market_and_workload_analysis.md)
- [02_spec_definition.md](./02_spec_definition.md)
- [03_architecture_exploration.md](./03_architecture_exploration.md)
- [04_ip_strategy.md](./04_ip_strategy.md)
- [05_process_node_selection.md](./05_process_node_selection.md)
- [06_milestones_and_signoffs.md](./06_milestones_and_signoffs.md)

## 参考公开来源

- [RISC-V International Ratified Specifications](https://riscv.org/specifications/ratified/)
- [TSMC Open Innovation Platform](https://www.tsmc.com/english/dedicatedFoundry/oip)
- [UCIe Consortium Specifications](https://www.uciexpress.org/specifications)
- [PCI-SIG PCI Express Specifications](https://pcisig.com/specifications)

## 内容可信度说明

- **公开信息（高可信）**：芯片早期阶段需要产品定义、架构探索、IP 策略、工艺选择和规格冻结；RISC-V、PCIe、UCIe 等公开标准对接口和生态有约束。
- **行业惯例（中可信）**：PRD、架构规格、IP 清单、工艺选择建议和 signoff package 的组织方式；AI 芯片以 workload trace 驱动架构探索的做法。
- **经验性观察（中低可信）**：软件背景创始人容易过度相信自动生成 RTL、低估规格冻结和验证成本；第一颗芯片应优先控制验证和供应链风险。
- **不确定/需向资深工程师确认（低可信）**：具体 foundry 支持策略、商业报价、IP vendor 条款、先进封装可获得性、不同客户对 benchmark 的实际接受标准。
