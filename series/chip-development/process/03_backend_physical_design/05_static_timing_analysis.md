# Static Timing Analysis

## 前置知识

- 建议先读 [Routing](./04_routing.md)。
- 建议理解 [STA](../00_overview/05_glossary.md#sta)、[SDC](../00_overview/05_glossary.md#sdc)、[ECO](../00_overview/05_glossary.md#eco)、[Signoff](../00_overview/05_glossary.md#signoff)。

## 核心概念

Static Timing Analysis，简称 STA，是不用穷举输入向量而检查所有时序路径是否满足 setup/hold 要求的方法。STA 是数字芯片 signoff 的核心。它回答的问题不是“仿真有没有跑过”，而是在给定 PVT corner、mode、clock、寄生、variation 和约束下，信号是否能在正确时间到达寄存器。

STA 的关键输出包括 [WNS/TNS](../00_overview/05_glossary.md#wnstns)、violating paths、setup/hold slack、transition、capacitance、clock uncertainty、SI-aware delay 和 path group QoR。错误的 SDC 会让 STA 结果失真：约束太松会漏 bug，约束太严会浪费面积功耗甚至导致不可收敛。

## 关键活动顺序

1. 建立 [MMMC](../00_overview/05_glossary.md#mmmc)：multiple modes, multiple corners，包括 functional、scan、bist、低功耗模式、不同 [PVT corner](../00_overview/05_glossary.md#pvt-corner)。
2. 审查 SDC：clock、generated clock、IO delay、false path、multi-cycle path、clock groups、case analysis。
3. Pre-layout/placement/CTS/post-route 多阶段 STA，持续跟踪趋势。
4. Post-route extraction 后使用 SPEF 做 signoff STA。
5. 分析 setup violation：逻辑深度、线长、clock skew、cell delay、SI、IR impact。
6. 分析 hold violation：过短路径、clock skew、min delay、OCV。
7. 执行 ECO：cell sizing、buffer、VT swap、route optimization、logic restructuring、pipeline request。
8. LEC/形式等价、incremental STA、power/DRC 回归，直到 closure。
9. 生成 timing signoff package 和 waiver/risk 清单。

## 工具名

主流 STA 工具包括 Synopsys PrimeTime、Cadence Tempus。实现工具内部也有 timing engine，如 Innovus 和 Fusion Compiler/IC Compiler II。寄生抽取来自 StarRC、Quantus 等。ECO 后等价检查使用 Synopsys Formality、Cadence Conformal。

## 角色与典型时长

STA engineer 是核心 owner，physical design engineer、RTL owner、DFT、low-power、IP owner 都参与。Block 级 STA closure 可以数周量级；复杂 SoC 多 mode/corner signoff 可能数月迭代。先进节点 corner/mode/variation 更多，STA 不是后端末尾的一次报告，而是贯穿整个 physical design 的闭环。

## 关键决策点

- Corner/mode 范围：少跑会漏风险，多跑会增加收敛成本。
- Timing exception 是否可信：false path 和 multi-cycle path 必须有设计依据，不能作为“消 violation”的手段。
- 修 setup 还是修 hold：setup 和 hold 经常互相影响，盲目加 buffer 可能修一个坏另一个。
- 是否做 RTL ECO：如果关键路径是结构性问题，应前端修 pipeline，而不是后端硬塞 buffer。
- 是否降低频率：创业公司必须把频率目标和 tapeout 风险放在一起决策。

## 先进节点与 28/16nm 差异

7nm 及以下，STA 需要更复杂的 variation 建模，如 [AOCV/POCV/LVF](../00_overview/05_glossary.md#aocvpocvlvf) 等；寄生、coupling、SI、IR drop、temperature gradient 对 timing 影响更强。先进节点还可能需要更多 PVT corner、mode 和 derate 策略，工具 runtime 和数据管理成本上升。

## SI 与 Noise Signoff

STA 不只检查理想 delay。Post-route 后需要把 crosstalk delta delay 和 noise 纳入 timing signoff。工具会根据 SPEF、coupling capacitance、aggressor switching window 和 victim path 计算 delay 变动；严重时还要检查 glitch/noise 是否可能让静态控制信号、reset、clock gate enable 或异步输入误翻转。

常见修复包括 shielding、加 spacing、降低 slew、buffer insertion、重布线、调整 NDR 或把易受害信号移到更高层金属。修复后必须回归 STA、power 和 DRC。对高带宽 AI 芯片，宽总线的同步切换和 NoC 长线会放大 SI 风险，因此 SI 不能只在最后一次 signoff 才看。

28nm/16nm 项目中，一些 timing 问题可能通过 sizing/buffering 较容易修复。先进节点下 wire delay 和 variation 更主导，逻辑门变快不代表芯片更容易跑高频。长线、跨 macro、跨 block 路径常需要微架构调整。

## 常见坑

- SDC 由前端随手写，后端没有逐条 review。
- 用 false path 掩盖真实跨域或异常路径。
- 只看 WNS，不看 TNS、path distribution 和 violation 类型。
- 忽略 hold，认为 setup 收敛就结束。
- ECO 后不跑 LEC 或不回归 power/DRC。
- IP black box timing model 不完整或版本不一致。
- 没有把 top critical paths 反馈给 RTL/架构团队。

## 上下游接口

STA 上游依赖网表、SDC、library、SPEF、OCV/derate、mode/corner 定义和 clock/power intent。下游影响 ECO、routing、power analysis、signoff 和 tapeout 决策。

STA 对前端反推很强。关键路径如果来自过深组合逻辑、长距离单周期访问、集中仲裁、宽 mux、未分层控制，后端工程师应把 path schematic、物理位置、delay breakdown 反馈给 RTL owner。软件背景创始人应要求团队区分“后端可修 timing”和“架构需改 timing”。

## 创业公司取舍

创业公司第一颗芯片可以降低目标频率换取 closure 确定性。高频目标会显著增加后端迭代、EDA license、工程师时间和 tapeout 风险。若市场允许，选择较保守频率、较宽裕 timing margin、较少 mode/corner 复杂度，通常比极限 PPA 更符合首版芯片目标。

但不能省 STA signoff。即使是 MPW 或 test chip，也要知道哪些路径未约束、哪些 violation 被接受，不能用“只是原型”作为无约束流片的理由。

## 典型场景

Post-route STA 显示 NPU 的 global accumulator path setup violation 严重。Delay breakdown 显示 cell delay 只占少数，大部分来自跨越两个 macro 区域的 interconnect。后端尝试 buffer 和 cell sizing 后改善有限，并引入 hold violation。正确决策是增加 pipeline stage 或改变 accumulator 分层，而不是继续消耗后端时间。这个 STA 结果实际上是在告诉架构团队：当前单周期通信假设不物理。

## 后续阅读

- [Power Analysis](./06_power_analysis.md)
- [DRC/LVS Signoff](./07_drc_lvs_signoff.md)
- [前端综合准备](../02_frontend_design_and_verification/04_synthesis_preparation.md)
- [前端签核标准](../02_frontend_design_and_verification/08_signoff_criteria.md)

## 参考公开来源

- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Cadence Tempus 相关产品页面](https://www.cadence.com/en_US/home/tools/digital-design-and-signoff.html)
- [Synopsys StarRC](https://www.synopsys.com/implementation-and-signoff/signoff/starrc.html)
- J. Bhasker, Rakesh Chadha, *Static Timing Analysis for Nanometer Designs*

## 内容可信度说明

- **公开信息（高可信）**：STA、setup/hold、SDC、MMMC、寄生抽取、PrimeTime/Tempus 工具用途公开可查。
- **行业惯例（中可信）**：timing exception review、ECO closure、AOCV/POCV/LVF 使用策略因节点和公司而异。
- **经验性观察（中低可信）**：AI 芯片长线和集中控制经常导致结构性 timing 问题，需要 RTL/架构反馈。
- **不确定/需向资深工程师确认（低可信）**：具体 signoff corner、derate、uncertainty、OCV 模型和 foundry 要求。
