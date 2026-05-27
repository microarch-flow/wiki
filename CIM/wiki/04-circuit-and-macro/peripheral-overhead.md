# Peripheral 开销：为什么 ADC/控制电路常常吃掉主要功耗与面积

上级：[04 Circuit And Macro](./README.md)
相关：[ADC/DAC/SA in CIM](./adc-dac-sa-in-cim.md), [Macro Design Tradeoff Framework](./macro-design-tradeoff-framework.md), [FAB: Process Nodes](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md), [BUS: Interconnect Components](../../../BUS/wiki/04-microarchitecture-integration/interconnect-components.md)

## 这页在回答什么问题

为什么一个 array core 看起来极高效，完整 macro 却没有那么亮眼？因为 CIM 的外围不是辅助细节，而是把 cell 计算变成可用数字结果所必须付出的面积、能耗、时序和验证成本。

## Peripheral 包括什么

Peripheral 至少包括 WL driver、precharge、input encoder、DAC 或 pulse generator、SA、ADC、reference、sample/hold、local accumulator、shift-add、output buffer、controller、clocking、calibration storage 和 test logic。

不同论文对 peripheral 的统计口径差异很大。有人只报 array energy，有人包含 ADC 但不含 DAC，有人包含 macro control 但不含外部 buffer。没有 breakdown 的 TOPS/W 只能作为局部线索，不能作为架构结论。

## 三条 Paradigm 的外围重心

Analog CIM 的外围重心是 DAC/ADC/reference/calibration。低比特 ReRAM/Flash MVM 的 array energy 可以很低，但 column ADC、input drive、write-verify 和数字校正会把优势压缩。

Digital CIM 的外围重心是 local logic、popcount、shift-add、accumulator、routing 和 SRAM read stability。它没有高精度 ADC 的压力，但 bit-serial 支持 INT8 时，周期和 partial sum storage 会显著上升。

Mixed-signal CIM 的外围最容易被低估，因为它把 analog array、SA/ADC、数字校正和 buffer 分散在多个模块里。评估时必须统一统计到 macro boundary。

## 为什么会超过 60%

当 array cell 极小、并行列很多、目标精度需要 ADC、或 bit-serial 需要多周期累加时，外围会成为面积和功耗主项。很多 mixed-signal CIM macro 中，ADC、SA、driver、accumulator 和 buffer 合计超过 60% 并不奇怪；这不是实现差，而是 cell 阵列太便宜后，接口和控制变成主成本。

这个比例不能机械套用到所有设计。SRAM digital CIM 的 60% 可能来自 local logic 和 buffer；ReRAM analog CIM 的 60% 可能来自 ADC/DAC/reference；Flash CIM 还要计入 program/verify 和长期校准。

## Macro 指标的最低披露要求

| 项目 | 为什么必须披露 |
| --- | --- |
| array size | 决定 IR drop、parallelism 和 peripheral amortization |
| ADC/DAC bit 与共享比 | 决定 analog 路线有效精度和吞吐 |
| accumulator width | 决定 digital/mixed-signal partial sum 成本 |
| buffer 容量 | 决定 macro 是否能独立喂饱 |
| controller/calibration | 决定真实面积、能耗和启动/运行成本 |
| measured vs simulated | 决定结论成熟度 |

## 与系统互连的边界

Peripheral 不是最后一层开销。macro 输出还要进入 tile buffer、local reduction、NoC、memory-mapped command path 或 host interface。05 章会连接 NoC wiki 的 [memory-centric NoC](../../../NoC/wiki/06-ai-noc-specifics/memory-centric-noc.md)，解释为什么 macro-level saving 会在系统层继续衰减；BUS wiki 的 interconnect 组件则适合理解 activation/result transfer 和 host-visible movement。

工艺节点也会改变 peripheral 口径。Digital SRAM-CIM 更能跟随主流 CMOS scaling；analog/mixed-signal CIM 受 matching、reference、layout parasitic、低电压 headroom 和 analog-friendly node 约束，不能把 digital PPA scaling 直接套到 ADC/DAC 和 reference 上。

## 一句话理解

Peripheral overhead 是 CIM 从物理原理走向产品指标的最大过滤器；没有外围口径，array TOPS/W 没有架构意义。

## 研究启示

研究应把 peripheral breakdown 作为主结果，而不是附录。产业实现会优先选择外围可控、测试可闭合、软件可建模的 macro，即使它牺牲一部分理想 array 能效。
