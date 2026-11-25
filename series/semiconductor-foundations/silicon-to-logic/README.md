# 从硅到门电路

上级：[半导体与电路基础](../README.md)

<div id="阅读顺序"></div>

一个输入电压怎样决定电路输出 0 还是 1？从[电子到二极管](../electrons-to-diode/README.md)出发，有两条路可走。想看反向偏置的结怎样收集另一端注入的电子，可以先读下面的 [BJT](#三极管怎样放大电流并作为开关)。想弄清数字门怎样翻转，可以直接从 [MOS 的栅极与沟道](../bands-to-channel/README.md)读到 [CMOS 反相器](../cmos-logic-gates/README.md#inverter)，跟着输出节点上的电荷算一次翻转要花多少[时间](../fanout-and-wire-delay/README.md#load)和[能量](../fanout-and-wire-delay/README.md#energy)。

从门电路继续，还可以追一拍时钟的来路。先看[放大级](../transistor-amplifier/README.md)怎样补回[石英振荡回路](../quartz-oscillator/README.md)的损耗，再看[触发器怎样采样和二分频](../latch-and-divider/README.md)，以及 [PLL 怎样利用分频反馈倍频](../integer-pll/README.md)。芯片能用多快的时钟，还受[本地供电压降](../ir-drop-and-decoupling/README.md)以及[工艺、电压、温度对路径延迟的影响](../pvt-and-path-delay/README.md)约束。

## 硅晶体里的电子 {#从硅的四个价电子理解-p-型和-n-型掺杂}

<span id="硅原子如何成键"></span>从一个原子的[电子状态](../electrons-to-diode/README.md#states)开始，再看许多硅原子形成晶体后，[能带怎样形成、电子能占据哪些状态](../electrons-to-diode/README.md#bands)。

## 从掺杂读到电流 {#p-型与-n-型掺杂}

<span id="磷提供电子硼提供空穴"></span><span id="电子和空穴从哪里来"></span>在硅中换入一个磷或硼原子，哪些电荷固定在晶格中，哪些还能移动？跟着电子的位置读[施主、受主与载流子](../electrons-to-diode/README.md#doping)。

<span id="载流子怎样形成电流"></span>电子一直在运动，穿过一个截面的净电流却可以为零。怎样计算两个方向的差别，见[电子的漂移与扩散](../electrons-to-diode/README.md#transport)。

## PN 结为什么会整流 {#pn-结如何形成势垒二极管如何整流}

- <span id="耗尽区怎样形成"></span><span id="平衡时扩散和漂移怎样抵消"></span>**两区接触以后。** 从电子净扩散造成的电荷变化，读到[耗尽区怎样达到平衡](../electrons-to-diode/README.md#equilibrium)。
- <span id="电子能进去耗尽区为什么还能保持"></span>**电子走进结区。** 从 N 区走向 P 区时，沿途的[电场和势垒](../electrons-to-diode/README.md#field)怎样变化？
- <span id="外加电压怎样改变结电流"></span><span id="先选参考点和方向"></span><span id="正接时多数载流子持续跨结"></span>**P 端接正极。** 势垒略微降低，为什么[跨过结的电子会多出许多](../electrons-to-diode/README.md#forward)？
- <span id="反接时充稳后只剩少量漏电"></span>**P 端接负极。** 读[反偏下的电流](../electrons-to-diode/README.md#reverse)，区分刚换接电源时的电流与稳定后的漏电。
- <span id="pn-结也会储存电荷"></span>**改变偏压。** 哪些区域的电荷要重新分布？读[储存电荷与结电容](../electrons-to-diode/README.md#storage)。

## 双极型晶体管（BJT） {#三极管怎样放大电流并作为开关}

双极型晶体管（BJT）有两个 PN 结，共用一个很薄的**基区**。在正向放大区，发射结向基区注入载流子，集电结收集穿过基区的载流子。如果基区厚度远小于注入载流子的扩散长度，**大部分注入基区的载流子能到达集电极**。这是 BJT 能提供电流增益的原因之一。电路中常说的「三极管」在这里指 BJT。

<details markdown="1">
<summary>跟着一个电子穿过 NPN 管，再用负载检查放大与饱和</summary>

### 三个端子决定两个结的偏置

以 NPN 管为例。发射极 E 接在重掺杂 N 型发射区，基极 B 接在薄的 P 型基区，集电极 C 接在 N 型集电区。定义 V<sub>BE</sub> = V<sub>B</sub> − V<sub>E</sub>，V<sub>BC</sub> = V<sub>B</sub> − V<sub>C</sub>。PNP 管交换 P 型和 N 型区域，偏置和常规电流方向也相应反转。

[![正向放大的 NPN 示意。电子由重掺杂 N 型发射区注入薄 P 型基区，大部分越过基区，被反偏的集电结收集到 N 型集电区。](./img/npn-injection.svg)](./img/npn-injection.svg)

*图中箭头表示电子运动方向。区域宽度仅作示意。*

在正向放大区，发射结正偏，集电结反偏。发射区把电子注入基区。大部分电子扩散到集电结，再被该处的电场扫入集电区。部分电子在基区与空穴复合，基极电流负责补充空穴。空穴从基区注入发射区的过程也贡献基极电流。见 [MIT 6.012 的 BJT 注入与收集模型](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2009/resources/mit6_012f09_lec07/)。

### 从端口看工作区

下表假设器件避开击穿。电流取 NPN 正向使用时的大小。

| 工作区 | 发射结和集电结的偏置 | 可用的近似 |
| --- | --- | --- |
| 截止 | 发射结反偏或正偏很弱，集电结反偏或零偏。 | 集电极电流接近漏电量级。 |
| 正向放大 | 发射结正偏，集电结反偏。 | 固定温度、低注入时，I<sub>C</sub> 对 V<sub>BE</sub> 近似呈指数关系。给定工作点附近，也可用 I<sub>C</sub> ≈ βI<sub>B</sub>。 |
| 饱和 | 两个结均正偏。 | V<sub>CE</sub> 通常较小，集电极电流需与外部负载一起求解。 |
| 反向放大 | 发射结反偏，集电结正偏。 | 集电区承担注入。常规器件的发射区和集电区结构不同，反向增益通常较低。 |

β 随器件、温度和偏置而变。工程上可以用基极电流估算集电极电流，内部注入同时取决于 V<sub>BE</sub>。硅 BJT 的 V<sub>BE</sub> 应随电流和温度一起给出。用作饱和开关时，关断还要移除基区的储存电荷。

### 用负载检查一次开关状态

<div id="电阻把压差换算成支路电流"></div>

设发射极接地，集电极经 1 kΩ 电阻接 3.3 V 电源。基极驱动由外部电路提供。流过这个线性电阻的电流等于两端的压差除以阻值。因此 I<sub>C</sub> = (3.3 V − V<sub>CE</sub>) / 1 kΩ。

1. 若假设 β = 100、I<sub>B</sub> = 10 µA，正向放大模型给出 I<sub>C</sub> ≈ 1 mA，V<sub>CE</sub> ≈ 2.3 V。取教学工作点 V<sub>BE</sub> ≈ 0.7 V，集电极高于基极，满足集电结反偏的条件。
2. 若 I<sub>B</sub> 增至 0.4 mA，沿用 β = 100 会得到 40 mA。即使 V<sub>CE</sub> 降为零，电阻也只能提供 3.3 mA。应检查饱和工作点。若本例取 V<sub>CE(sat)</sub> ≈ 0.2 V，则 I<sub>C</sub> ≈ **3.1 mA**。

这里的参数是供手算使用的假设。实际开关要根据负载电流与基极驱动查规格。例如 onsemi 的 2N3904 在 I<sub>C</sub> = 10 mA、I<sub>B</sub> = 1 mA、环境温度 25 °C 的脉冲测试中，给出 V<sub>CE(sat)</sub> 最大值 0.2 V。另一个电流测试点有不同上限。见 [onsemi 2N3904/D，Rev. 3，第 2 页](https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf#page=2)。

</details>

## MOSFET 与沟道电流 {#mosfet-如何用栅极电压控制沟道电流}

MOSFET 的栅极与硅之间隔着绝缘层。栅极能改变硅表面的电子分布，形成连接源、漏的沟道。在同一只平面 NMOS 上，把栅压和漏压分开调，就能看清电荷从哪里来，又沿哪条路走。[MOS 管怎样隔着绝缘层控制电流？](../bands-to-channel/README.md)

- <span id="用平面-nmos-观察沟道怎样形成"></span>**先只调栅压。** 源、漏同电势，沟道里可以已有电子，稳态源漏净电流仍为零。[看绝缘栅下的耗尽和反型](../bands-to-channel/README.md#隔着绝缘层加电压)
- <span id="漏极电流随端电压怎样变化"></span>**再只调漏压。** 整条金属栅极接同一根引线，沿着沟道，栅极相对于当地沟道的电压却在变化。跟着电子从[源端走向漏端](../bands-to-channel/README.md#channel-voltage)，再看[漏端夹断后电流怎样延续](../bands-to-channel/README.md#pinch-off)。
- <span id="看规格时先看测量条件"></span>**读电流要带上测试条件。** 用一个小电流定义的阈值与规定负载下的导通电阻，要分别查对应的栅压、漏压和温度。对照[一只器件的阈值与导通电阻测试条件](../bands-to-channel/README.md#specs)。

## CMOS 反相器与逻辑门 {#cmos-门怎样用充放电实现逻辑运算}

一只接地的 NMOS 可以给输出放电。它关断后，谁把已经放掉的电荷补回来？把 PMOS 的源极接到电源，共用一个输入，电路就有了另一条充电路径。[两只 MOS 管怎样组成一个逻辑门？](../cmos-logic-gates/README.md)

- <span id="用两只管构成反相器"></span>**接好两只管。** 在输入高、低两种情况下分别沿导通路径走一遍，推出[反相器的输出](../cmos-logic-gates/README.md#inverter)。
- <span id="用电压电流电阻和电容描述一个节点"></span><span id="电容把电流换算成电压变化"></span>**跟着电荷走。** 流入输出节点的净电流改变负载电荷。给定电容，再用 Q = CV 换算成[输出电压随时间的变化](../cmos-logic-gates/README.md#edge)。
- <span id="用串联和并联推导-nand-与-nor"></span>**增加第二个输入。** 在四组输入下，逐一查通向电源与地的路径，由此得到[NAND 与 NOR 的真值表](../cmos-logic-gates/README.md#nand-nor)。
- <span id="电压落在哪个范围逻辑值才有效"></span>**连接下一级。** 测到输出端处于某个电压，后面的门会把它读成几？用[输入和输出的电压范围](../cmos-logic-gates/README.md#levels)检验两级之间的噪声裕量。
- <span id="翻转消耗的能量来自哪里"></span>**算一次充放电。** 分清电源提供、负载暂存和导通路径耗散的能量。见[一次翻转的能量](../cmos-logic-gates/README.md#energy)。

<div id="接下来怎么读"></div>

## 用到哪里

想把一个上升沿画到时间轴上，可从[电容充电到时钟边沿](../voltage-to-clock/README.md)算出输出电压越过门限需要多久。想在一块硅片上找回输入、输出和两根电源线，可以对照[反相器的实物剖面与封装](../inverter-to-package/README.md)。

也可以从这个反相器向里或向外追一步。向里看[栅极怎样控制硅表面的电荷](../bands-to-channel/README.md)，向外看[一组节点的翻转怎样累加成芯片功耗](../fanout-and-wire-delay/README.md#activity)。

- **时序。** 从输出节点充放电继续算到寄存器的采样边沿。见[电路与时序基础](../../microarchitecture/02-pipeline/electrical-timing-foundations.md)。
- **运算。** 从基本逻辑门进入部分积和累加电路。见[从部分积到 MAC](../../microarchitecture/01-datapath/multiply-accumulate-from-gates.md)。
- **存储。** 从两个反相器维持状态，读到访问管怎样连接存储节点与位线。见 [6T SRAM cell](../../storage/02-sram/foundations/6t-cell-bistable-storage.md)和 [1T1C DRAM](../../storage/03-dram/foundations/1t1c-cell-destructive-read.md)。
- **前道工艺。** 从材料特性进入掺杂、注入和栅极结构。见[掺杂与离子注入](../../chip-development/FAB/wiki/02-front-end-fabrication/doping-and-ion-implantation.md)和[器件演化](../../chip-development/FAB/wiki/02-front-end-fabrication/transistor-evolution-planar-finfet-gaa.md)。
