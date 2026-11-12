# 前端签核标准

## 前置知识

- 建议先读本目录所有前序文件。
- 建议先读 [里程碑与签核](../01_product_definition_and_architecture/06_milestones_and_signoffs.md)。
- 建议理解 [Signoff](../00_overview/05_glossary.md#signoff)、[ECO](../00_overview/05_glossary.md#eco)、[Synthesis](../00_overview/05_glossary.md#synthesis)、[CDC](../00_overview/05_glossary.md#cdc)、[DFT](../00_overview/05_glossary.md#dft)。

## Signoff 的含义

[Signoff](../00_overview/05_glossary.md#signoff) 不是“没有 bug”，而是团队基于证据决定风险足够低，可以进入下一阶段。前端 signoff 的目的，是让后端物理设计接收一套稳定、可综合、可约束、可测、可验证的 RTL 和约束包。

如果前端 signoff 只看“仿真回归通过”，后端会被迫处理本该前端解决的问题：约束缺失、clock/reset 不清、CDC waiver 无证据、DFT 插入失败、UPF 不一致、面积爆炸、关键路径不可修。

## 前端 Signoff Checklist

| 类别 | 最低证据 |
|---|---|
| 规格 | 架构/微架构规格冻结，变更记录清楚 |
| RTL | lint clean 或 waiver 有 owner 和理由 |
| 验证 | regression pass，coverage closure，有未关闭 bug 列表 |
| Assertion/Formal | 关键协议和状态机有 assertion/formal 证据 |
| CDC/RDC | 工具报告关闭，waiver 有结构和验证证据 |
| 综合 | early synthesis 达到可接受 QoR，无严重 unconstrained path |
| SDC | clock、generated clock、IO、exception 被 review |
| DFT | scan/MBIST/test mode plan 通过 DFT review |
| Low Power | UPF/power state/clock gating 检查通过 |
| LEC | RTL-to-netlist LEC 流程可运行或风险明确 |
| 软件接口 | register model、header、文档和 RTL 一致 |
| 后端接口 | macro、floorplan 假设、timing budget、physical constraint 交付 |
| 风险 | risk register 更新，waiver 和 residual risk 被接受 |

不同公司会有更细模板，但这些类别不应缺失。

## Bug 和 Waiver 管理

进入前端 signoff 前，应冻结严重 bug。Bug 应按 severity 分类：功能错误、数据损坏、死锁、可恢复错误、性能问题、文档问题。对硬件来说，“低概率死锁”通常不是低优先级，因为硅后可能无法修复。

Waiver 必须包含违反了哪条规则、为什么不是 bug、哪个规格或结构证明它安全、哪个测试/assertion/formal 或人工分析覆盖它、owner 和到期条件、如果后续 RTL 变化是否需要重新审查。没有证据的 waiver 应视为未关闭 bug。

## 进入后端的交付包

前端交给后端的不是单个 RTL tarball，而是一套 package：

- RTL file list、版本 tag、编译 define、参数配置。
- Top-level integration 说明。
- SDC 初版和约束说明。
- UPF/CPF 和 power state 说明。
- DFT constraint、test mode、scan/MBIST plan。
- Memory macro list、black box model、LEF/lib/db。
- IP deliverable 和版本。
- CDC/RDC/lint/verification/synthesis 报告。
- Timing/area/power early estimate。
- Known issue、waiver、risk register。
- Register model、软件 header、firmware boot requirement。
- ECO 流程和变更冻结规则。

后端团队必须能复现前端 build。不可复现的交付包会让每个问题都变成环境争议。

## 典型时长和节奏

前端 signoff 不是最后一周完成的活动，而是 RTL 开发期间持续收敛。Block-level 可以每周或每两周设小 gate；subsystem-level 在功能集成后设较硬 gate；SoC-level signoff 通常需要多轮 regression、CDC/RDC、综合、DFT 和低功耗报告闭合。具体时长因项目规模差异很大，不应承诺固定数字。

先进节点项目通常更早引入后端 feedback，因为频率、功耗、macro 和拥塞风险更高。成熟节点或小 test chip 可以轻量一些，但不能省掉基本静态检查和验证证据。

## 与 ECO 和 Agent 工作流的关系

[ECO](../00_overview/05_glossary.md#eco) 是后期工程修改。前端 signoff 后仍可能有 ECO，但应有变更控制。每个 ECO 要评估功能、验证、综合、LEC、STA、CDC/RDC、DFT、UPF 和软件影响。常见错误是把 signoff 后的 RTL 修改当作普通软件 patch。越靠近 tapeout，越要限制修改范围，并要求明确证据。

如果 RTL 由 agent 或 generator 产生，signoff 还要增加生成源、prompt、模型版本、generator commit 可追溯；生成 RTL 与规格需求有映射；禁止 signoff 后手改生成结果而不回灌；生成器本身有 regression suite；对关键模板有人工审核和 formal/仿真证据；对随机生成差异有稳定性检查。否则你签核的是一次偶然输出，而不是可维护设计。

## 典型场景

项目准备交给后端。RTL regression 通过，但 CDC 报告有 300 个 waiver，很多写着“known safe”。综合报告有 50 条 unconstrained path，理由是“后端会处理”。DFT 还没插 scan，只是“预计没问题”。这种状态不应 signoff。

正确处理方式是把 waiver 分类，删除无效 waiver；补 clock/reset 约束；对标准同步器建立 waiver 模板；对真实跨域 bug 修 RTL；让 DFT 跑一次 rule check；让综合和 STA owner review unconstrained path。可能会晚两周，但比后端进行一半发现结构性问题便宜得多。

## 创业公司视角

创业公司可以采用轻量 signoff，但不能采用口头 signoff。建议每个 gate 用一页 dashboard：版本、工具、报告路径、pass/fail、waiver 数量、严重 bug、风险接受人。创始人不需要看每条 timing path，但必须知道哪些风险被接受，为什么接受，后果是什么。

如果资金不足以覆盖后端和一次合理 respin，前端 signoff 标准应更严格，而不是更宽松。因为你没有成本空间把前端遗漏留到硅后修。

## 后续阅读

- [后端物理设计总览](../03_backend_physical_design/README.md)
- [静态时序分析](../03_backend_physical_design/05_static_timing_analysis.md)
- [Tapeout 流程](../04_tapeout_and_post_silicon/01_tapeout_process.md)
- [硅后调试](../04_tapeout_and_post_silicon/05_post_silicon_debug.md)

## 参考公开来源

- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Synopsys Formality](https://www.synopsys.com/implementation-and-signoff/signoff/formality-equivalence-checking.html)
- [Cadence Conformal Equivalence Checker](https://www.cadence.com/ja_JP/home/tools/digital-design-and-signoff/logic-equivalence-checking/conformal-equivalence-checker.html)
- [Synopsys VC LP](https://www.synopsys.com/verification/static-and-formal-verification/vc-lp.html)
- [Accellera Standards](https://accellera.com/downloads/standards)

## 内容可信度说明

- **公开信息（高可信）**：STA、LEC、UPF、CDC、DFT、lint 等工具和标准类别公开可查；PrimeTime、Formality、Conformal、VC LP 等工具用途公开。
- **行业惯例（中可信）**：前端 signoff package、waiver 管理、risk register、RTL freeze、ECO control、后端 handoff 是主流 ASIC 项目实践。
- **经验性观察（中低可信）**：创业公司应使用轻量但硬约束的 dashboard；agent/generator 输出需要版本和生成源可追溯。
- **不确定/需向资深工程师确认（低可信）**：具体 pass/fail 阈值、coverage 目标、waiver 审批层级、ECO 流程和后端接收标准需按团队和 foundry/EDA 流程确认。
