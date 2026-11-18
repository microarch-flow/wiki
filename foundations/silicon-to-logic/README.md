# 从硅到门电路

芯片用连续的电压和电流传递离散的 0 与 1。要理解这层抽象，可以从两个问题入手。**什么决定电流？什么把下一级的输入推到有效电平？** 前一个问题涉及载流子和晶体管，后一个问题涉及门电路和负载电容。

这一组文章为时序、存储和前道工艺提供共同基础。读完后，可以沿一个 CMOS 反相器的输出节点，解释数字翻转的电荷从哪里来、经过哪条路径，以及为什么需要时间。

## 阅读顺序

1. [电压、电流、电阻与电容](./circuit-quantities.md) 用电路方程解释支路电流和节点充电。
2. [硅晶格、载流子与 P/N 型掺杂](./silicon-and-doping.md) 从硅的四个价电子理解共价键、电子、空穴和电导率。
3. [PN 结与二极管](./pn-junction.md) 追踪扩散、耗尽区、内建电场和偏置下的电流。
4. [双极型晶体管（BJT）](./bipolar-transistor.md) 看两个 PN 结如何在同一个薄基区内配合，形成放大器或开关。
5. [MOSFET 与沟道电流](./mosfet.md) 看栅极怎样建立沟道，并读懂阈值、导通电阻和 I–V 曲线。
6. [CMOS 反相器与逻辑门](./cmos-logic.md) 从上拉和下拉路径推导反相器、与非门和或非门的输出。

晶体管是一类器件。电路中常说的「三极管」通常指双极型晶体管（BJT）。MOS 管通常指金属–氧化物–半导体场效应晶体管（MOSFET）。理解 BJT 有助于理解载流子注入。搭建静态 CMOS 逻辑时，直接使用的是 NMOS 和 PMOS 两种 MOSFET。

## 用到哪里

- **计算门延迟。** 从输出节点的充放电继续读，算出电压越过参考门限的时刻，再引入寄存器和采样边沿。见[电路与时序基础](../../series/microarchitecture/02-pipeline/electrical-timing-foundations.md)。
- **理解 1 bit 怎样保存。** 看两个反相器怎样维持状态，以及访问管怎样连接存储节点与位线。见 [6T SRAM cell](../../series/storage/02-sram/foundations/6t-cell-bistable-storage.md)和 [1T1C DRAM](../../series/storage/03-dram/foundations/1t1c-cell-destructive-read.md)。
- **理解硅片怎样做出晶体管。** 从材料特性进入掺杂、注入和栅极结构。见[掺杂与离子注入](../../series/chip-development/FAB/wiki/02-front-end-fabrication/doping-and-ion-implantation.md)和[器件演化](../../series/chip-development/FAB/wiki/02-front-end-fabrication/transistor-evolution-planar-finfet-gaa.md)。
