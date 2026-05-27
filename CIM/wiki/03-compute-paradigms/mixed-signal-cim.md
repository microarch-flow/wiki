# Mixed-Signal CIM：在哪一段切换、为什么切换

上级：[03 Compute Paradigms](./README.md)
相关：[Analog CIM 深入](./analog-cim-deep-dive.md), [Digital CIM 深入](./digital-cim-deep-dive.md), [Peripheral Overhead](../04-circuit-and-macro/peripheral-overhead.md)

## 这页在回答什么问题

为什么真实 CIM 设计很少是“纯 analog”或“纯 digital”？因为 array 内物理并行有价值，但系统最终需要数字控制、可校准精度、可编程数据流和可验证接口，切换边界决定了收益和风险。

## Mixed-Signal 的基本边界

```text
digital input/control
  -> analog/charge/current-domain local compute in array
  -> SA / ADC / comparator
  -> digital correction / accumulation / scheduling
```

这个边界可以放得很靠近 cell，也可以放在 column、subarray、macro 或 tile。越晚数字化，analog 局部并行保留越多，但误差、噪声和校准压力越大；越早数字化，精度和验证更稳，但 analog CIM 的能效优势被削弱。

## 主要落在哪些 memory 上

ReRAM-CIM 的现实落点常是 mixed-signal：crossbar 内 analog MVM，外围做 ADC、差分编码、数字校正和多 tile accumulation。SRAM-CIM 也常落在 mixed-signal：bitline charge/current-domain 做局部累加，SA/ADC 和数字 accumulator 完成判决与累加。Flash CIM 用 cell 状态保存 analog weight，但必须依赖数字校准和后处理。

PCM mixed-signal 可以把 resistance state 用作 analog 权重，再用数字校正补偿 drift，但写入能耗、write-verify 和长期漂移让它更适合研究样片或窄场景。MRAM mixed-signal 只有在 read/sense path、comparator、SA offset correction 或 local reduction 直接参与 compute 时才有 CIM 意义；普通 MRAM + 外围数字逻辑不算 mixed-signal CIM。

DRAM/HBM/GDDR-PIM 不属于本章 mixed-signal CIM 纵轴。PIM 系统中当然有 analog PHY、sense path 和 digital processing，但它不是 array-native CIM 的 mixed-signal 切换问题。

## 为什么 mixed-signal 容易美化指标

Mixed-signal 设计最容易把“阵列内计算”报告得很漂亮，再把 ADC、DAC、reference、buffer、controller、calibration、digital accumulation 分散到其他模块里。如果论文或产品材料没有统一统计口径，读者会高估 analog 部分收益。

评估 mixed-signal CIM 时要问：输入在哪里变成 analog？输出在哪里数字化？ADC 是每列、共享还是分时？数字校正要多少 SRAM/register？calibration 频率多高？tile 间 partial sum 是否仍要走 NoC？

## 工程意义

Mixed-signal 不是折中口号，而是职责切分。一个好的边界会把物理最擅长的局部并行留在 array，把精度敏感和控制复杂的部分交给数字逻辑。一个差的边界会同时继承 analog 的校准难度和 digital 的面积开销。

## 一句话理解

Mixed-signal CIM 的核心问题是 analog/digital 边界放在哪里；边界决定能效、精度、校准、验证和系统可扩展性。

## 研究启示

Mixed-signal CIM 的研究应把边界作为一等对象报告，而不是只写 “array + ADC”。产业上，最可行的设计往往会牺牲一部分理想 analog 能效，换取低位可控精度、可测试性和软件可建模性；这也是 SRAM-CIM 和 ReRAM-CIM 从论文走向产品时绕不开的方向。
