# 前端验证方法学

## 前置知识

- 建议先读 [RTL 设计工程实践](./01_rtl_design_practices.md)。
- 建议先读 [微架构设计](./02_microarchitecture_design.md)。
- 建议理解 [UVM](../00_overview/05_glossary.md#uvm)、[Formal Verification](../00_overview/05_glossary.md#formal-verification)、[Emulation](../00_overview/05_glossary.md#emulation)、[Golden Model](../00_overview/05_glossary.md#golden-model)。

## 验证不是“跑几个 test”

芯片验证的目标是用可审计证据说明设计满足规格，并把剩余风险控制在可接受范围内。仿真通过几个典型 workload 只能说明 happy path 工作，不能说明 reset、异常、backpressure、并发、跨域、低功耗、非法配置和边界条件正确。

验证计划应从规格出发，而不是从 RTL 出发。每条架构和微架构需求都要映射到 test、assertion、formal property、coverage point 或人工 review。没有映射的需求就是未验证需求。

## 验证层次

| 层次 | 目标 | 常用方法 |
|---|---|---|
| Block-level | 单模块功能和协议 | directed test、random test、assertion、formal |
| Subsystem | 多模块交互 | UVM env、scoreboard、coverage、stress test |
| SoC-level | 软件可见行为和系统集成 | C test、firmware test、VIP、emulation |
| Gate-level | 综合后结构检查 | gate simulation、SDF、LEC、X 检查 |
| Pre-silicon software | boot、driver、runtime | emulation、FPGA prototype、virtual platform |

创业公司最容易低估 subsystem 验证。单个模块都正确，不代表 DMA、NoC、NPU、register block、interrupt 和 firmware 组合后正确。

## Golden Model 的边界

[Golden Model](../00_overview/05_glossary.md#golden-model) 可以是 C/C++、Python、SystemC 或高层模型。它用于判断 RTL 输出是否符合预期。关键是 golden model 必须定义精度、舍入、异常、未定义行为和时序无关行为。

对 AI 芯片，常见争议包括 INT8/FP16/BF16 的舍入和饱和规则，NaN、Inf、denormal、overflow 的处理，不同 tiling 顺序导致的累加误差，稀疏或动态 shape 的无效元素处理，以及非法配置下是报错、忽略还是行为未定义。如果 golden model 没定义这些，验证失败时会变成“RTL 错还是模型错”的争论。

## UVM、Assertion 和 Formal

[UVM](../00_overview/05_glossary.md#uvm) 是构建可复用 SystemVerilog 验证环境的方法学。典型组件包括 driver、monitor、sequencer、agent、scoreboard、coverage collector 和 virtual sequence。UVM 的价值在复杂协议、随机刺激、可复用环境和覆盖率收敛。

UVM 不是质量保证本身。一个结构复杂但 test plan 很弱的 UVM 环境仍然会漏 bug。创业公司可以在小模块使用轻量 testbench、cocotb、Verilator 或 C++ harness，但在复杂 SoC 子系统、标准协议和可复用 VIP 上，成熟 UVM 环境仍有价值。

Assertion 用于把协议和不变量写成机器可检查规则。它可以在仿真中触发，也可以交给 [Formal Verification](../00_overview/05_glossary.md#formal-verification) 工具证明。适合 formal 的问题包括 FIFO 不溢出不读空、握手 payload 稳定、仲裁公平性、寄存器访问权限、死锁局部证明和协议状态机。Formal 不是万能证明器，大规模 datapath、复杂存储系统和完整 SoC 通常难以一次性证明。

## Coverage 和回归

Coverage 分为 code coverage、functional coverage、assertion coverage 和 requirements coverage。Code coverage 高不代表功能验证充分，只说明代码被执行过。Functional coverage 才表达“我们关心的场景是否被覆盖”。

对 AI 芯片，coverage 应覆盖 shape、tile size、stride、padding、precision、buffer 满空、backpressure、DMA 边界、中断、错误、timeout、reset during operation、多 master 并发访问、低功耗状态切换和软件配置寄存器组合。Coverage closure 不是追求 100% 数字，而是解释未覆盖点为什么可接受。

回归系统要可复现：记录 RTL commit、test seed、工具版本、编译参数、模型版本和失败波形。随机测试发现的问题如果无法复现，会拖慢整个项目。

## Emulation 和 FPGA Prototype

[Emulation](../00_overview/05_glossary.md#emulation) 使用专用硬件加速大规模 RTL 运行，适合 SoC 级软件 bring-up、长场景、性能分析和复杂并发。常见商业平台包括 Cadence Palladium、Synopsys ZeBu、Siemens Veloce。FPGA prototype 成本可能较低，但映射、时钟、memory 和调试可见性会带来额外工作。

Emulation 不能替代 block-level 验证。把没验证好的 RTL 放进 emulation，只会更快地遇到更难 debug 的 bug。

## Agent 生成 RTL 的验证策略

如果使用 agent 从 C model 或规格生成 RTL，应增加额外护栏：

- 每次生成必须通过 lint、格式化、基本仿真和综合 smoke test。
- 生成器输出必须带 traceability，说明哪条规格对应哪段 RTL。
- 对接口协议自动生成 assertion。
- 对算术行为使用 C/Python golden model 做 differential testing。
- 对状态机和 FIFO 使用 formal。
- 对 prompt 和 generator 版本做版本管理。
- 禁止人工“临时修补”不回灌到生成源。

否则项目会出现不可复现 RTL：某次生成能过，下一次生成破坏 corner case，没人知道差异来自 prompt、模型版本还是人工修改。

## 角色、节奏、成本与接口

验证的 owner 应是 DV lead，而不是 RTL designer 兼职“写几个 test”。Block 级验证由 DV engineer、RTL owner 和架构师共同闭环；subsystem/SoC 级还需要 firmware、driver、VIP、emulation 和系统软件参与。验证计划应在 RTL 大规模编码前启动，block 级回归通常随 RTL 每周滚动，subsystem/SoC regression 会持续到前端 signoff 前；复杂 AI SoC 的验证往往是前端最长路径之一。

上游输入是 PRD、架构/微架构规格、C/golden model、寄存器模型、接口协议和 IP 文档。下游输出是 testbench、assertion、coverage、bug 数据库、回归报告、waiver、emulation bring-up 资产和 signoff 证据。成本包括 DV 人力、商业仿真/formal/emulation license、VIP、算力和回归维护。创业公司可以用 Verilator/cocotb/CI 做快速 smoke，但不能省 DV lead、需求覆盖、关键协议 assertion 和 bug triage 纪律。

## 典型场景

一个矩阵乘 block 在 directed test 中全部通过。随机测试开启 backpressure 后，scoreboard 发现偶发结果错位。波形显示输入 valid 保持，但内部 tile ID 在 stall 时前进了一拍。C model 没有 stall 概念，所以此前无法发现。

团队修复方法是把 tile ID 和 payload 绑定为同一 transaction，在 RTL 中所有 pipeline stage 使用 valid-ready skid buffer；补 assertion 检查 stall 时 payload 稳定；functional coverage 增加连续 stall、随机 stall、FIFO almost full、不同 tile size 组合。这个 bug 的价值不在于修一行代码，而是暴露验证计划缺少 backpressure 维度。

## 创业公司视角

验证负责人是早期关键招聘。没有强 DV owner，自动生成 RTL 只会加速生成未验证代码。创业公司可以在工具上务实组合：开源 Verilator/cocotb 做快速 smoke，商业 simulator 做 signoff regression，formal 用在关键协议，emulation 外包或租用用于 SoC 软件 bring-up。

不要把 coverage 数字当融资指标。真正有用的是 requirements coverage、关键风险列表、未关闭 bug 趋势、waiver 解释和硅后可调试能力。

## 后续阅读

- [综合准备](./04_synthesis_preparation.md)
- [CDC 与 RDC](./06_cdc_and_rdc.md)
- [低功耗设计](./07_low_power_design.md)
- [前端签核标准](./08_signoff_criteria.md)

## 参考公开来源

- [IEEE 1800.2-2020 UVM 标准页面](https://standards.ieee.org/ieee/1800.2/7567/)
- [Accellera Standards](https://accellera.com/downloads/standards)
- [Accellera Portable Stimulus Working Group](https://accellera.org/activities/working-groups/portable-stimulus)
- [Synopsys VC Formal](https://www.synopsys.com/verification/resources/datasheets/vc-formal.html)
- [Cadence Xcelium](https://www.cadence.com/en_US/home/tools/system-design-and-verification/simulation-and-testbench-verification/xcelium-simulator.html)
- [Synopsys VCS](https://www.synopsys.com/verification/simulation/vcs.html)

## 内容可信度说明

- **公开信息（高可信）**：UVM 是 IEEE 1800.2 标准；PSS、UVM、SystemC 等 Accellera 标准公开；商业仿真、formal、emulation 工具类别公开可查。
- **行业惯例（中可信）**：block/subsystem/SoC 分层验证、scoreboard、coverage closure、assertion、formal、emulation 组合是主流 ASIC 验证实践。
- **经验性观察（中低可信）**：AI 芯片 bug 常集中在 backpressure、DMA、buffer、shape、精度和并发；agent 生成 RTL 需要 traceability 和自动化回归护栏。
- **不确定/需向资深工程师确认（低可信）**：具体 coverage 目标、formal 应用范围、emulation 投入时间、VIP 选择和 regression 规模需由项目复杂度决定。
