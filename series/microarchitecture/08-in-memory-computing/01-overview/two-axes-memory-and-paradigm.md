# 存储介质与求值方式：两个不同的坐标

<span class="micro-legacy-anchor" id="两条正交主线memory-technology-compute-paradigm"></span>
<span class="micro-legacy-anchor" id="这页在回答什么问题"></span>
<span class="micro-legacy-anchor" id="交叉矩阵"></span>
<span class="micro-legacy-anchor" id="为什么两条轴必须同时出现"></span>
<span class="micro-legacy-anchor" id="与其他-wiki-的连接"></span>
<span class="micro-legacy-anchor" id="一句话理解"></span>


上级：[问题、术语与分类](./README.md)

存储介质决定状态如何保存与读取；求值方式决定操作数如何形成计算结果。两者需要分别描述，因为同一种存储可以采用不同电路，同一种电路思路也可以落在不同存储介质上。


<span class="micro-legacy-anchor" id="横轴memory-technology"></span>

## 介质告诉我们什么

SRAM 保存锁存状态；ReRAM、PCM 等器件可以利用电阻或电导状态；Flash 使用电荷状态；DRAM 依赖动态存储与刷新。具体可用精度、写入方式和保持条件要看器件及电路，不能从“非易失”推出容量、精度或能效。

各路线的详细机制和限制由[存储介质与计算路径](../02-memory-technologies/README.md)展开，本页不重复器件比较表。


<span class="micro-legacy-anchor" id="纵轴compute-paradigm"></span>

## 求值方式告诉我们什么

| 观察对象 | 记录方式 | 需要解释的机制 |
| --- | --- | --- |
| 阵列求值为模拟 | analog | 电流、电荷、电压等连续量如何编码输入、权重和累积结果 |
| 阵列求值为数字 | digital | bitwise、bit-serial、popcount 等如何产生离散结果 |
| 宏包含模拟与数字处理 | mixed-signal | 转换在哪里发生，ADC/DAC、数字控制和累加分别占什么成本 |

Analog array 与 mixed-signal macro 可以同时成立，因为观察层级不同。把两者作为互斥标签，会漏掉转换成本。数字路径也要统计位串行周期、局部累加、面积和时序，并非只有模拟路径有外围开销。

## 独立处理单元怎么记录

若方案使用与 cell 分离的 PIM/NMC 处理单元，记录其指令、数值格式、算术资源和存储接口。它可以使用数字逻辑，但“数字处理单元”不等于本专题口径下的 digital CIM。术语范围统一见[计算位置与命名口径](./cim-pim-nmc-taxonomy.md)。

## 从坐标走向工程判断

先记录具体介质，再确认阵列参与哪一步，最后画出输入编码、阵列求值、转换、累加和输出路径。然后计算每一步的周期、字节和能量。精简查阅矩阵见[路线对照](../02-memory-technologies/memory-tech-comparison-matrix.md)；按求值机制展开的文章见[阵列求值与信号转换](../03-compute-paradigms/README.md)。

这是一种阅读与建模方法，不声明哪条路线在整个产业中占主流，也不把器件兼容性等同于完整产品成熟度。
