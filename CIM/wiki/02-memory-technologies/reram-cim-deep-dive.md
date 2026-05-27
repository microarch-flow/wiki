# ReRAM-CIM 深入：Crossbar 结构、IR Drop、Sneak Path

上级：[02 Memory Technologies](./README.md)
相关：[ReRAM 作为计算元件](./reram-as-compute-element.md), [Analog CIM 深入](../03-compute-paradigms/analog-cim-deep-dive.md), [ADC/DAC/SA in CIM](../04-circuit-and-macro/adc-dac-sa-in-cim.md)

## 这页在回答什么问题

ReRAM crossbar 的 MVM 原理很简洁，为什么产品化却很难？因为真实阵列不是理想电阻矩阵，线阻、旁路电流、器件漂移、写入误差和 ADC/DAC 开销会把“物理完成 MAC”的优势逐层侵蚀。

## Crossbar MVM 的理想图

```text
        column current
          |
V0 -> [G00] [G01] [G02]
V1 -> [G10] [G11] [G12]
V2 -> [G20] [G21] [G22]

I_col_j = sum_i(V_i * G_ij)
```

理想模型把每个 cell 看成一个精确电导，把每条 wordline 看成无阻抗输入，把每条 bitline 看成理想电流汇合点。这个模型足以解释 ReRAM-CIM 的吸引力，但不足以评估芯片。

## ReRAM 在三种 Paradigm 下的落点

ReRAM-CIM 的主线是 analog，因为 conductance state 与 column current summation 正好对应 MVM。Digital ReRAM-CIM 可以把 ReRAM 当非易失 binary storage，再在 read path 或外围做 bitwise/digital compute，但这样会削弱 multi-level conductance 和 array-native summation 的核心优势；如果计算完全离开 array path，它也不应被称为 CIM。

Mixed-signal 是产品化更现实的落点：crossbar 内保留 analog MVM，crossbar 外用 ADC、数字校正、差分编码、分块累加和 mapping 补偿误差。后文讨论 IR drop、sneak path 和 ADC 时，默认是在解释为什么理想 analog MVM 必须被 mixed-signal system 包起来才可能可用。

## IR Drop 为什么是核心问题

Crossbar 尺寸增大后，wordline 和 bitline 的线阻不再可忽略。同一行输入电压沿线下降，不同位置 cell 看到的实际电压不同；同一列电流汇聚时也会在 bitline 上产生压降。这会让矩阵中的同一个数值权重因为物理位置不同而产生不同有效贡献。

阵列越大，并行度越高，但 IR drop 越严重。缩小阵列可以降低误差，却增加 peripheral、tile 数量和 interconnect 开销。这是 ReRAM-CIM 的典型 trade-off：不能只追求大 crossbar，也不能把阵列切得过碎。

## Sneak Path 与选择器问题

在无选择器或弱选择器 crossbar 中，未被目标路径选中的 cell 也可能形成旁路电流。Sneak path 会污染读出值，降低 conductance state 的可分辨性，并增加 standby/read 能耗。选择器、1T1R、1S1R 和 bias scheme 可以抑制旁路，但会牺牲密度、工艺复杂度或操作电压窗口。

这说明 ReRAM-CIM 的高密度优势不是免费获得的。每引入一个 selector 或 access transistor，都在用面积和制造复杂度换取可读性。

## ADC/DAC 不只是外围细节

ReRAM array 输出是 analog current，进入数字系统前必须量化。低精度 ADC 可以保留能效优势，但模型精度和 accumulation range 受限；高精度 ADC 会快速吃掉面积和能耗。论文报道的 macro 能效如果没有包含 DAC、ADC、sample/hold、reference generation、calibration 和 digital accumulation，就不能用于系统比较。

一个经验判断是：当目标精度从 4-bit 走向 8-bit 等效精度时，analog CIM 的外围代价会显著上升，理想阵列并行性的优势会被压缩。具体数字依设计不同变化很大，但“ADC 精度每上升一档，能耗和面积非线性上升”是读论文时必须检查的趋势。

## 误差如何传到模型

ReRAM-CIM 的误差不是单一噪声项，而是一条链：

```text
write variation
  -> conductance distribution
  -> IR drop / sneak path / read noise
  -> ADC quantization
  -> partial sum error
  -> layer output error
  -> model accuracy loss
```

工程上可用的方案需要在这条链上多点补偿：write-verify、差分编码、小阵列切分、reference calibration、variation-aware mapping、QAT 或 noise-aware training。只给出理想 SPICE 或小阵列 measured MVM 结果，不能证明系统成立。

## 与 3D 集成的关系

ReRAM-CIM 常被放进 3D integration 的研究叙事中，因为非易失阵列和 logic 可以在垂直方向更紧密结合。这个方向与 FAB wiki 的 [3DIC fundamentals](../../../FAB/wiki/04-back-end-packaging/3d-routes/3dic-fundamentals.md) 和 [TSV](../../../FAB/wiki/04-back-end-packaging/3d-routes/tsv-through-silicon-via.md) 共享封装与互连背景。但 3D 集成解决的是距离和密度问题，不会自动消除 device variation、写入和读出误差。

## 一句话理解

ReRAM-CIM 的理想 MVM 来自 crossbar 物理定律，真实难点来自同一张 crossbar 的非理想物理：线阻、旁路、漂移、写入误差和转换电路。

## 研究启示

ReRAM-CIM 的高价值研究应把 device、array、ADC 和 model accuracy 放在同一个评估闭环中。只优化 cell 或只报告 MVM kernel 不够；需要说明 array size 为什么这样选、IR drop 如何建模、sneak path 如何抑制、ADC 能耗是否计入、模型是否做了硬件感知训练。产业上，这条路线的短期机会更像 edge fixed-weight inference，而不是需要频繁权重更新和高精度的通用 LLM accelerator。
