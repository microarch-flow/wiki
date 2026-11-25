# 阵列求值与信号转换

<span class="micro-legacy-anchor" id="03-compute-paradigms"></span>


上级：[存内与近存计算](../README.md)

## 这页在回答什么问题

上一章把同一个点积放到不同介质上。这一章先固定两项输入和权重，看**加法发生在哪里，哪一步第一次得到可以移位、传送的数字**。把输入 2 和 3 写成二进制，阵列先看它们的低位，再看高位。两次列读数本身还不是答案。只有知道每次读取代表哪一位，才能把它们合成 23。[回看不同存储单元的读出路径](../02-memory-technologies/README.md)

## 本章的纵轴

读电路图时，可以分两步。先看阵列怎样形成局部结果，再看外围怎样把它交给下一步。这样，一颗宏在阵列里做模拟加法，在列末做模数转换，在数字端做加法，这些描述就能同时成立。[存储介质与求值方式](../01-overview/two-axes-memory-and-paradigm.md)

| 观察哪一步 | 沿电路追踪什么 |
| --- | --- |
| [模拟求值](./analog-cim-fundamentals.md) | 输入用电压、脉冲等信号激励阵列，乘积以电流或电荷等物理量参与求和。需要知道读数的单位、零点、量程和误差。ReRAM、Flash 和部分 SRAM 均有相应实现。 |
| [数字求值](./digital-cim-fundamentals.md) | 例如 SRAM 在阵列读路径得到按位结果，再统计多少位为 1、恢复位权。部分 MRAM 也能在双行感测时判断布尔函数。要计入局部逻辑、布线和逐位执行的拍数。 |
| [混合信号实现](./mixed-signal-cim.md) | 在同一计算宏里标出哪一段用连续量求值、在哪里判决或量化、哪些工作接着由数字逻辑完成。转换器、校准和结果归并都会耗时耗能。 |

有感放的普通存储器也会将模拟信号判成数字位。区分它与本章的计算宏，要看多个操作数是否已经在阵列或读出路径中参与求值。若 DRAM 普通读出后把数字送到 bank 旁的独立处理单元，乘加发生在那个单元。本系列把这种实现放在 [DRAM/HBM-PIM](../02-memory-technologies/dram-pim-foundation.md) 讨论。

<span class="micro-legacy-anchor" id="推荐阅读顺序"></span>

## 阅读顺序

1. [把输入拆成两个位平面，模拟阵列怎样算出 23？](./analog-cim-fundamentals.md)　先读低位平面，再读高位平面，按各自的位权合并两次转换的结果。
2. [同一个输入反复读，怎样找出部分和里的误差？](./analog-cim-deep-dive.md)　先把同一个输入读几遍，再换一组输入，检查哪些误差能由这两种观测区分。
3. [阵列每列只输出一位，怎样靠计数算出 2×4 + 3×5？](./digital-cim-fundamentals.md)　从两列的按位与数出有几个 1，再按输入位和权重位的位置累加。
4. [六组位平面要算几拍，换成负数又怎样累加？](./digital-cim-deep-dive.md)　先排出六组位平面占用的计算资源，再给补码的符号位带上负权。
5. [Mixed-Signal CIM](./mixed-signal-cim.md)：array 内 analog/charge/current 计算，外围数字转换与校正；SRAM、ReRAM、Flash；边界复杂，外围开销容易被低估。
6. [Analog vs Digital](./analog-vs-digital-tradeoff-map.md)
7. [存储介质与求值方式的交叉检查](./paradigm-memory-crossmap.md)

<span class="micro-legacy-anchor" id="一句话理解"></span>
<span class="micro-legacy-anchor" id="研究启示"></span>

读完可以用一张宏的框图自查。圈出第一个局部和，标明它是电流、电压、电荷还是数字码。再沿线找到量化、校正、移位和跨块归并的位置。到这里，论文里的精度损失、外围面积和 TOPS/W 各自覆盖哪段电路，就有了可以核对的边界。
