# 数据编码：Bit-Serial、Binary、Unary、Stochastic

上级：[04 Circuit And Macro](./README.md)
相关：[Digital CIM 深入](../03-compute-paradigms/digital-cim-deep-dive.md), [Precision and Quantization](./precision-and-quantization-at-circuit.md), [Software: Quantization for CIM](../06-software-stack/quantization-for-cim.md)

## 这页在回答什么问题

同样标称 INT4 或 INT8，为什么不同 CIM macro 的面积、周期、能耗和误差完全不同？因为数据编码决定输入如何进入 array、权重如何放进 cell、partial sum 如何形成，以及外围要补多少账。

## 四类常见编码

Binary encoding 用少量 bit 表达数值，密度高，适合 digital CIM 和 SRAM bit-serial 路线。代价是多比特乘法需要 bit-plane 展开、shift-add 和更宽 accumulator。

Unary encoding 用多个相同权重的单位表示数值，线性和鲁棒性好，适合某些 analog 或 stochastic 方案。代价是面积、周期或脉冲数增加，难以支撑高精度大模型。

Bit-serial encoding 把 activation 或 weight 拆成多个 bit plane，多周期送入 array。它让 SRAM digital CIM 更容易实现可变精度，但 latency 和 energy 随位宽上升。

Stochastic encoding 用 bitstream 的概率表达数值，乘法可以变简单，但需要长 bitstream 才能降低方差。它在研究中有价值，产品化受吞吐、随机源和验证成本限制。

## 三条 Paradigm 的编码差异

Analog CIM 的编码要把数字输入变成电压、脉宽、脉冲次数或电流，并把权重映射成 conductance、threshold 或 charge state。ReRAM/Flash 适合 multi-level 或 differential encoding，但 write-verify、drift 和 device variation 会限制可用状态数。

Digital CIM 的编码以 bit plane、binary/ternary、XNOR-popcount 和 bit-serial 为主。SRAM 最自然，因为 cell 保存离散 bit，local logic 处理离散 partial sum。它的关键问题是多周期展开后，是否仍比外部 MAC 更省。

Mixed-signal CIM 常把输入或权重的一侧离散化，另一侧保留 analog 局部并行。例如输入 bit-serial，阵列内 charge/current accumulation，输出经低比特 ADC 后数字累加。这个路线的难点是把编码、ADC range 和 accumulator 宽度统一设计。

## 编码和 Memory Technology 的错配

ReRAM/Flash 如果只按纯 binary digital 方式使用，会放弃 multi-level state 和 current summation 的核心优势。SRAM 如果追求高精度 analog multi-level weight，则需要多 cell、多周期或高精度外围，容易失去 CMOS 工程优势。DRAM/HBM/GDDR-PIM 的数据格式由 PIM instruction、bank/channel 粒度和 memory command 决定，不属于本页 CIM macro 编码主线；相关背景可连接 RAM wiki 的 [HBM stacked wide-IO](../../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md) 和 [DRAM row/column/sense path](../../../RAM/wiki/04-dram-foundations/row-column-decode-sense-amplify.md)。若这些格式通过 host-visible command 或 memory-mapped interface 暴露，还需要按 BUS wiki 的 [interconnect components](../../../BUS/wiki/04-microarchitecture-integration/interconnect-components.md) 评估接口成本。

PCM 可以表达多级 resistance，但 drift、write-verify 和温度敏感性会让编码状态随时间变差。MRAM 更接近 binary reliable storage；若 read/sense path 参与比较或局部归约，可以做 digital-like CIM，但不适合作为 ReRAM 式 multi-level analog 编码主线。

## 读论文时的记录模板

| 字段 | 要问的问题 |
| --- | --- |
| activation encoding | bit-serial、bit-parallel、pulse-width 还是 voltage-level |
| weight encoding | binary、ternary、multi-level、differential 还是 replicated |
| partial sum | 在 bitline、SA 后、local accumulator 还是 tile 级形成 |
| signed value | 用 differential cell、offset、two's complement 还是后处理 |
| zero / sparsity | 是否真的跳过能耗，还是只跳过数字累加 |

## 一句话理解

数据编码不是格式细节，而是 CIM macro 把模型数值翻译成电路行为的合同；它决定周期、面积、误差和外围开销。

## 研究启示

研究应同时报告模型量化格式和电路编码格式，不能用 “INT8 support” 掩盖 bit-serial 周期、multi-cell weight、ADC range 和 partial sum 宽度。产业实现更偏低比特、可校准、可编译映射的编码，而不是只在单层网络上有效的精巧表示。
