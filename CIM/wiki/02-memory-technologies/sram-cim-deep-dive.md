# SRAM-CIM 深入：Bitline 加和、Charge Sharing、典型 Macro 结构

上级：[02 Memory Technologies](./README.md)
相关：[SRAM-CIM 基础](./sram-cim-foundation.md), [ADC/DAC/SA in CIM](../04-circuit-and-macro/adc-dac-sa-in-cim.md), [RAM: Wordline Bitline Sense Amp](../../../RAM/wiki/02-sram-foundations/wordline-bitline-sense-amp.md)

## 这页在回答什么问题

SRAM-CIM macro 里“计算”到底发生在哪里？如果不拆 bitline、sense amplifier、local accumulator 和外围控制，就无法判断一个 macro 是真的减少了数据搬运，还是把普通数字逻辑包装成 CIM。

## 三种常见计算路径

Digital bitwise SRAM-CIM 让多行或多列数据在 read path 中完成逻辑组合，再用 sense amplifier 或局部逻辑输出结果。它适合 binary/ternary network、bit-serial multiply 和 popcount 类计算。优势是输出确定、验证路径清晰；代价是多比特乘法需要周期展开，吞吐随 bit width 和 accumulation depth 下降。

Charge-domain SRAM-CIM 利用电容和电荷共享，把多个 cell 或多条线上的状态转成电压差。它的类比是把多个小电荷桶接到同一条线上，最终水位代表局部和；精确语言是 bitline 或 capacitor network 的电荷重分布形成 analog partial sum。代价是电压 margin 有限，噪声、leakage、PVT 和 mismatch 会直接影响判决。

Current-domain SRAM-CIM 通过 read port 或 bitline current 对多个激活 cell 的电流求和。它与 ReRAM crossbar 的 “电导 × 电压 = 电流” 直觉接近，但 SRAM cell 是二值存储，多比特权重需要多 cell、多行、多周期或编码。因此它更常落在 mixed-signal，而不是 ReRAM 式高密度 analog MVM。

## 典型 macro 结构

```text
Input / activation bits
  -> WL driver / input encoder
  -> SRAM cell array
  -> BL / RBL local compute
  -> SA or low-bit ADC
  -> local accumulator
  -> tile buffer / NoC / next stage
```

真正影响 macro 指标的不是 cell array 一项，而是 WL driver、precharge、SA/ADC、local accumulator、input encoder、output buffer 和 controller。一个 256x256 或 128x128 array 的 cell 部分看起来很高效，但如果每列配高精度 ADC，面积和能耗会迅速转移到外围。

## 精度路径如何形成

SRAM-CIM 的多比特支持有三种典型方式。第一是 bit-serial，把 INT4/INT8 拆成多个 bit plane，多周期执行，外围累加；它验证友好，但 latency 和 energy 随位宽上升。第二是 bit-parallel，用更多 cell 或更宽 datapath 同时表达多个 bit；它吞吐高，但面积和布线压力上升。第三是 analog/mixed-signal accumulation，用电荷或电流一次聚合多个贡献；它节省局部加法，但把成本转移给 SA/ADC 和校准。

这解释了为什么“支持 INT8”不是一个充分指标。必须继续问：权重和激活是否都是真 INT8？是否 bit-serial 展开？partial sum 在 array 内、macro 外还是 tile 级累加？ADC/SA 的有效位数是多少？模型 accuracy 是仿真还是 silicon-backed？

## 与工艺节点的关系

Digital SRAM-CIM 可以更好跟随先进 CMOS 节点，因为逻辑、SRAM 和数字验证流程同源。Analog/mixed-signal SRAM-CIM 在先进节点上会遇到更紧的电压余量、更强 variation 和更复杂的 analog characterization。FAB wiki 的 [process nodes and PPA tradeoffs](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md) 对这个背景有更完整说明。

因此，先进节点不自动让 SRAM-CIM 更容易。digital 路线受益于密度和速度，analog 路线可能因为电压 headroom 和 mismatch 变得更难。

## 常见误解

常见误解：SRAM-CIM 比 ReRAM-CIM “保守”，所以研究价值低。实际上，SRAM-CIM 的价值在于可制造、可验证、可集成，适合把 CIM 从 macro 推向 SoC。

常见误解：8T/10T 一定比 6T 好。实际上，8T/10T 换来 read/compute 隔离，但面积增加会降低有效 TOPS/mm2 和片上容量。

常见误解：bitline 上能求和就代表系统能效高。实际上，bitline 求和只是局部收益，SA/ADC、buffer、NoC、tile 利用率会决定系统收益保留多少。

## 一句话理解

SRAM-CIM 的深水区在 bitline/read path 与外围之间的分工：越多计算压进 array，越要付出稳定性、精度和读出电路代价。

## 研究启示

SRAM-CIM 的产业状态比 ReRAM/Flash analog CIM 更接近落地，但研究仍需要回答三个问题：低位模型是否足够有商业价值，peripheral 是否被完整计入，macro 指标升到 tile/chip 后还剩多少收益。下一阶段更有价值的工作不是单宏 TOPS/W 再创新高，而是给出可复现的 macro-to-system 能耗拆解、DFT/校准方法和真实模型映射结果。

