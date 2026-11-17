# 存储介质与求值方式的交叉检查

<span class="micro-legacy-anchor" id="三种-paradigm-三种-memory哪些组合是主流哪些罕见为什么"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>
<span class="micro-legacy-anchor" id="crossmap"></span>
<span class="micro-legacy-anchor" id="三个主流组合"></span>
<span class="micro-legacy-anchor" id="罕见组合为什么罕见"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>
<span class="micro-legacy-anchor" id="研究启示"></span>


上级：[阵列求值与信号转换](./README.md)

同一种介质可以支持不同求值方式。读到一个组合时，应检查编码、计算路径和外围成本，不能凭“主流”或“罕见”标签判定可行性。

## 交叉检查表

| 介质 | 模拟求值需要核查 | 数字求值需要核查 | 宏级混合信号边界 |
| --- | --- | --- | --- |
| SRAM | 多行激活、电流或电荷如何累积，误差怎样传播 | bitwise、bit-serial、popcount 的读出与归约 | SA/ADC、数字累加和控制是否计入 |
| ReRAM | 电导编码、阵列非理想性、写入验证 | 读取路径是否参与离散求值，或只是供给独立 ALU | 转换、校准、差分编码和部分和合并 |
| Flash | 电荷状态、读出精度与权重更新 | 具体感测或逻辑机制，不能由器件名推断 | 编程、转换、数字校准及控制 |
| PCM | 电阻状态、漂移与温度依赖 | 离散状态读取与运算路径 | 漂移补偿、转换与累加 |
| MRAM | 可区分状态和实际读出方案 | 阵列或 sense path 如何参与求值 | 比较、感测和数字结果处理的边界 |

表中是问题清单，不声称每个组合已有相同成熟度的产品。具体器件实例见[介质章节](../02-memory-technologies/README.md)。模拟阵列与 mixed-signal 宏可以同时描述同一设计的不同层级。

## 独立 CU 单列

DRAM/HBM/GDDR 的独立 PIM 处理单元，用指令、算术资源、局部存储和接口描述。普通 PHY 包含模拟电路，不足以把整个系统称为 mixed-signal 求值宏。分类口径见[计算位置与术语](../01-overview/cim-pim-nmc-taxonomy.md)。

## 怎样使用这张表

先画输入编码、存储、求值、转换、累加和输出路径，再逐项查证对应的电路与实验。性能与能量的比较还要固定任务、精度和包含成本，查阅入口见[路线速查](../02-memory-technologies/memory-tech-comparison-matrix.md)。
