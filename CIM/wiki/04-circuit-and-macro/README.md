# 04 Circuit And Macro

上级：[CIM Wiki](../README.md)
相关：[Compute Paradigms](../03-compute-paradigms/README.md), [SRAM-CIM 深入](../02-memory-technologies/sram-cim-deep-dive.md), [ReRAM-CIM 深入](../02-memory-technologies/reram-cim-deep-dive.md)

## 这页在回答什么问题

为什么 CIM 不能只看 cell 或 device？因为真正决定可用性的往往是 macro：array、wordline driver、bitline、sense path、ADC/DAC、accumulator、buffer 和 controller 共同决定能效、精度、面积、测试和模型误差。

## 本章的层级

```text
cell / device
  -> array
  -> driver / bitline / sense path
  -> ADC / DAC / SA / comparator
  -> local accumulator / buffer / controller
  -> tile and system
```

CIM 的定义要求计算发生在 cell 内或紧邻 array path。第 04 章只讨论这个层级的电路与 macro 问题；DRAM/HBM/GDDR-PIM 的独立 compute unit 属于 PIM，不应塞进 CIM macro 指标表。

## 本章页面地图

| 页面 | 主要回答的问题 | Paradigm 差异焦点 |
| --- | --- | --- |
| [Macro Primitives](./cim-macro-primitives.md) | array、driver、sense、accumulator 如何组成 CIM macro | 计算到底在 analog path、digital path 还是边界处发生 |
| [ADC/DAC/SA](./adc-dac-sa-in-cim.md) | 转换和判决为何是 analog/mixed-signal 咽喉 | analog 受 ADC/DAC 支配，digital 更依赖 SA/local logic |
| [Data Encoding](./data-encoding-strategies.md) | 模型数值如何变成电路输入和权重状态 | analog multi-level、digital bit-plane、mixed-signal 边界 |
| [Precision and Quantization](./precision-and-quantization-at-circuit.md) | nominal bit 与 effective precision 为什么不同 | analog 受噪声/ADC，digital 受 accumulator，mixed-signal 受校正 |
| [Non-Idealities](./non-idealities-and-error-sources.md) | 误差如何从 device 传到模型 accuracy | analog/mixed-signal 是数值误差，digital 更像离散故障和时序问题 |
| [Peripheral Overhead](./peripheral-overhead.md) | 为什么外围常吞掉 array 收益 | 三条路线的成本主项不同，统计口径必须统一 |
| [Macro Design Framework](./macro-design-tradeoff-framework.md) | 如何从 workload 反推 macro 参数 | analog/digital/mixed-signal 的选择条件不同 |

## 三条 Paradigm 在 Macro 层的差异

| 话题 | Analog CIM | Digital CIM | Mixed-Signal CIM |
| --- | --- | --- | --- |
| 计算位置 | cell conductance、bitline current、charge sharing | bitwise logic、popcount、bit-serial local accumulation | array 内 analog 局部计算 + 数字判决/校正 |
| 主要瓶颈 | ADC/DAC、noise、variation、drift、IR drop | 面积、布线、周期数、local accumulator | analog/digital 边界、转换开销、校准闭环 |
| 自然 memory | ReRAM、Flash、部分 SRAM current/charge-domain | SRAM，少量 MRAM read/sense-path compute | SRAM、ReRAM、Flash |
| 评估风险 | 只报 array energy | 把 SRAM + MAC 包装成 CIM | 把 ADC、buffer、calibration 分散统计 |

## 读本章时要盯住的口径

Macro 指标必须说明是否包含 WL driver、precharge、SA/ADC、DAC、sample/hold、reference、local buffer、controller、calibration 和 digital accumulation。只报告 array core 的 TOPS/W 不能外推到 chip，更不能和 PIM/NMC 的 system-level latency 横比。

本章也会主动连接外部 wiki：SRAM bitline 和 SA 对应 RAM wiki 的 [wordline-bitline-sense-amp](../../../RAM/wiki/02-sram-foundations/wordline-bitline-sense-amp.md)；工艺节点和 analog headroom 对应 FAB wiki 的 [process nodes and PPA tradeoffs](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)；多 macro reduction 会在 05 章连接 NoC wiki 的 [reduction networks](../../../NoC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md)；macro 与 host-visible command、activation/result transfer 的边界可参考 BUS wiki 的 [interconnect components](../../../BUS/wiki/04-microarchitecture-integration/interconnect-components.md)。

## 一句话理解

第 04 章把 CIM 从“cell 能算”推进到“macro 能不能真实交付”：外围、编码、精度、误差和设计参数比单个 array 原理更接近成败边界。

## 研究启示

CIM 研究的关键转向是从 ideal array 走向 measured macro。高价值论文应报告完整 macro breakdown、有效精度、校准成本、误差传播和 silicon-backed 数据；产业实现则更偏低比特、固定模型、可测试、可校准的 SRAM 或 mixed-signal macro。
