# Analog CIM 深入：非理想性、噪声源、Device Variation、温度漂移

上级：[03 Compute Paradigms](./README.md)
相关：[Analog CIM 基础](./analog-cim-fundamentals.md), [ReRAM-CIM 深入](../02-memory-technologies/reram-cim-deep-dive.md), [Non-Idealities](../04-circuit-and-macro/non-idealities-and-error-sources.md)

## 这页在回答什么问题

Analog CIM 的理论模型很干净，真实芯片为什么难？因为计算结果不再是布尔逻辑，而是受器件、阵列、外围和环境共同影响的模拟分布。

## 非理想性分层

```text
device: conductance variation / drift / retention / write noise
array: IR drop / sneak path / coupling / line resistance
circuit: DAC error / ADC quantization / SA offset / reference noise
system: calibration drift / mapping mismatch / model accuracy loss
```

在 ReRAM-CIM 中，device 层的 conductance 分布和 drift 是核心；在 SRAM charge/current-domain CIM 中，PVT、read disturb、bitline mismatch 和 sense margin 更关键；在 Flash CIM 中，threshold drift、program variation 和长期 retention 更突出。

## Analog Paradigm 的 Memory 落点

Analog CIM 最自然落在 ReRAM 和 Flash，因为 cell state 可以表达多级权重，array current summation 可以直接形成 MVM。SRAM 只能在 charge-domain 或 current-domain 中做低比特局部累加，二值 cell 本身不擅长保存多级 analog weight，所以 multi-bit 权重需要编码、重复访问或外围累加。

PCM 有 analog resistance state，但 resistance drift、写入能耗、write-verify 和温度敏感性让它更像特定研究路线，而不是 analog CIM 主线。MRAM 的主流优势是二值非易失和可靠读写，不是稳定多级 conductance；只有读出路径或 sense path 被用于计算时才可能进入 CIM，且更偏 digital-like 或 mixed-signal。DRAM/HBM/GDDR-PIM 的主线是 memory-side digital processing，不是把 1T1C cell 或 HBM stack 改造成 analog MAC，因此不属于本页 analog CIM 主线。

## 精度瓶颈不是单个 bit 数

论文里写 “4-bit input, 4-bit weight, 8-bit output” 不代表系统有 8-bit 有效精度。有效精度取决于输入 DAC、cell state、array accumulation、ADC、数字累加和校准后的误差预算。Analog CIM 的高位往往由外围和多周期数字补偿形成，而不是单次阵列物理计算自然给出。

这也是 analog CIM 与 digital CIM 的根本差异：digital 的误差主要来自离散设计错误、timing、fault 或量化策略；analog 的误差本身是运行时数值路径的一部分。

## 温度和时间为什么危险

Analog CIM 的权重和读出行为会随时间与温度变化。ReRAM conductance drift、Flash threshold shift、PCM resistance drift、SRAM leakage 和 sense offset 都会让同一输入在不同时间得到不同结果。离线校准只能覆盖出厂或启动时状态，长期运行需要决定是否在线校准、多久校准一次、校准参数存在哪里、校准能耗是否吞掉收益。

如果目标是车载、工业或 always-on edge，温区、寿命和 worst-case 行为比平均 TOPS/W 更重要。一个常温 demo 能跑，不等于产品能跨温区稳定交付。

## 系统补偿的代价

常见补偿手段包括 differential encoding、write-verify、reference calibration、小阵列切分、redundancy、variation-aware mapping、QAT 和 noise-aware training。每种补偿都在把硬件问题转移到面积、时间、软件或模型训练成本上。

最危险的指标写法是只给补偿后的 accuracy，却不报告补偿成本。对架构判断来说，校准时间、额外存储、重复写入次数、ADC sharing、重训练成本都应计入系统代价。

## 一句话理解

Analog CIM 的难点是把模拟分布变成可部署的数字结果；非理想性不是边缘噪声，而是这条路线的核心系统变量。

## 研究启示

Analog CIM 的研究前沿应从“误差存在”走向“误差预算闭环”：device 测量、array 仿真、ADC 模型、mapping 策略和模型 accuracy 必须连起来。产业实现的真实状态是低比特、固定模型、可校准场景更有机会；高精度、动态权重和大规模通用 LLM 路线仍需要强证据。
