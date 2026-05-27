# ADC/DAC/Sense Amp：Analog CIM 的咽喉

上级：[04 Circuit And Macro](./README.md)
相关：[Analog CIM 基础](../03-compute-paradigms/analog-cim-fundamentals.md), [Peripheral Overhead](./peripheral-overhead.md), [ReRAM-CIM 深入](../02-memory-technologies/reram-cim-deep-dive.md)

## 这页在回答什么问题

为什么很多 analog CIM 的理想能效到 macro 后会缩水？因为阵列输出不是可直接交给数字系统的结果，必须经过 DAC/driver 激励、SA 判决、ADC 量化、reference 和校准链路。

## 三类电路的职责

DAC 或 input driver 把数字输入变成模拟激励。它可以是电压幅度、脉宽、脉冲次数或多周期 bit-serial 控制；位宽越高，输入端开销越难隐藏。

Sense amplifier 把小电压或小电流差放大并判决。对 SRAM digital CIM，它可能服务于 bitwise 结果；对 SRAM mixed-signal CIM，它可能面对 charge/current accumulation 的小 margin；对 ReRAM/Flash analog CIM，它常常是 ADC 前的关键读出路径。

ADC 把 array 输出的电流、电压或电荷转成数字 partial sum。低比特 ADC 能保住一部分能效，高比特 ADC 会快速增加比较次数、参考精度、面积、功耗和布局压力。经验上，4-bit column ADC 在小 macro 中可能占约 30-60% 的能耗或面积预算；8-bit 等效精度往往需要多周期、分段或数字校正，否则会吞掉理想阵列收益。

## 三条 Paradigm 的差异

Analog CIM 对 ADC/DAC 最敏感。ReRAM/Flash 的 array-native MVM 必须靠量化进入数字系统，ADC 位数、共享方式和采样率直接决定有效精度与吞吐。

Digital CIM 可以避免完整 ADC，但不能避免 sense path 和 local logic。它的代价转移到 SA 稳定性、popcount tree、bit-serial cycles、shift-add accumulator 和 routing。

Mixed-signal CIM 的核心设计点是边界：更晚 ADC 化可以保留 analog 并行，但 calibration 和 noise 更难；更早 SA/comparator 判决可以提高可控性，但会损失 analog 局部累加收益。

## ADC 共享不是免费午餐

每列 ADC 吞吐高，但面积和功耗重。多列共享 ADC 可降面积，却引入 multiplexing、sample/hold、时序排队和带宽瓶颈。分时 ADC 对低吞吐 edge inference 可能可接受，对高利用率 NPU tile 可能让 array 空转。

因此读论文时不能只记录 ADC bit 数，还要记录 ADC 架构、列共享比、sample rate、是否包含 reference、是否包含 input DAC、是否包含数字校正和 calibration memory。

## 与 RAM Sense Path 的关系

传统 SRAM/DRAM sense path 追求可靠读出；CIM sense path 还要承载 partial sum 或 bitwise 判决。RAM wiki 中的 [read/write timing](../../../RAM/wiki/02-sram-foundations/read-write-cycle-timing.md) 和 [row-column decode sense amplify](../../../RAM/wiki/04-dram-foundations/row-column-decode-sense-amplify.md) 是理解这条路径的基础，但 CIM 会进一步牺牲一部分 margin 来换取局部计算。

DRAM/HBM/GDDR-PIM 中也有 PHY、sense path 和模拟接口，但那不是本页讨论的 analog CIM ADC 问题。PIM 的关键是 memory die/bank 侧的独立 compute unit、command/dataflow 和 host offload；HBM base die、interposer 或 package-side logic 上的 compute 属于 NMC 边界，不应拿来和 CIM column ADC 直接比较。

## 一句话理解

ADC/DAC/SA 是 analog 与 mixed-signal CIM 的咽喉：它们决定阵列物理并行能留下多少，而不是只负责把结果“读出来”。

## 研究启示

研究应从 “array-only energy” 转向 “conversion-aware macro”。必须报告 ADC/DAC/SA 的位宽、架构、共享比、能耗、面积、时序和校准策略；产业上，可部署方案更倾向低比特 ADC、强数字校正和可测试的 mixed-signal 边界。
