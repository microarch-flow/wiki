# CIM 专用的量化策略：低比特、非对称、Calibration 的特殊性

上级：[06 Software Stack](./README.md)
相关：[Precision at Circuit](../04-circuit-and-macro/precision-and-quantization-at-circuit.md), [Data Encoding Strategies](../04-circuit-and-macro/data-encoding-strategies.md), [RAM: SRAM Cell](../../../RAM/wiki/02-sram-foundations/6t-cell-bistable-storage.md), [FAB: Process Nodes](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md), [BUS: AXI Attributes](../../../BUS/wiki/04-microarchitecture-integration/axi-attributes-cacheability-barrier.md)

## 这页在回答什么问题

CIM 量化为什么不能只问 INT8 还是 INT4？因为最终可用精度由模型量化、输入编码、cell state、ADC/SA、partial sum、校准和硬件误差共同决定。

## 三层精度

模型层精度描述训练/推理图中的数值格式。电路层精度描述 cell、driver、ADC、SA 和 accumulator 能稳定表达的值。系统层精度描述 mapping、tile reduction 和 fallback 后的任务 accuracy。

把这三层混在一起会产生误判。一个 macro 可以有 8-bit ADC，但有效位数受 noise、variation 和 calibration 限制；一个 digital SRAM-CIM 可以支持 INT8，但 bit-serial cycle 和 accumulator width 会改变吞吐与能耗。

## 三条 Paradigm 的量化差异

Analog CIM 适合低比特和硬件感知量化。ReRAM/Flash 的 multi-level state、differential encoding、ADC range 和 conductance drift 要进入量化搜索；高等效精度需要证明 ADC/DAC 和 calibration 成本仍可接受。

Digital CIM 更接近传统整数推理，但 bit slicing、popcount、bit-serial expansion 和 local accumulator 会改变性能模型。它对 INT4/INT8 更稳，代价是面积和周期。

Mixed-signal CIM 需要联合设计 analog range 与 digital correction。scale、zero-point、saturation、outlier handling 和 tile-level accumulation 不能只由软件量化器独立决定。

Memory technology 也会改变量化边界。ReRAM/Flash 的 multi-level state 有表达优势，但 write-verify、drift 和 ADC range 会限制有效状态数；SRAM binary cell 使 digital bit-plane 更自然；PCM 有 resistance-state 潜力但受 drift 和 programming cost 限制；MRAM 更适合作为 binary/read-sense-path compute，不适合当成 ReRAM 式 multi-level analog 权重。

DRAM/HBM/GDDR-PIM 的量化属于 PIM compute unit 的数据格式和 memory-side command 约束，不是 CIM macro 的 cell/ADC 精度问题。HBM base die、interposer 或 package-side compute 属于 NMC，量化边界更接近 accelerator tensor format、DMA 可见格式和 package bandwidth。

## 非对称与校准

非对称量化常带来 zero-point 处理。数字硬件可以用加法和偏置处理；analog CIM 可能需要 offset current、reference shift、差分编码或额外校正。每种方式都会改变 array 能耗或外围复杂度。

Calibration 不只是 post-training quantization 的统计步骤。CIM calibration 还包括 ADC reference、cell conductance、temperature drift、bad column 和 tile health。量化工具需要知道校准参数何时生成、存在哪里、是否会随运行时间变化。

host-visible tensor format 也要一致。若 runtime、DMA 或 fallback 单元看到的是 INT8 tensor，而 CIM macro 内部使用 bit-serial、differential pair 或 asymmetric scale，compiler 必须在边界插入 format conversion，并按 BUS/cacheability/ordering 规则管理可见数据。

## 常见误解

常见误解：QAT 后 accuracy 够高，就说明 CIM 可部署。实际上，QAT 必须使用和硬件一致的 error model、ADC saturation、mapping fragmentation 和 calibration policy，否则只能证明软件假设成立。

常见误解：低比特一定适合 CIM。实际上，低比特降低 ADC 和 accumulator 压力，但如果模型层敏感、fallback 增多或重训练成本高，端到端收益仍可能消失。

## 一句话理解

CIM 量化是模型数值、电路精度和系统映射的联合约束，不是单独选择一个 bit-width。

## 工具链启示

量化工具要接收硬件 profile：ADC/SA bit、cell state count、noise model、accumulator width、supported encoding、scale granularity 和 calibration state。输出不应只有 quantized weights，还应包含 per-layer/per-tile scale、saturation policy、fallback mark 和 retraining/validation 报告。
