# Analog CIM：用电流/电压代表乘累加结果

上级：[03 Compute Paradigms](./README.md)
相关：[Analog CIM 深入](./analog-cim-deep-dive.md), [ReRAM 作为计算元件](../02-memory-technologies/reram-as-compute-element.md), [ADC/DAC/SA in CIM](../04-circuit-and-macro/adc-dac-sa-in-cim.md)

## 这页在回答什么问题

Analog CIM 为什么在概念上如此吸引人？因为它把乘法和累加映射到物理定律：输入用电压、脉冲或电荷表示，权重用电导、阈值或电荷状态表示，求和由 bitline 或 column current 自然完成。

## Analog CIM 的基本执行链

```text
digital activation
  -> DAC / pulse / WL driver
  -> cell conductance or charge state
  -> current / voltage / charge accumulation
  -> SA / ADC
  -> digital partial sum
```

理想 analog CIM 的收益来自省掉大量显式数字乘法器和加法树。ReRAM crossbar 中，`I = V * G` 对应乘法，列电流求和对应 dot product；SRAM current-domain 或 charge-domain CIM 中，多行激活后的 bitline 电流/电荷变化对应局部累加；Flash CIM 中，浮栅状态和读电流对应固定权重推理。

## 主要落在哪些 memory 上

ReRAM 是 analog CIM 最自然的 memory，因为 conductance state 可以直接表达权重，crossbar column current 可以直接表达 MVM。Flash 也适合固定权重 analog CIM，因为 cell 阈值或电荷状态可表达多级权重。SRAM 也能做 current-domain 或 charge-domain analog/mixed-signal compute，但 SRAM cell 是二值存储，multi-bit 权重需要多 cell、多周期或外围编码，所以它不如 ReRAM 自然。

DRAM/HBM/GDDR-PIM 不是 analog CIM 主线。DRAM cell/bitline charge sharing 的 in-DRAM logic 研究存在，但这属于特定 DRAM-CIM 研究，不是 02 章定义的 DRAM-PIM。

## 为什么 analog 不是“免费 MAC”

Analog CIM 省掉的是局部数字乘加，不省掉输入编码、读出、量化、校准和系统归约。ADC 是最典型的反噬点：4-bit 级 ADC 可以保留一部分能效优势，8-bit 级等效精度会让面积、功耗和速度压力迅速上升。论文中若只报告 array energy，不包含 DAC、ADC、sample/hold、reference、buffer 和 controller，就不能外推系统收益。

Analog CIM 的另一个代价是输出不是确定数字值，而是带噪声、漂移和位置依赖误差的模拟量。device variation、IR drop、thermal noise、temperature drift、retention drift 会把硬件误差传到模型输出，因此 analog CIM 往往需要 QAT、noise-aware training 或 calibration。

## 常见误解

常见误解：analog CIM 一定比 digital CIM 能效高。实际上，analog 的优势集中在低精度、局部阵列和高复用场景；高精度 ADC 和系统外围会缩小甚至反转优势。

常见误解：analog CIM 等于 ReRAM-CIM。实际上，ReRAM 是最自然落点，但 SRAM charge/current-domain 和 Flash analog CIM 也属于 analog/mixed-signal 空间。

常见误解：阵列里完成 MVM 就代表系统完成推理。实际上，softmax、normalization、activation、routing、fallback 和 host synchronization 仍可能主导端到端性能。

## 一句话理解

Analog CIM 的本质是用物理连续量完成局部乘加；它的收益来自 array 内并行，代价集中在转换、误差、校准和系统集成。

## 研究启示

Analog CIM 的开放问题不是证明电流能相加，而是证明带有 ADC、DAC、variation、温漂和模型补偿的完整链路仍然有系统收益。研究应同时报告 array-level 与 macro-level 指标，并明确是否包含外围、目标精度、模型 accuracy 和 silicon measurement。

