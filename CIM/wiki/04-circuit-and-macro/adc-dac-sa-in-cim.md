# ADC/DAC/Sense Amp：Analog CIM 的咽喉

上级：[04 Circuit And Macro](./README.md)
相关：[Analog CIM 基础](../03-compute-paradigms/analog-cim-fundamentals.md), [Peripheral Overhead](./peripheral-overhead.md), [ReRAM-CIM 深入](../02-memory-technologies/reram-cim-deep-dive.md)

## 这页在回答什么问题

为什么很多 analog CIM 的理想能效到 macro 后会缩水？因为阵列输出不是可直接交给数字系统的结果，需要输入驱动和某种读出或转换路径。其结构因实现而异。模拟读出可能经 ADC 转换；数字 CIM 可能使用 sense amplifier 判决。SA 和 ADC 不一定串接，reference、校准和 sample/hold 也需按实际电路核算。

## 三类电路的职责

DAC 或 input driver 把数字输入变成模拟激励。它可以是电压幅度、脉宽、脉冲次数或多周期 bit-serial 控制；位宽越高，输入端开销越难隐藏。

Sense amplifier 把小电压或小电流差放大并判决。对 SRAM digital CIM，它可能服务于 bitwise 结果；对 SRAM mixed-signal CIM，它可能面对 charge/current accumulation 的小 margin；有些实现将读出放大级置于 ADC 前；其他实现直接由 ADC 或其比较器完成相应判决。应以具体电路为准。

ADC 把 array 输出的电流、电压或电荷转成数字 partial sum。ADC 精度与参考电路、噪声、面积、能耗和吞吐相关；比较次数与功耗如何变化取决于 ADC 架构。不能在没有具体设计和统计边界时为面积或能耗指定通用比例。

## 三条 Paradigm 的差异

Analog CIM 对 ADC/DAC 最敏感。ReRAM/Flash 的 array-native MVM 必须靠量化进入数字系统，ADC 位数、共享方式和采样率直接决定有效精度与吞吐。

Digital CIM 可以避免完整 ADC，但不能避免 sense path 和 local logic。它的代价转移到 SA 稳定性、popcount tree、bit-serial cycles、shift-add accumulator 和 routing。

Mixed-signal CIM 的核心设计点是边界：更晚 ADC 化可以保留 analog 并行，但 calibration 和 noise 更难；更早 SA/comparator 判决可以提高可控性，但会损失 analog 局部累加收益。

## ADC 共享不是免费午餐

每列 ADC 吞吐高，但面积和功耗重。多列共享 ADC 可降面积，却引入 multiplexing、sample/hold、时序排队和带宽瓶颈。分时 ADC 对低吞吐 edge inference 可能可接受，对高利用率 NPU tile 可能让 array 空转。

假设八个独立样本由两个 ADC 处理，每个 ADC 每轮转换一个样本，且每个样本能均衡路由，则需要四轮，共八次转换；四个 ADC 均衡分配则需两轮，仍为八次转换。若固定连接使四个样本都只能去 ADC 0，即使有四个 ADC 也要四轮。若 ADC 可流水化，转换 latency 可以大于启动间隔（II），完成时间应按排队和两者计算，而不能简单把轮数乘以 latency。若在转换前有实际模拟合并，先按合并后的独立样本数重新计数。详见[参数字典](../05-architecture-and-system/cim-modeling-parameter-schema.md#adc-样本转换次数与共享)。

[ISAAC 论文](https://users.cs.utah.edu/~rajeev/pubs/isca16-old.pdf)给出 sample/hold 配合共享 ADC 的架构实例。其采样率、交叠和能耗属于具体设计点，不是通用常数。

因此读论文时不能只记录 ADC bit 数，还要记录 ADC 架构、列共享比、sample rate、是否包含 reference、是否包含 input DAC、是否包含数字校正和 calibration memory。

## 与 RAM Sense Path 的关系

传统 SRAM/DRAM sense path 追求可靠读出；CIM sense path 还要承载 partial sum 或 bitwise 判决。RAM wiki 中的 [read/write timing](../../../series/storage/RAM/wiki/02-sram-foundations/read-write-cycle-timing.md) 和 [row-column decode sense amplify](../../../series/storage/RAM/wiki/04-dram-foundations/row-column-decode-sense-amplify.md) 是理解这条路径的基础，但 CIM 会进一步牺牲一部分 margin 来换取局部计算。

DRAM/HBM/GDDR-PIM 中也有 PHY、sense path 和模拟接口，但那不是本页讨论的 analog CIM ADC 问题。PIM 的关键是 memory die/bank 侧的独立 compute unit、command/dataflow 和 host offload；HBM base die、interposer 或 package-side logic 上的 compute 属于 NMC 边界，不应拿来和 CIM column ADC 直接比较。

## 一句话理解

ADC/DAC/SA 是 analog 与 mixed-signal CIM 的咽喉：它们决定阵列物理并行能留下多少，而不是只负责把结果“读出来”。

## 研究启示

研究应从 “array-only energy” 转向 “conversion-aware macro”。必须报告 ADC/DAC/SA 的位宽、架构、共享比、能耗、面积、时序和校准策略；产业上，可部署方案更倾向低比特 ADC、强数字校正和可测试的 mixed-signal 边界。
