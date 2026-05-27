# ReRAM 作为计算元件：电阻态如何编码权重

上级：[02 Memory Technologies](./README.md)
相关：[ReRAM-CIM 深入](./reram-cim-deep-dive.md), [Analog CIM 基础](../03-compute-paradigms/analog-cim-fundamentals.md), [Non-Idealities](../04-circuit-and-macro/non-idealities-and-error-sources.md)

## 这页在回答什么问题

ReRAM 为什么被反复视为“最像 CIM 理想形态”的 memory？因为它的存储状态就是电阻或电导，而电导可以直接进入 Ohm 定律和 Kirchhoff 电流求和，天然对应矩阵向量乘中的权重乘法和列向累加。

## 从电阻态到权重

ReRAM cell 通过材料中的导电通道、氧空位分布或阻变状态保存信息。对 CIM 来说，关键不是它能保存 0/1，而是它可以把权重映射成 conductance：

```text
V_input -> ReRAM conductance G_weight -> I = V * G
column current sum -> dot product
```

这条路径让乘法和加法都变成物理过程。乘法由输入电压和器件电导产生电流，加法由同一列上的电流自然汇合。类比地说，ReRAM crossbar 像一张权重已经固化在水管粗细里的网，输入电压打开水压，每列流量就是局部 dot product；精确语言是 conductance matrix 与 input voltage vector 的 analog MVM。

## 为什么它天然偏 analog / mixed-signal

ReRAM-CIM 的核心吸引力来自 analog conductance 和 column current summation。Digital ReRAM-CIM 可以做，但会放弃 multi-level conductance、阵列并行 MVM 和高密度模拟累加的主要优势，变成一种非易失 binary memory 加外围数字逻辑。它不是不可能，而是不符合 ReRAM 被选中的主要理由。

Mixed-signal 是更现实的落点。array 内用 analog current 完成局部 MVM，array 外用 ADC、数字校正、多周期累加、差分编码和 mapping 补偿误差。也就是说，ReRAM 的“计算元件”是 analog，但可用系统几乎必然需要 digital support。

## 权重表示的几个硬问题

第一，正负权重不能由单个无符号电导自然表示。常见方案是差分对：一组 cell 表示正权重，另一组表示负权重，输出取差。代价是容量翻倍、匹配误差增加，读出链路也更复杂。

第二，多比特权重不等于一个 cell 稳定保存任意多级。论文会报告 2-bit、3-bit 或更多 conductance levels，但可产品化的有效位数取决于写入分布、retention drift、read noise、temperature 和校准频率。层级越多，conductance window 越窄，可靠性越难。

第三，写入不是免费操作。ReRAM write 需要 set/reset pulse 和 verify，写入延迟、能耗与 endurance 会限制它用于频繁更新的模型。固定权重 inference 比 training 或高频在线更新更自然。

## 与 SRAM-CIM 的根本差异

SRAM-CIM 从成熟 CMOS array 出发，试图在稳定二值存储旁边加入计算。ReRAM-CIM 从可变电导出发，试图让权重本身成为计算元件。前者的工程路径更稳，后者的理论密度和 analog MVM 更吸引人。

这也决定了两者的风险位置不同。SRAM-CIM 的风险集中在面积、bitline 稳定、外围和系统收益；ReRAM-CIM 的风险从 device 层开始，包括 write variation、conductance drift、forming、retention、IR drop、sneak path 和 ADC 量化。

## 一句话理解

ReRAM 适合 CIM，不是因为它是新型非易失存储，而是因为 conductance 可以直接作为 MVM 权重进入 analog 物理计算。

## 研究启示

ReRAM-CIM 的开放问题集中在“可用电导”而不是“理想电导”：写入后能否落在目标分布，运行中能否保持，温度和时间变化后能否校准，模型能否吸收残余误差。产业实现仍处在研究样片和特定原型阶段，离大规模通用 AI accelerator 还有明显距离；它更可能先在固定权重、低更新频率、能耗极敏感的 edge 场景寻找切口。

