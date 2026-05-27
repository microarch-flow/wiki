# 精度与量化在电路层的实现约束

上级：[04 Circuit And Macro](./README.md)
相关：[Data Encoding Strategies](./data-encoding-strategies.md), [Analog vs Digital Tradeoff Map](../03-compute-paradigms/analog-vs-digital-tradeoff-map.md), [RAM: SRAM Applications](../../../RAM/wiki/03-sram-applications/README.md), [NoC: Reduction Networks](../../../NoC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md)

## 这页在回答什么问题

为什么论文里写 INT8、4-bit ADC 或 6-bit weight 仍然不够？因为模型精度、存储状态、输入编码、array accumulation、ADC 量化和数字 partial sum 宽度是不同层级的精度，不能混成一个数字。

## 精度的五个层级

```text
model numeric format
  -> stored weight state
  -> input drive precision
  -> array accumulation precision
  -> ADC / SA / digital accumulator precision
```

模型层的 INT8 不代表 cell 保存 8-bit 权重，也不代表单次 array 输出有 8-bit 有效精度。很多 CIM macro 通过 bit-serial、多 cell、重复读、数字 shift-add 或 calibration 拼出等效精度。

## 三条 Paradigm 的精度来源

Analog CIM 的有效精度受 device variation、IR drop、noise、ADC bit、reference 和 calibration 共同限制。低比特固定模型更自然；高精度需要多次读出、差分编码、数字补偿或更重 ADC。

Digital CIM 的精度由 bit-width、cycle count 和 accumulator width 决定。它更容易给出 deterministic worst-case，但 INT8/FP8 支持会增加周期、局部寄存器、routing 和 accumulator 面积。

Mixed-signal CIM 的精度来自边界协同：array 内保留低比特 analog 局部并行，数字端做校正、累加和范围管理。它的核心问题是 ADC range、quantization scale 和模型 QAT 是否同口径设计。

## Quantization 不是软件后处理

CIM 的量化必须下沉到电路约束。scale 是否对称、zero-point 是否需要 offset current、signed weight 是否用 differential pair、outlier 是否触发 saturation、partial sum 是否溢出，都会改变 macro 设计。

对于 ReRAM/Flash，multi-level state 的可分辨数量和 drift 决定 weight quantization 的真实上限。对于 SRAM，bit-serial 周期和 accumulator 宽度决定精度代价，相关存储背景可对照 RAM wiki 的 [SRAM applications](../../../RAM/wiki/03-sram-applications/README.md)。对于 DRAM/HBM/GDDR-PIM，量化约束来自 PIM compute unit 的数据格式和 memory-side bandwidth，而不是 CIM macro 的 cell/bitline 精度；若 compute 位于 HBM base die、interposer 或 package-side logic，则属于 NMC 边界。partial sum 离开 macro 后还会进入 tile reduction 和互连，可连接 NoC wiki 的 [reduction networks](../../../NoC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md)。

## 常见误解

常见误解：ADC 是 8-bit，所以 macro 有 8-bit 精度。实际上，ADC 只是读出链路的一环；input drive、cell state、array noise、offset、calibration 和 accumulator 都会降低有效位数。

常见误解：模型能 QAT，就能吸收任何硬件误差。实际上，QAT 只能吸收统计上稳定、可建模的误差；温漂、retention、随机 write noise 和 aging 仍需要硬件校准或运行时保护。

常见误解：peak precision、effective number of bits 和 model accuracy 是同一件事。实际上，peak precision 是电路或格式宣称的上限，effective precision 是带非理想性后的数值质量，model accuracy 是 workload 对这些误差的最终响应。三者必须分开报告。

## 一句话理解

CIM 的精度是模型、编码、器件、array、ADC 和数字累加共同形成的有效精度，不是某个 bit 数标签。

## 研究启示

高质量研究应报告有效精度链路：权重状态数、输入编码、ADC bit、accumulator width、校准方式、模型 accuracy 和 corner 条件。产业上，可接受的路线不是追求最高 nominal bit-width，而是在可测试、可校准、可编译的范围内闭合误差预算。
