# CIM Macro 的基本原语：Array、Driver、Sense、Accumulator

上级：[04 Circuit And Macro](./README.md)
相关：[SRAM-CIM 深入](../02-memory-technologies/sram-cim-deep-dive.md), [Digital CIM 深入](../03-compute-paradigms/digital-cim-deep-dive.md), [RAM: Wordline Bitline Sense Amp](../../../RAM/wiki/02-sram-foundations/wordline-bitline-sense-amp.md), [NoC: Reduction Networks](../../../NoC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md)

## 这页在回答什么问题

读 CIM macro 图时应该先看哪些对象？不是先看 TOPS/W，而是先定位输入、权重、局部计算、读出、量化和累加分别落在哪个电路原语上。

## Macro 的基本链路

```text
input register / encoder
  -> wordline driver / DAC / pulse generator
  -> bitcell array
  -> bitline / source line / local reduction path
  -> sense amplifier / comparator / ADC
  -> local accumulator / shift-add / output buffer
  -> macro controller
```

这个链路中，array 只是一部分。CIM 的收益来自把一部分 multiply、bitwise operation 或 reduction 推进 cell、bitline、sense path；如果计算主要发生在 output buffer 后的普通 MAC array，就不应称为 CIM。

## 原语如何对应三条 Paradigm

Analog CIM 中，wordline driver 或 DAC 把输入变成电压、脉宽或电流激励，cell conductance 或 bitline charge/current 完成局部乘加，ADC 把结果带回数字域。ReRAM crossbar 是最典型形态；Flash 可以用 threshold state 保存固定权重，但 program/verify、retention 和校准限制应用范围；PCM 有 resistance-state 潜力，却受 drift 和写入代价约束，更像研究或窄场景。SRAM charge-domain CIM 则把 SRAM bitline 当作局部累加节点。

Digital CIM 中，WL/BL/SA 路径承载 bitwise operation、XNOR、AND、popcount 或 bit-serial multiply。SRAM 最自然，因为 6T/8T/10T cell 和 CMOS peripheral 可以共同设计。MRAM 只有 read/sense path 参与 compute 时才可能进入 digital-like CIM。ReRAM/Flash 若只做 binary read 加外围 digital logic，会放弃 multi-level/current-summation 优势；只有 read/sense path 直接参与计算时，才可能算 CIM。

Mixed-signal CIM 中，array 内保留 analog 或 charge/current-domain 局部并行，SA/ADC/comparator 后转为数字校正与累加。它不是“既有 analog 又有 digital”这么宽泛，而是 analog/digital 边界切在 macro 内部。

## 四个容易误判的位置

第一，local accumulator 可以属于 CIM macro 的结果路径，但不能单独证明 CIM；关键是 accumulator 前面的 array path 是否参与计算。

第二，sense amplifier 可以只是读出电路，也可以成为计算判决的一部分。要看 SA 前的 bitline 电压/电流是否已经承载 partial sum 或 bitwise 结果。

第三，controller 和 buffer 不是免费外围。bit-serial CIM 会把复杂度转移到 sequencing、shift-add 和 partial sum storage。

第四，macro boundary 不是产品 boundary。一个 128x128 或 256x256 macro 的收益可能在 tile buffer、NoC reduction 和 host fallback 中衰减。

## 和传统 SRAM/DRAM Macro 的区别

传统 SRAM macro 的目标是可靠读写；CIM macro 的目标是让读写路径同时承担计算。这个变化会牺牲一部分读稳定性、面积、时序裕量或测试简洁性。与 RAM wiki 的 [SRAM array organization](../../../RAM/wiki/02-sram-foundations/sram-array-organization.md) 相比，CIM macro 修改的是 array 内部读出和局部归约语义，而不是只把 SRAM 当 scratchpad。

DRAM/HBM/GDDR-PIM 则是另一类问题：它是在 memory die/bank 侧加独立 processing block，不是让 DRAM cell 或 bitline 成为本页意义上的 CIM macro 原语。若 compute 放在 HBM base die、interposer 或 package-side logic，则进入 NMC 边界。macro 输出继续进入 tile reduction 时，问题会连接 NoC 的 collective/reduction 网络；工艺选择则连接 FAB wiki 的 [process nodes and PPA](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)。

## 一句话理解

CIM macro 的核心原语不是“array + accelerator”，而是 input、cell、bitline、sense path 和 accumulator 共同形成一条靠近存储的计算链路。

## 研究启示

后续研究应把 macro 图翻译成位置证据：乘法在哪里发生，累加在哪里发生，何处数字化，何处缓存，何处校准。产业实现最看重的是这条链路能否被 DFT、timing、PVT corner 和软件模型共同约束，而不是单个原语是否新颖。
