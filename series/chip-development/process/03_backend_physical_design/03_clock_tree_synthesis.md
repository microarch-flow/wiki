# Clock Tree Synthesis

## 前置知识

- 建议先读 [Placement](./02_placement.md)。
- 建议理解 [CTS](../00_overview/05_glossary.md#cts)、[STA](../00_overview/05_glossary.md#sta)、[IR Drop](../00_overview/05_glossary.md#ir-drop)、[EM](../00_overview/05_glossary.md#em)。

## 核心概念

Clock Tree Synthesis，简称 CTS，是构建时钟分发网络的过程。时钟必须到达大量触发器，同时满足 skew、latency、transition、jitter、OCV、功耗和 EM 约束。时钟网络通常是芯片动态功耗的重要来源，也是时序收敛的核心对象。

软件背景容易低估时钟。软件中的“顺序执行”由 CPU 保证，RTL 中每个寄存器都依赖真实时钟边沿。时钟到达不同寄存器的时间差会直接改变 setup/hold margin。CTS 做不好，功能正确的逻辑也会在硅上失败。

## 关键活动顺序

1. 清理 placement 后设计，确认 clock definitions、generated clocks、clock groups、exceptions。
2. 定义 CTS constraints：目标 skew、latency、transition、buffer/inverter 类型、NDR、shielding、clock gating cell。
3. 规划 clock topology：tree、mesh、H-tree、hybrid、局部 clock spine。
4. 插入 clock buffers/inverters，连接 clock gating 和 sinks。
5. post-CTS optimization：修 setup/hold、调整 skew、修 transition/capacitance。
6. 检查 clock power、clock routing congestion、IR/EM 风险。
7. 与 STA/power/routing 迭代，生成 post-CTS checkpoint。
8. 对特殊 clock domain、test clock、scan clock、PLL 输出和 low-power clock 做专项 review。

## 工具名

CTS 通常在 Cadence Innovus、Synopsys IC Compiler II/Fusion Compiler、Siemens Aprisa 中完成。时序签核用 PrimeTime 或 Tempus。功耗和电源完整性分析使用 Voltus、RedHawk-SC、PrimePower 等。clock gating 相关检查可能涉及 SpyGlass、VC LP、Conformal Low Power 等前端/低功耗工具。

## 角色与典型时长

CTS owner 是 physical design engineer，STA engineer 必须深度参与。低功耗 engineer、DFT engineer、RTL owner 也要参与 clock gating、test clock 和 generated clock 审查。中等复杂 block 的 CTS 可以数天到数周；复杂 SoC、多 clock domain、多 power domain 或高频 AI 芯片可能需要多轮数周以上迭代。

## 关键决策点

- Skew 目标：skew 越小不一定越好，过度追求低 skew 会增加 buffer、功耗和 routing 压力。
- Latency 分布：过大 latency 影响 timing budget 和 clock uncertainty。
- Clock gating 粒度：细粒度 gating 省功耗，但增加控制复杂度、CTS 负担和验证风险。
- Clock topology：clock mesh 更鲁棒但功耗和面积高；tree 更省资源但对 variation 更敏感。
- Useful skew：可用于修 setup，但可能恶化 hold，并增加 signoff 复杂度。

## 先进节点与 28/16nm 差异

7nm 及以下节点中，工艺变异、线阻、via resistance、电源噪声和 clock power 更突出。CTS 需要更强的 OCV/AOCV/POCV 建模，更谨慎的 clock routing layer 选择和 shielding，更早的 IR-aware timing 分析。

相比 28nm，先进节点的 hold closure 常更棘手，因为数据路径和 clock path 变异建模更复杂。时钟树本身也会显著影响局部电源噪声，AI 芯片大规模同步切换时尤其明显。

## 常见坑

- SDC 中 generated clock 或 clock group 定义错误，导致 CTS 和 STA 基于错误前提。
- 异步/测试/scan clock 没有完整约束。
- Clock gating cell 插入不规范，造成 glitch 或 test mode 问题。
- 过度 buffer 导致 clock power 超预算。
- 只看 skew，不看 clock tree 对 IR/EM 和 routing 的影响。
- 后期才发现 PLL/clock mux/test clock 结构不符合 DFT 或 low-power 要求。
- 用普通数据信号方式处理 clock，导致 routing 和 SI 风险。

## 上下游接口

CTS 上游依赖 placement、clock/reset 规格、SDC、UPF、DFT test mode 和 PLL/clock controller 设计。下游影响 routing、STA、power analysis、IR/EM 和 ECO。

CTS 也会反推前端。如果 clock domain 太多、generated clock 关系复杂、clock gating 过度细碎、test clock 结构不清，后端会要求 RTL/DFT/低功耗重构。对“快速迭代”团队，clock 结构必须模板化和规范化，不能让 agent 随意生成局部 clock mux 或 gated clock。

## 创业公司取舍

创业公司第一颗芯片应减少 clock domain 数量，避免过度复杂的 DVFS 和局部异步结构。省功耗固然重要，但 clock/power domain 复杂度会迅速放大 CDC、STA、DFT、UPF 和后端风险。

可以选择保守频率、清晰 clock architecture、成熟 clock gating policy。不要为了宣传峰值频率把 CTS 推到极限，因为后续 routing、IR drop 和 silicon variation 可能让这个频率无法量产。

## 典型场景

一个 AI accelerator 为每个 tile 生成本地 clock gating，并支持多个低功耗模式。前端仿真通过，但 CTS 时发现 clock gating enable 来自跨域控制，test mode 下部分 clock 不可控，generated clock 约束不完整。修复需要重构 clock controller，定义统一 test bypass、同步 enable、更新 UPF 和 CDC waiver。这个问题如果在 CTS 后期才发现，会比前端阶段修复贵得多。

## 后续阅读

- [Routing](./04_routing.md)
- [Static Timing Analysis](./05_static_timing_analysis.md)
- [Power Analysis](./06_power_analysis.md)
- [前端 CDC/RDC](../02_frontend_design_and_verification/06_cdc_and_rdc.md)

## 参考公开来源

- [Synopsys IC Compiler II](https://www.synopsys.com/implementation-and-signoff/physical-implementation/ic-compiler.html)
- [Cadence Innovus Implementation System](https://www.cadence.com/en_US/home/resources/datasheets/innovus-implementation-system-ds.html)
- [Synopsys PrimeTime](https://www.synopsys.com/implementation-and-signoff/signoff/primetime.html)
- [Cadence Voltus](https://www.cadence.com/en_US/home/resources/datasheets/voltus-ic-power-integrity-solution-gt-ds.html)

## 内容可信度说明

- **公开信息（高可信）**：CTS、skew、latency、clock power、post-CTS optimization 属于公开数字后端流程。
- **行业惯例（中可信）**：clock topology、useful skew、clock gating、test clock review 的策略因项目和工具而异。
- **经验性观察（中低可信）**：创业公司应减少 clock domain 和 DVFS 复杂度，优先保证可签核。
- **不确定/需向资深工程师确认（低可信）**：具体 skew/latency 目标、clock mesh 使用条件、OCV 模型和 foundry signoff 要求。
