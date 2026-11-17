# SRAM-CIM

## 路线定位

SRAM-CIM 通常是最接近 CMOS 量产和 SoC 集成的一条路线。

如果把多条 CIM 路线放在一起比较，SRAM-CIM 往往不是理论能效最激进的，但它通常是工程上最容易落地、最容易和现有数字系统耦合的一条路线。

## 为什么它重要

SRAM 本来就是现代 SoC 中最常见的片上存储形式之一，因此 SRAM-CIM 的优势不只在“能不能算”，还在于：

- 更容易接入现有 `CMOS` 工艺
- 更容易与 `MCU / NPU / AI SoC` 集成
- 速度快，读写延迟短
- 工程团队更容易做验证、测试和量产

这也是为什么很多面向 edge AI 的 CIM 方案，会优先从 SRAM 路线切入。

## 常见实现思路

SRAM-CIM 并不只有一种做法，常见上可以分成三类：

### 1. Digital SRAM-CIM

主要使用位运算、bit-serial 数据路径或局部数字累加。

特点：

- 精度可控
- 验证难度较低
- 更像把轻量计算单元推进到存储宏附近

### 2. Charge-domain SRAM-CIM

利用电荷共享或电容上的电荷累积进行计算。

特点：

- 能效较高
- 设计复杂度上升
- 对噪声和工艺偏差更敏感

### 3. Current-domain SRAM-CIM

利用 bitline 电流或相关模拟效应进行局部乘加。

特点：

- 并行性强
- 需要更认真处理读出链路和 ADC 开销
- 更接近 mixed-signal 路线

## 重点问题

- 使用 `6T / 8T / 10T` 哪类 bitcell
- 是 charge-domain、current-domain 还是 digital 方案
- 支持 `INT1 / INT4 / INT8` 的方式是什么
- ADC 是否必须存在
- 如何与片上 NPU 或 buffer 连接

## SRAM-CIM 的典型优点

- 工艺成熟，和标准数字芯片流程更兼容
- 与片上 buffer、DMA、NoC 更容易协同
- 对 edge inference、always-on AI 比较友好
- 适合做固定算子加速，如 MVM、dot product、bitwise op

## SRAM-CIM 的典型限制

- 面积大，单位容量成本不低
- 容量有限，难以像 DRAM / HBM 一样承载大模型权重
- leakage 较高，不适合单纯依赖超大规模片上存储取胜
- 如果外围 ADC、buffer、controller 太重，系统收益会被吃掉

## 适合的应用场景

| 场景 | 适配度 | 原因 |
| --- | --- | --- |
| Edge AI | 高 | 功耗约束强，模型规模相对可控 |
| MCU / TinyML | 高 | 适合小模型和定制算子 |
| Mobile / IoT | 中高 | 适合集成式低功耗推理 |
| Data center LLM | 低到中 | 受容量限制，通常不足以独立承载大模型 |

## 研究和评估时要特别注意

### bitcell 选择

`6T` 更紧凑，但可能更难兼顾稳定存储和计算路径；`8T / 10T` 往往更容易支持解耦读写和计算，但面积代价更大。

### 精度实现方式

很多论文会写支持 `INT4 / INT8`，但需要进一步拆开看：

- 权重和激活是否都是真多比特
- 多比特是否依靠 bit-serial 展开
- 结果精度是否受 ADC 或累加路径限制

### 系统集成方式

SRAM-CIM 宏很少独立存在，通常要看它如何接入：

- 上游 buffer
- tile controller
- 片上 interconnect
- host NPU 或 CPU

## 关键指标

## 关键指标

- TOPS/W 或 TFLOPS/W
- area efficiency
- bit precision
- macro size
- leakage / active power

## 读论文时建议新增记录项

- bitcell 类型
- 阵列大小
- 是否需要 ADC
- 输入 / 权重编码方式
- 是 macro 指标还是 chip 指标
- 对模型精度的影响

## 后续可补充内容

- 宏结构图
- 代表论文时间线
- 工艺节点对比
