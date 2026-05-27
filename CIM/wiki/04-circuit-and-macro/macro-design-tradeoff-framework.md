# Macro 设计的决策框架：从 Workload 到 Macro 参数

上级：[04 Circuit And Macro](./README.md)
相关：[Memory Tech Comparison Matrix](../02-memory-technologies/memory-tech-comparison-matrix.md), [Analog vs Digital Tradeoff Map](../03-compute-paradigms/analog-vs-digital-tradeoff-map.md), [FAB: Architecture to Process Selection](../../../FAB/wiki/06-cross-cutting-engineering/from-architecture-to-process-selection.md)

## 这页在回答什么问题

如果要设计或评估一个 CIM macro，应该先选 memory、paradigm、array size，还是先看 workload？正确顺序是从 workload 的数值、复用、更新频率和误差容忍出发，再反推 macro 参数。

## 决策链

```text
workload numeric / reuse / update rate
  -> memory technology
  -> compute paradigm
  -> encoding and precision
  -> array size and peripheral sharing
  -> calibration and test strategy
  -> macro-to-tile integration
```

如果 workload 是低比特、固定权重、强能效约束的 edge inference，ReRAM/Flash analog 或 mixed-signal 有研究吸引力。如果目标是 LLM decode memory-side offload，问题应转向 DRAM/HBM/GDDR-PIM 或 NMC，而不是强行设计 CIM macro。如果目标是可量产 SoC、INT4/INT8、可验证软件栈，SRAM digital/mixed-signal 更自然。

## 关键参数怎么选

Array size 越大，parallelism 和 peripheral amortization 越好，但 IR drop、variation、read disturb、ADC range 和 yield 风险上升。ReRAM crossbar 尤其受 array size 约束；SRAM-CIM 则要平衡 bitline load、WL driver 和 local logic。

ADC/DAC 位宽越高，模型精度越容易保留，但能耗、面积和 latency 非线性上升。低比特 ADC 配合 QAT 和数字累加更现实；高等效精度需要证明外围没有吞掉收益。

Accumulator width 越大，partial sum 安全性越高，但 local register、adder、routing 和 buffer 成本上升。Digital CIM 的 INT8 支持尤其要检查这一项。

Calibration 越强，accuracy 越稳，但启动时间、运行能耗、测试向量、参数存储和软件模型复杂度上升。

## Paradigm-Specific 设计取舍

Analog CIM 的设计重点是让 array physics 和 workload tolerance 对齐：低比特、固定权重、小阵列、可校准、可容错。它不适合频繁权重更新和高精度动态模型，除非有很强的系统证据。

Digital CIM 的设计重点是证明靠近 array 的 bitwise/bit-serial 逻辑比传统 SRAM buffer + MAC 更划算。它需要公平 baseline、真实 bit-width、utilization 和 routing 口径。

Mixed-signal CIM 的设计重点是选择 analog/digital 边界。边界靠前，产品风险低但能效不极致；边界靠后，理论能效高但 ADC、noise、校准和验证更重。

## 工艺与封装因素

Digital SRAM-CIM 更能跟随先进 CMOS 节点；analog ReRAM/Flash/PCM 路线未必从先进节点直接受益，因为低电压、mismatch、analog headroom 和新器件集成会带来额外风险。3D CIM 和 memory-on-logic 研究可连接 FAB wiki 的 [3DIC fundamentals](../../../FAB/wiki/04-back-end-packaging/3d-routes/3dic-fundamentals.md)，但要分清两类边界：cell/array 垂直集成才可能属于 CIM macro；memory die/bank 上独立 compute unit 属于 PIM；HBM base die、interposer 或 package-side logic 上的 compute 属于 NMC。

Memory technology 约束不能跳过：SRAM 适合 digital/mixed-signal；ReRAM/Flash 更适合 analog/mixed-signal；PCM/MRAM 是研究或窄场景；DRAM/HBM/GDDR 是 PIM 系统路线。macro 参数还会向 05 章传递，影响 tile interface、bank 组织、NoC reduction、memory hierarchy 和 host integration。

## 评价框架

| 问题 | 不合格回答 | 合格回答 |
| --- | --- | --- |
| 为什么选这种 memory | density 高 | workload、写入频率、精度和工艺共同匹配 |
| 为什么选这种 paradigm | analog 更省电 | 包含 ADC/DAC/校准后仍有收益 |
| 为什么这个 array size | 并行度高 | IR drop、peripheral amortization 和 yield 平衡 |
| 是否可产品化 | TOPS/W 高 | DFT、PVT、silicon data、软件映射和系统利用率可闭合 |

## 一句话理解

CIM macro 设计不是追求单项最强，而是在 workload、memory、paradigm、编码、外围、误差和工艺之间闭合一个可部署的局部系统。

## 研究启示

研究应从 workload-to-macro 的决策链报告设计，而不是只展示新电路。产业实现会偏向保守但可闭合的参数：中小阵列、低比特、明确 calibration、完整 peripheral 统计和可接入现有 SoC/编译栈的接口。
