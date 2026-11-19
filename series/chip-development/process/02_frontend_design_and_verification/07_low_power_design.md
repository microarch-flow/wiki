# 低功耗设计

## 前置知识

- 建议先读 [微架构设计](./02_microarchitecture_design.md)。
- 建议先读 [综合准备需要哪些输入与检查](./04_synthesis_preparation.md)。
- 建议先读 [CDC 与 RDC](./06_cdc_and_rdc.md)。
- 建议理解 [PPA](../00_overview/05_glossary.md#ppa)、[SDC](../00_overview/05_glossary.md#sdc)、[DFT](../00_overview/05_glossary.md#dft)。

## 低功耗不是后端优化

低功耗设计跨越架构、微架构、RTL、综合、后端、验证、软件和硅后。后端可以优化电容、门级实现和电源网络，但如果架构让大量单元无效翻转，或者软件无法进入低功耗状态，后端救不了。

按工作负载和库模型检查开关、内部和漏电功耗。不要重复计入已包含在库内部功耗中的分量。分析边界和瞬态供电见[功耗、压降与电迁移](../03_backend_physical_design/06_power_analysis.md)。

## 常见低功耗技术

| 技术 | 作用 | 代价 |
|---|---|---|
| Clock gating | 关闭无效时钟翻转 | 需要 enable 正确、test bypass、时序检查 |
| Operand isolation | 阻止无效数据进入组合逻辑 | 增加门控逻辑和验证点 |
| Power gating | 关闭整个 power domain | 需要 isolation、retention、rush current 管理 |
| DVFS | 动态调整电压频率 | 需要 PMU、PLL、软件策略和 timing mode |
| Multi-Vt cells | 用不同阈值单元平衡速度/漏电 | 后端优化复杂 |
| Memory banking | 只激活需要的 bank | scheduler 和 bank conflict 复杂 |
| Data precision scaling | 降低 bit width 和切换 | 软件、模型精度和硬件支持复杂 |
| Activity-aware scheduling | 避免热点和无效搬运 | 编译器/runtime 复杂 |

## UPF 和 Power Intent

IEEE 1801 UPF 描述电源域、供电、隔离、电平转换、保持和电源状态。验证、综合和物理实现使用一致的 RTL 和功耗意图，并按所需版本和工具能力核对。 [IEEE 1801-2024](https://standards.ieee.org/ieee/1801/7466/)

低功耗规格要定义：哪些模块属于哪些 power domain；每个 domain 的电源状态和切换条件；关闭 domain 前如何 drain transaction；isolation clamp 值是什么；哪些寄存器 retention；唤醒 latency 和软件可见状态；debug/test mode 下 power 行为；CDC/RDC 与 power state 的关系。

## Clock Gating

Clock gating 是最常见低功耗技术。RTL 可以用使能描述寄存器更新。是否插入集成时钟门控单元取决于综合配置、库和结构。不要随意手写 `clk & en`，这会带来毛刺、时序和 DFT 问题。

Clock gating 关键检查包括 enable 是否稳定，gating 后 reset 是否仍可工作，scan enable 是否能 bypass，gated clock 是否被 CDC/STA 正确识别，关闭时钟时状态是否仍满足协议，wake-up 后是否丢 event。对 agent 生成 RTL，要检查它是否为了“省功耗”手写门控时钟。这类代码应被 lint 规则禁止。

## Power Gating

Power gating 能降低 leakage，但引入 isolation、retention、power switch、状态保存、唤醒序列、inrush current 和验证复杂度。第一颗芯片不应随意引入细粒度 power domain，除非产品功耗目标强依赖它。

Power gating 的核心不是插 power switch，而是定义安全序列：一套可能的顺序是停止接收事务、等待在途操作完成、保存需要保留的状态、建立隔离并关断。唤醒时等待电源和时钟可用，更新复位及恢复状态，再解除隔离、重新接收。保存、隔离、复位及电源操作的具体先后要符合所用宏和控制器。

## AI 芯片低功耗重点

AI 芯片功耗常被数据搬运支配。减少外部内存访问、提高 SRAM reuse、避免 NoC 无效搬运、压缩数据、降低精度、批处理调度和避免阵列空转，通常比单个 MAC gate 优化更重要。

微架构应提供功耗可观测性，例如 per-block activity counter、stall reason、memory access counter、temperature/voltage telemetry。没有观测，就无法在硅后和客户 workload 中优化功耗。

## 低功耗验证

低功耗验证包括静态 UPF 检查、power-aware simulation、formal low-power check、power state coverage 和 gate-level/power-aware signoff。常见工具包括 Synopsys VC LP、Cadence Jasper Low-Power Verification App、Cadence Xcelium power-aware simulation 等。

需要验证的场景包括：power state 转换期间无协议违规；isolation clamp 不造成错误中断或假事务；retention restore 后状态一致；断电 domain 输出不会污染上电 domain；软件误操作时硬件能拒绝或报错；test mode 下 power intent 不破坏 DFT；reset 与 power sequence 不冲突。

## 角色、时长和成本

低功耗设计由架构师、RTL、low-power specialist、验证、后端、电源完整性、软件/firmware 共同负责。轻量 clock gating 可以在 RTL 开发中持续完成；多 power domain、DVFS、retention 和 power-aware 验证会贯穿前端到后端。成本主要体现在额外验证、UPF 维护、EDA license、后端电源网络复杂度和硅后功耗调试时间。

## 典型场景

**教学假设。** 团队希望 NPU tile 空闲时 power gate。初版 RTL 只加了 `tile_power_down` 控制。验证发现如果 DMA 正在写 tile SRAM，软件同时关闭 tile，事务会丢失。后端指出 SRAM macro 的电源状态和 tile logic 不一致会产生 isolation 风险。DFT 工程师指出 power-off domain 无法 scan。

正确方案是增加 power manager 状态机：停止调度新任务，等待 DMA 和 compute drain，flush 状态，保存必要寄存器，配置 isolation，关闭电源。软件驱动只能发请求，不能直接切电。验证计划增加 power transition random test 和 assertion。

## 创业公司视角

如果第一颗芯片目标是证明架构和软件生态，低功耗策略应务实：优先做 clock gating、memory banking、数据搬运优化和功耗计数器；谨慎做复杂 power gating 和 DVFS。复杂低功耗状态会成倍增加验证、DFT、CDC/RDC 和硅后 bring-up 难度。

如果产品定位是边缘低功耗，低功耗不能后置。必须从 workload、编译器、memory hierarchy 和电源状态模型开始设计，而不是 RTL 完成后再“降功耗”。

## 后续阅读

- [可测性设计与制造测试](./05_dft_introduction.md)
- [CDC 与 RDC](./06_cdc_and_rdc.md)
- [前端交接评审](./08_signoff_criteria.md)
- [后端功耗分析](../03_backend_physical_design/06_power_analysis.md)

## 参考公开来源

- [IEEE P1801 / UPF 标准页面](https://standards.ieee.org/ieee/1801/7466/)
- [Synopsys VC LP](https://www.synopsys.com/verification/static-and-formal-verification/vc-lp.html)
- [Synopsys Low Power Verification](https://www.synopsys.com/verification/solutions/low-power/low-power-verification.html)
- [Cadence Jasper Low-Power Verification App](https://www.cadence.com/ko_KR/home/tools/system-design-and-verification/formal-and-static-verification/jasper-verification-platform/low-power-verification-app.html)

## 内容可信度说明

- **公开信息（高可信）**：IEEE 1801/UPF、低功耗静态检查、power-aware simulation、clock gating、power gating 等公开可查。
- **行业惯例（中可信）**：低功耗设计需要 power intent、power domain、isolation、retention、DFT/test mode、软件协作和 verification plan。
- **经验性观察（中低可信）**：AI 芯片功耗常由数据搬运和 SRAM/NoC 活动主导；第一颗芯片应谨慎引入复杂 power gating/DVFS。
- **不确定/需向资深工程师确认（低可信）**：具体 power domain 划分、UPF 写法、retention 策略、IR/EM 影响、唤醒时间和电源管理策略需由低功耗/后端/系统专家确认。
