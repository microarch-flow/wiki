# 电路、外围与计算宏

<span class="micro-legacy-anchor" id="04-circuit-and-macro"></span>


上级：[CIM Wiki](../README.md)
相关：[Compute Paradigms](../03-compute-paradigms/README.md), [SRAM-CIM 深入](../02-memory-technologies/sram-cim-deep-dive.md), [ReRAM-CIM 深入](../02-memory-technologies/reram-cim-deep-dive.md)

## 这页在回答什么问题

为什么 CIM 不能只看 cell 或 device？因为真正决定可用性的往往是 macro：array、wordline driver、bitline、sense path、ADC/DAC、accumulator、buffer 和 controller 共同决定能效、精度、面积、测试和模型误差。

## 本章的层级

跟一条计算命令看信号往哪里走。**控制器**安排预充、驱动、采样和输出握手。**数据通路**从输入驱动器开始。它向行线施加激励，阵列中已保存的权重决定各支路的响应，列端读出电压、电流或逻辑位。若输入要从数字码变成模拟激励，数模转换器（DAC）或脉冲驱动器位于阵列之前。[沿一条命令查读出与交付](./cim-macro-primitives.md#follow-one-command)

列端要交出什么，决定接哪种电路。判一个逻辑位时，感测放大器（SA）可以分辨一对位线的电压高低，也可以将信号与参考比较。要把连续的部分和分成多个数字等级时，可以保持样本，交给模数转换器（ADC）。在本章的双样本例子里，共享 ADC 先后交出两份码，本地累加器将它们相加，输出缓冲保存结果，直到 tile 中的下一级接收。判断宏与系统的边界时，可以分别指出码生成、结果写入和接收发生在哪里。[看一份保持样本怎样成为数字码](./adc-dac-sa-in-cim.md#sample-to-code)

CIM 的定义要求计算发生在 cell 内或紧邻 array path。第 04 章只讨论这个层级的电路与 macro 问题；DRAM/HBM/GDDR-PIM 的独立 compute unit 属于 PIM，不应塞进 CIM macro 指标表。

<span class="micro-legacy-anchor" id="本章页面地图"></span>

## 阅读顺序

1. [一条点积命令进了 CIM 宏，结果在哪一拍才算交付？](./cim-macro-primitives.md)　跟一条命令经过驱动、采样、转换和累加，区分结果算出与下一级收下的时刻。
2. [比较器每次只判一位，ADC 怎样把 16 mV 和 30 mV 读成 8 和 15？](./adc-dac-sa-in-cim.md)　沿四次阈值比较，把保持的两个样本分别读成 8 和 15，再检查这两份码何时能相加。
3. [数据编码](./data-encoding-strategies.md)：模型数值如何变成电路输入和权重状态；analog multi-level、digital bit-plane、mixed-signal 边界。
4. [精度与量化在电路层的实现约束](./precision-and-quantization-at-circuit.md)：nominal bit 与 effective precision 为什么不同；analog 受噪声/ADC，digital 受 accumulator，mixed-signal 受校正。
5. [非理想性总览](./non-idealities-and-error-sources.md)：误差如何从 device 传到模型 accuracy；analog/mixed-signal 是数值误差，digital 更像离散故障和时序问题。
6. [Peripheral 开销](./peripheral-overhead.md)：为什么外围常吞掉 array 收益；三条路线的成本主项不同，统计口径必须统一。
7. [Macro 设计的决策框架](./macro-design-tradeoff-framework.md)：如何从 workload 反推 macro 参数；analog/digital/mixed-signal 的选择条件不同。
## 三条 Paradigm 在 Macro 层的差异

| 话题 | Analog CIM | Digital CIM | Mixed-Signal CIM |
| --- | --- | --- | --- |
| 计算位置 | cell conductance、bitline current、charge sharing | bitwise logic、popcount、bit-serial local accumulation | array 内 analog 局部计算 + 数字判决/校正 |
| 主要瓶颈 | ADC/DAC、noise、variation、drift、IR drop | 面积、布线、周期数、local accumulator | analog/digital 边界、转换开销、校准闭环 |
| 自然 memory | ReRAM、Flash、部分 SRAM current/charge-domain | SRAM，少量 MRAM read/sense-path compute | SRAM、ReRAM、Flash |
| 评估风险 | 只报 array energy | 把 SRAM + MAC 包装成 CIM | 把 ADC、buffer、calibration 分散统计 |

## 读本章时要盯住的口径

Macro 指标必须说明是否包含 WL driver、precharge、SA/ADC、DAC、sample/hold、reference、local buffer、controller、calibration 和 digital accumulation。只报告 array core 的 TOPS/W 不能外推到 chip，更不能和 PIM/NMC 的 system-level latency 横比。

本章也会主动连接外部 wiki：SRAM bitline 和 SA 对应 RAM wiki 的 [wordline-bitline-sense-amp](../../../storage/02-sram/foundations/wordline-bitline-sense-amp.md)；工艺节点和 analog headroom 对应 FAB wiki 的 [process nodes and PPA tradeoffs](../../../chip-development/FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)；多 macro reduction 会在 05 章连接 NoC wiki 的 [reduction networks](../../../interconnect/NOC/06-ai-noc-specifics/reduction-and-collective-networks.md)；macro 与 host-visible command、activation/result transfer 的边界可参考 BUS wiki 的 [interconnect components](../../../interconnect/BUS/04-microarchitecture-integration/interconnect-components.md)。

## 一句话理解

第 04 章把 CIM 从“cell 能算”推进到“macro 能不能真实交付”：外围、编码、精度、误差和设计参数比单个 array 原理更接近成败边界。

## 研究启示

CIM 研究的关键转向是从 ideal array 走向 measured macro。高价值论文应报告完整 macro breakdown、有效精度、校准成本、误差传播和 silicon-backed 数据；产业实现则更偏低比特、固定模型、可测试、可校准的 SRAM 或 mixed-signal macro。
