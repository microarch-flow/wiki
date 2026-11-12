# CDC 与 RDC

## 前置知识

- 建议先读 [RTL 设计工程实践](./01_rtl_design_practices.md)。
- 建议先读 [微架构设计](./02_microarchitecture_design.md)。
- 建议理解 [CDC](../00_overview/05_glossary.md#cdc)、[RDC](../00_overview/05_glossary.md#rdc)、[STA](../00_overview/05_glossary.md#sta)。

## 为什么跨域问题危险

[CDC](../00_overview/05_glossary.md#cdc) 是 clock domain crossing，信号从一个时钟域进入另一个时钟域。[RDC](../00_overview/05_glossary.md#rdc) 是 reset domain crossing，不同 reset 或 reset release 顺序导致的问题。跨域 bug 的危险在于仿真经常不暴露，硅上表现为低概率、温度/电压相关、负载相关的随机错误。

软件背景的人容易把跨域理解成多线程同步。这个类比有帮助，但不完整。硬件里的亚稳态是物理现象，不能靠“多跑几次 test”证明没有。必须使用同步结构、异步 FIFO、握手协议和静态 CDC/RDC 工具检查。

## 常见 CDC 场景

| 场景 | 推荐结构 |
|---|---|
| 单 bit 控制信号慢变 | 两级或多级 synchronizer |
| pulse 跨域 | pulse stretcher、toggle synchronizer、握手 |
| 多 bit 数据 | valid/ready handshake、async FIFO、gray counter |
| high-throughput stream | async FIFO 或 clock converter |
| config register 到高速域 | shadow register + update handshake |
| status 返回软件域 | synchronizer + sticky bit |
| reset release | reset synchronizer |

禁止把多 bit bus 直接逐位同步后当作同一时刻数据使用。每一位可能在不同周期稳定，组合后会产生不存在的值。

## 亚稳态、同步器和 Async FIFO

当异步信号在目的时钟采样边沿附近变化，触发器可能进入亚稳态。两级同步器不能消灭亚稳态，但能降低传播到后续逻辑的概率。同步器需要使用专门约束和库单元，后端也要避免被优化、重定时或放得太远。

同步器只适合单 bit 控制或灰码指针等特定结构。数据 bus、counter、valid payload 需要协议保证。异步 FIFO 通常使用双口 memory、读写指针、gray code、跨域同步和满空判断。FIFO 深度要根据频率差、突发长度、backpressure 和系统 latency 计算。

Async FIFO 风险包括 gray pointer 同步错误、full/empty 判断 off-by-one、reset 两侧释放顺序导致假满或假空、overflow/underflow 未被 assertion 捕获、DFT/test mode 不支持异步结构、STA false path 或 max delay 约束错误。建议优先使用经过验证的 FIFO IP 或公司标准库，不要让 agent 从零生成 async FIFO，除非有 formal proof 和成熟回归。

## RDC 特有问题

Reset domain crossing 经常被低估。两个模块使用同一 clock，但 reset source 不同，也可能发生 RDC。一个模块 reset 后输出默认值，另一个模块未 reset 或已经运行，就可能采样到非法组合。异步 reset 释放如果不同步，也会让状态机进入非法状态。

RDC 策略包括异步断言、同步释放；reset tree 分层设计；reset dependency 文档化；reset 后 valid bit 清零；reset during operation 的行为定义；对 reset crossing 使用 RDC 工具检查。

## CDC/RDC 工具流程

常见工具包括 Synopsys VC SpyGlass CDC/RDC、Siemens Questa CDC/RDC、Cadence Jasper CDC 相关能力。工具会识别 clock/reset domain、跨域路径、同步器结构、reconvergence、data/control crossing 和 waiver。

流程通常是：定义 clock 和 reset；定义同步器、FIFO 和已知 IP 模型；运行结构检查；分类 violation 为真实 bug、约束缺失、已验证结构、工具误报；为 waiver 写明理由、owner 和证据；对关键 crossing 增加 assertion 或 formal；在 RTL 变化后持续回归。CDC waiver 不是垃圾桶。没有证据的 waiver 会把硅上随机 bug 合法化。

## 与 STA 的关系

CDC 路径通常不能按普通同步时序分析处理，但这不等于所有跨域路径都可以随意 false path。异步 FIFO 的 gray pointer、synchronizer 输入、handshake path 需要合适的 false path、max delay 或 bus skew 约束。CDC 工具和 STA 约束必须一致。

前端团队不能把 CDC 全推给后端。后端需要知道哪些路径是真异步、哪些是 generated clock、哪些是 physically exclusive、哪些需要特殊约束。

## 角色、节奏、成本与接口

CDC/RDC 的 owner 通常是 RTL lead 或专门的 CDC signoff engineer，block owner 负责解释每条 crossing，STA/后端负责约束一致性，DV/formal 负责对关键跨域协议补证据。CDC/RDC 不应等 SoC 集成末期才做；block 级应在接口稳定后开始跑，subsystem 和 SoC 级在每次 clock/reset 集成变化后回归。

上游输入包括 clock/reset intent、RTL、跨域 primitive 清单、IP clocking 文档、UPF 和 SDC 初版。下游输出包括 CDC/RDC 报告、waiver、标准同步器实例清单、STA exception 建议和需要验证补强的 crossing 列表。成本主要是工具 license、报告 triage 人力和修复跨域结构的设计时间。创业公司可以外包一次 signoff 检查，但内部必须制定“禁止裸 crossing”的编码规则和标准跨域库。

## Agent 生成 RTL 的跨域风险

Agent 很容易在两个 clock domain 之间直接连信号，尤其是顶层集成 glue logic、status register、interrupt、DMA completion、debug path。它可能知道“加两级触发器”，但不知道什么时候两级触发器不适用于多 bit bus，也不知道 reset release、reconvergence 和 handshake liveness。

因此所有生成 RTL 必须自动标注 clock/reset domain，并经过 CDC/RDC 检查。生成器最好内建跨域 primitive，只允许通过 `sync_bit`、`async_fifo`、`pulse_sync`、`reg_update_handshake` 等模板跨域，禁止随意 wire crossing。

## 典型场景

一个 compute tile 在 `npu_clk` 域完成任务后输出 `done_pulse`，控制寄存器在 `cfg_clk` 域读取 done 状态。Agent 生成 RTL 直接把 pulse 接到 cfg 域 sticky bit。仿真中两个 clock 对齐，test 全过。硅上若 pulse 宽度小于 cfg clock 周期，状态偶发丢失。

修复方式是用 toggle synchronizer 或跨域握手，把 done event 转换为目的域可可靠采样的事件；增加 assertion 检查 event 不丢失；CDC waiver 指向标准 synchronizer；软件寄存器定义为 sticky W1C。这个问题说明仿真对齐时钟会掩盖 CDC bug。

## 创业公司视角

CDC/RDC 是不能靠经验省掉的 signoff 项。创业公司可以外包 CDC signoff，但内部 RTL 规范必须限制跨域写法。最实用的做法是建立小型跨域 IP 库和 lint 规则：任何跨域必须实例化标准 primitive，代码评审直接拒绝裸 crossing。

对第一颗芯片，尽量减少 clock domain 和 reset domain。每增加一个 domain，都增加验证、约束、低功耗、DFT 和硅后 debug 成本。

## 后续阅读

- [低功耗设计](./07_low_power_design.md)
- [前端签核标准](./08_signoff_criteria.md)
- [后端 STA](../03_backend_physical_design/05_static_timing_analysis.md)
- [硅后调试](../04_tapeout_and_post_silicon/05_post_silicon_debug.md)

## 参考公开来源

- [Synopsys SpyGlass CDC](https://www.synopsys.com/verification/static-and-formal-verification/spyglass/spyglass-cdc.html)
- [Siemens Questa Design Solutions](https://www.siemens.com/en-us/products/ic/questa-one/design-solutions/)
- [Siemens Questa RDC PDF](https://static.sw.cdn.siemens.com/siemens-disw-assets/public/78491/en-US/Siemens-SW-Questa-RDC-Reset-Domain-Crossing-Verification-FS-78491-C3.pdf)
- [Accellera CDC Standard 下载页](https://accellera.com/downloads/standards)

## 内容可信度说明

- **公开信息（高可信）**：CDC/RDC 工具和 Accellera CDC 相关标准资源公开可查；亚稳态、同步器、异步 FIFO 是数字设计基础概念。
- **行业惯例（中可信）**：CDC/RDC signoff 需要 clock/reset 定义、结构检查、waiver、assertion/formal 和 STA 约束一致性。
- **经验性观察（中低可信）**：agent 生成 glue logic 时容易产生裸 crossing；创业公司应限制 clock/reset domain 数量，并使用标准跨域 primitive。
- **不确定/需向资深工程师确认（低可信）**：具体 synchronizer 级数、MTBF 目标、FIFO 约束、RDC waiver 标准和 STA exception 写法需结合工艺、频率和工具确认。
