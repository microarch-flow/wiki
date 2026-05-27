# 03 Compute Paradigms

上级：[CIM Wiki](../README.md)
相关：[两条正交主线](../01-overview/two-axes-memory-and-paradigm.md), [Memory Technologies](../02-memory-technologies/README.md)

## 这页在回答什么问题

02 章回答“计算依附在哪类 memory 上”，03 章回答“计算到底以什么形式发生”。同样是 SRAM-CIM，可以是 bit-serial digital，也可以是 charge-domain mixed-signal；同样是 ReRAM-CIM，可以是理想 analog MVM，也可以被大量数字校正包起来。

## 本章的纵轴

| Paradigm | 计算发生方式 | 最自然的 memory | 主要风险 |
| --- | --- | --- | --- |
| [Analog CIM](./analog-cim-fundamentals.md) | 电流、电压、电荷直接承载乘加 | ReRAM、Flash、部分 SRAM charge/current-domain | ADC/DAC、噪声、variation、校准、精度上限 |
| [Digital CIM](./digital-cim-fundamentals.md) | bitwise、bit-serial、popcount、local digital accumulation | SRAM-CIM、部分 MRAM read/sense-path compute | 面积、布线、周期展开、是否真正进入 array path |
| [Mixed-Signal CIM](./mixed-signal-cim.md) | array 内 analog/charge/current 计算，外围数字转换与校正 | SRAM、ReRAM、Flash | 边界复杂，外围开销容易被低估 |

PIM 的 compute unit 可以是 digital processing block，但 PIM 不属于本章 analog/digital/mixed-signal CIM 纵轴。DRAM/HBM/GDDR-PIM 的数值格式和执行单元会在 DRAM-PIM、软件栈和产业章节讨论。

反向边界同样重要。Analog CIM 不适合直接套到 DRAM/HBM/GDDR-PIM，因为 PIM 的关键是 memory die/bank 旁的独立处理单元，不是 cell conductance 或 bitline 电荷直接承载 MAC。Digital CIM 不等于“memory 旁边有数字 ALU”，只有 array path 参与 bitwise、popcount 或 bit-serial compute 才成立。Mixed-signal CIM 也不是系统里同时有 analog PHY 和 digital block，而是 analog/digital 边界切在 CIM macro 内部。

## 推荐阅读顺序

1. [Analog CIM 基础](./analog-cim-fundamentals.md)
2. [Analog CIM 深入](./analog-cim-deep-dive.md)
3. [Digital CIM 基础](./digital-cim-fundamentals.md)
4. [Digital CIM 深入](./digital-cim-deep-dive.md)
5. [Mixed-Signal CIM](./mixed-signal-cim.md)
6. [Analog vs Digital Tradeoff Map](./analog-vs-digital-tradeoff-map.md)
7. [Paradigm × Memory Crossmap](./paradigm-memory-crossmap.md)

## 一句话理解

Compute paradigm 是 CIM 的计算机制坐标：analog 追求物理并行，digital 追求确定性和工程可控，mixed-signal 试图把前两者的收益和代价重新切分。

## 研究启示

03 章后续研究不应把 analog/digital/mixed-signal 写成三种风格标签，而要追问乘法、累加、量化、校正和归约分别在哪个物理位置发生。只有这个边界清楚，论文指标里的 TOPS/W、accuracy loss 和 peripheral overhead 才有可比性。
