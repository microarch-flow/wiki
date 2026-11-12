# RTL 设计工程实践

## 前置知识

- 建议先读 [本目录 README](./README.md)。
- 建议先读 [微架构设计](./02_microarchitecture_design.md)。
- 建议理解术语表中的 [RTL](../00_overview/05_glossary.md#rtl)、[C Model](../00_overview/05_glossary.md#c-model)、[Lint](../00_overview/05_glossary.md#lint)、[Synthesis](../00_overview/05_glossary.md#synthesis)。

## RTL 不是软件代码

[RTL](../00_overview/05_glossary.md#rtl) 描述的是每个时钟沿寄存器如何更新，以及寄存器之间的组合逻辑如何连接。软件代码默认是顺序执行，硬件默认是并行存在。你在 C 里写一段循环，通常表示一个处理器按顺序执行；你在 RTL 里写类似结构，综合工具可能推导出大量并行逻辑、计数器、状态机，或者根本不可综合。

软件工程师最容易犯的错误是把 Verilog/SystemVerilog 当作“另一种 C”。在硬件里，每个 `always_ff` 块代表触发器行为，每个 `always_comb` 块代表组合逻辑，每个信号赋值都可能生成真实门级结构。位宽、符号扩展、默认值、X 传播、reset 策略和时钟边界不是风格问题，而是功能、时序、面积和功耗问题。

## 基本编码纪律

推荐使用 SystemVerilog 的可综合子集，而不是随意使用语言全集。IEEE 1800 定义了语言，但综合工具、仿真工具、formal 工具和 LEC 工具对不同语法的支持可能不完全一致。工程上应建立 coding guideline，并用 lint 工具强制执行。

常见规则包括：

- 用 `always_ff` 描述时序逻辑，用 `always_comb` 描述组合逻辑，减少敏感列表和阻塞/非阻塞误用。
- 时序逻辑使用非阻塞赋值 `<=`，组合逻辑使用阻塞赋值 `=`。
- 所有寄存器 reset 后的状态必须符合系统 bring-up 和 DFT 要求。
- 组合逻辑必须给所有输出默认赋值，避免隐式锁存器。
- 明确每个信号位宽，避免依赖工具隐式扩展。
- FSM 必须有合法 reset state、默认转移和非法状态处理策略。
- ready/valid、request/grant、FIFO 满空等协议必须写成可检查的 assertion。
- 不在普通 RTL 中使用不可综合或工具支持不一致的高级 SystemVerilog 特性。

这些规则看起来啰嗦，是因为 RTL 错误不一定在仿真中暴露。一个未赋默认值的组合输出，在软件里可能只是未初始化变量；在硬件里可能推导出锁存器，带来时序、功耗和可测性问题。

## Reset 策略为什么重要

Reset 在软件里常被类比成进程初始化，但硬件 reset 更复杂。芯片上有多个 clock domain、power domain、IP、PLL、SRAM、寄存器和外设。reset 的断言和释放顺序如果不清楚，芯片可能偶发死锁，或者硅后 bring-up 时只能靠反复上电碰运气。

常见决策包括：

| 决策 | 选项 | 工程影响 |
|---|---|---|
| reset 类型 | 同步 reset / 异步 reset / 异步断言同步释放 | 影响时序、DFT、RDC 和工具处理 |
| reset 覆盖范围 | 所有寄存器 reset / 只 reset 控制状态 | 影响面积、功耗、布线和 X 调试 |
| reset 状态 | idle / safe / retention restore | 影响 boot、低功耗和异常恢复 |
| reset source | POR、软件 reset、watchdog、debug reset | 影响系统可调试性 |

先进节点下，大量全局 reset 信号本身会形成高扇出网络，增加布线和时序压力。因此不是“所有寄存器都 reset”就一定更好。常见做法是 reset 控制路径和可观察状态，数据路径寄存器通过 valid bit 保证无效数据不会被消费。但这种策略要求验证环境能证明 valid 语义正确。

## 为什么要避免锁存器

锁存器不是绝对不能用，但在主流同步数字 ASIC 流程中，隐式锁存器通常被视为 bug。它可能来自组合 always 块缺少默认赋值或 case 分支不完整。锁存器对时序分析、DFT scan、CDC 分析和调试都更麻烦。

软件背景的人容易认为“保持上一次值”是自然行为。在 RTL 组合逻辑里，如果你没给输出赋值，综合器为了保持值就可能生成锁存器。工程上应显式决定：如果要保持状态，用触发器；如果是组合输出，所有路径都赋值。

## FSM 编码

有限状态机通常拆成状态寄存器、next-state 组合逻辑和输出逻辑。编码方式可以是 binary、one-hot、gray 或工具自动选择。小状态机常用 one-hot 以换面积换时序；大状态机可能用 binary 节省触发器。关键不是哪种编码“高级”，而是是否可读、可综合、可验证、可 ECO。

FSM 必须回答：reset 后进入哪个状态；每个状态的输入条件和输出行为是什么；非法状态如何恢复或报错；backpressure 时是否保持状态；与跨时钟信号、低功耗状态、test mode 是否冲突。Agent 生成 FSM 时常见问题是只覆盖 prompt 中的 happy path，遗漏错误输入、同时事件、优先级和非法状态。

## 接口和握手

AI 芯片前端大量 bug 来自接口协议，而不是算术单元。ready/valid 协议看似简单，但要明确：valid 什么时候保持，ready 什么时候可拉低，payload 在 valid 且未 handshake 时是否稳定，是否允许 bubble，是否允许组合 ready path，是否存在死锁环。

建议为每类内部协议写小型规范和 assertion。例如：

```systemverilog
// 当 valid 拉高但尚未被 ready 接收时，payload 必须保持稳定。
property p_payload_stable;
  @(posedge clk) disable iff (!rst_n)
    valid && !ready |=> valid && $stable(payload);
endproperty
```

这类 assertion 比文档更难被误解。对 agent 生成 RTL，assertion 是必要护栏，因为它把“协议语义”从自然语言变成工具可检查条件。

## C Model 到 RTL 的风险

[C Model](../00_overview/05_glossary.md#c-model) 适合作为 [Golden Model](../00_overview/05_glossary.md#golden-model)，但它通常不会表达这些硬件细节：

- 每拍处理多少数据，pipeline latency 是多少。
- buffer 满时上游如何停顿。
- 多个 master 同时请求时仲裁优先级是什么。
- reset 中和 reset 后信号是否有效。
- 定点舍入、饱和、NaN、overflow、underflow 如何处理。
- 未对齐访问、非法配置、异常中断如何处理。
- 跨时钟域信号如何同步。
- SRAM 读延迟、写冲突和 read-during-write 语义是什么。

如果 agent 根据 C model 直接生成 RTL，它可能生成“功能上像”的硬件，但不是“工程上能流片”的硬件。正确流程是先把 C model 分成 reference model、cycle model、microarchitecture spec 和 interface contract，再生成 RTL。

## Lint、工具分类和代码评审

[Lint](../00_overview/05_glossary.md#lint) 不是美化工具，而是前端质量门。工具边界要分清：Verilator lint-only、Synopsys VC SpyGlass、Siemens Questa Lint、Verible 主要用于风格和静态结构检查；Synopsys VCS、Cadence Xcelium、Siemens Questa 主要用于仿真；Cadence JasperGold、Synopsys VC Formal 主要用于 formal；Synopsys Formality、Cadence Conformal 主要用于 LEC；Synopsys Design Compiler、Cadence Genus 主要用于综合。不要把“某个 EDA 套件里有很多 app”理解成一个工具能替代完整流程。

代码评审重点不是“语法是否能编译”，而是 RTL 是否对应微架构规格；时钟、reset、enable、valid、ready 语义是否明确；是否存在组合环路、隐式 latch、X 乐观/悲观问题；位宽、符号、截断、饱和是否与规格一致；是否给验证留下可观察点和 assertion；是否能综合、scan、CDC/RDC 检查和后端实现。

## 角色、节奏、成本与接口

RTL 的直接 owner 是 RTL designer 或 block owner，RTL lead 负责风格、接口和 signoff 纪律，DV lead 负责把 RTL 行为映射到验证计划，synthesis/STA/DFT/CDC/后端工程师提供早期约束反馈。一个中等复杂 block 从微架构评审到 RTL 初版通常是数周量级，复杂子系统会持续数月迭代；具体取决于规格稳定性、IP 复用和验证成熟度。

上游输入包括微架构规格、接口协议、寄存器模型、时钟/复位/功耗约束和 C/golden model。下游输出包括可综合 RTL、file list、lint 报告、基本仿真结果、assertion、CDC/RDC 标注、综合 smoke 结果和 waiver。成本主要来自资深 RTL/DV 人力和 EDA license；创业公司可以用模板、generator、CI 和开源工具降低重复劳动，但不能省 RTL owner、code review、lint/CDC 和综合试跑。

## 典型场景

团队用 agent 生成一个 DMA descriptor fetch 模块。仿真中单 descriptor 正常完成。代码评审发现 `desc_valid` 在 `desc_ready=0` 时会重新采样地址，导致 backpressure 下 descriptor payload 变化。Lint 又报出一个组合 always 块缺少默认赋值，综合可能推导锁存器。CDC 工具发现 completion pulse 从 DMA 时钟域直接进控制寄存器域。

修复不是简单“再生成一次”。团队应先写 descriptor 协议：payload 稳定规则、ready/valid 时序、跨域路径、reset 后状态、错误响应。然后补 assertion、directed test、random backpressure test 和 CDC waiver 说明。agent 可以参与改代码，但最终签核依据是工具报告和评审记录。

## 创业公司视角

早期不要追求复杂 RTL 框架，先建立少量硬规则：统一 reset 策略、统一接口协议、统一寄存器模板、统一 lint 规则、统一 assertion 风格、统一 code review checklist。每个自动生成模块必须带同版本的 spec、test、assertion 和 lint 结果。

如果团队的差异化是 RTL 自动生成，应把 generator 当作编译器产品来管理：有 IR、类型系统、协议库、静态检查、golden test、回归套件和版本锁定。不要把“LLM prompt + 手工修补”当作可重复芯片设计流程。

## 后续阅读

- [微架构设计](./02_microarchitecture_design.md)
- [前端验证方法学](./03_verification_methodology.md)
- [综合准备](./04_synthesis_preparation.md)
- [软件背景人的前端陷阱](./09_software_engineer_pitfalls.md)

## 参考公开来源

- [IEEE 1800-2023 SystemVerilog 标准页面](https://standards.ieee.org/standard/1800-2023.html)
- [Verilator lint-only 文档](https://verilator.org/guide/latest/verilating.html)
- [Synopsys SpyGlass CDC](https://www.synopsys.com/verification/static-and-formal-verification/spyglass/spyglass-cdc.html)
- [Synopsys VCS](https://www.synopsys.com/verification/simulation/vcs.html)

## 内容可信度说明

- **公开信息（高可信）**：SystemVerilog 是 IEEE 标准；Verilator 支持 lint-only；商业 EDA 工具覆盖仿真、lint、CDC、formal 和综合流程。
- **行业惯例（中可信）**：always_ff/always_comb、非阻塞/阻塞赋值、reset 策略、避免隐式 latch、FSM 评审、ready/valid assertion 是主流 RTL 工程实践。
- **经验性观察（中低可信）**：agent 生成 RTL 容易遗漏 backpressure、非法状态、X/reset、位宽和跨域细节；创业公司应把自动生成器按编译器工程管理。
- **不确定/需向资深工程师确认（低可信）**：具体项目采用同步 reset 还是异步 reset、FSM 编码策略、lint waiver 标准、不同工具对 SystemVerilog 子集的支持边界。
