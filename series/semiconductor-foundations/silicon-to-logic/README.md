# 从硅到门电路

上级：[半导体与电路基础](../README.md)

<div id="阅读顺序"></div>

一个输入电压怎样决定电路输出 0 还是 1？从[电子到二极管](../electrons-to-diode/README.md)出发，有两条路可走。想看反向偏置的结怎样收集另一端注入的电子，可以先读下面的 [BJT](#三极管怎样放大电流并作为开关)。想弄清数字门怎样翻转，可以直接从 [MOS 的栅极与沟道](../bands-to-channel/README.md)读到 [CMOS 反相器](#cmos-门怎样用充放电实现逻辑运算)，跟着输出节点上的电荷算一次翻转要花多少[时间](../fanout-and-wire-delay/README.md)和[能量](../switching-energy-and-power/README.md)。

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

在常见的硅 MOSFET 中，掺杂形成源区和漏区。MOSFET 的全称是金属–氧化物–半导体场效应晶体管。栅极隔着介质建立电场，改变硅表面的载流子浓度。当源区与漏区之间形成导电沟道时，源、漏两端的压差可以驱动电流。

<details markdown="1">
<summary>从沟道的形成读到漏极电流与器件规格</summary>

### 用平面 NMOS 观察沟道怎样形成

以增强型平面 NMOS 为例。器件有栅极 G、源极 S、漏极 D 和体端 B。两个重掺杂 N 型区形成源区和漏区，位于 P 型体区中。栅极和硅之间由薄的介质隔开。对本例，令体端与源极同电位，漏极电位略高于源极。

逐步提高栅极电压时，栅极电场先从硅表面排开部分空穴，形成耗尽区。电场进一步增强时，电子在表面聚集。表面从以空穴为主变为以电子为主，称为**反型**。在强反型且漏源电压较小时，电子沟道将源区和漏区连起来。

[![平面增强型 NMOS 的两种状态。低栅源电压下源区和漏区由 P 型体区隔开。较高的栅源电压在栅介质下方形成反型沟道，电子沿沟道由源区移向漏区。](./img/nmos-channel.svg)](./img/nmos-channel.svg)

*截面为教学示意。两幅图均以源极为参考，省略体端接触和边缘电场。下图假设漏源电压较小，强反型沟道延伸至漏区。*

定义 V<sub>GS</sub> = V<sub>G</sub> − V<sub>S</sub>，V<sub>DS</sub> = V<sub>D</sub> − V<sub>S</sub>。在上述 NMOS 方向下，电子从源极移向漏极，常规漏极电流 I<sub>D</sub> 从漏极流向源极。PMOS 使用空穴沟道，常用正值 V<sub>SG</sub> = V<sub>S</sub> − V<sub>G</sub> 表示栅驱动。提高 V<sub>SG</sub> 会增强 PMOS 的沟道导电能力。见 [MIT 6.004 的 MOSFET 结构与端口特性](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c3/c3s1/)。

### 漏极电流随端电压怎样变化

用一个长沟道 NMOS 的一阶模型。设体端与源极相连，V<sub>DS</sub> ≥ 0，温度固定。模型沿沟道采用恒定的迁移率和阈值，忽略亚阈值电流、沟道长度调制和串联电阻。以 V<sub>TN</sub> 表示 NMOS 阈值，V<sub>ov</sub> = V<sub>GS</sub> − V<sub>TN</sub> 表示过驱动电压。系数 k = μ<sub>n</sub>C<sub>ox</sub>W/L，C<sub>ox</sub> 是单位面积栅介质电容，W 和 L 是沟道宽度和长度。

| 模型工作区 | 条件 | 漏极电流 I<sub>D</sub> |
| --- | --- | --- |
| 截止 | V<sub>ov</sub> ≤ 0 | 近似为零。 |
| 线性区 | V<sub>ov</sub> > 0 且 0 ≤ V<sub>DS</sub> < V<sub>ov</sub> | k(V<sub>ov</sub>V<sub>DS</sub> − V<sub>DS</sub><sup>2</sup>/2)。 |
| 饱和区 | V<sub>ov</sub> > 0 且 V<sub>DS</sub> ≥ V<sub>ov</sub> | kV<sub>ov</sub><sup>2</sup>/2。 |

在线性区靠近 V<sub>DS</sub> = 0 的范围，沟道近似一个电阻，约为 1/(kV<sub>ov</sub>)。这个区间适合用来分析低压降开关的稳态导通。

当 V<sub>DS</sub> 增至 V<sub>ov</sub>，漏端的强反型沟道开始**夹断**。源端仍向沟道供应电子，电子穿过漏端的高电场区被收集。理想模型中的 I<sub>D</sub> 由栅源电压决定。实际饱和区的 I<sub>D</sub> 也可随 V<sub>DS</sub> 增加。见 [MIT 6.012 的长沟道 MOSFET 大信号模型](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2009/resources/mit6_012f09_lec11/)。

例如，取 V<sub>TN</sub> = 0.3 V、V<sub>GS</sub> = 0.8 V、k = 200 µA/V²，得到 V<sub>ov</sub> = 0.5 V。在 V<sub>DS</sub> = 0.1 V 时，模型得到 I<sub>D</sub> = **9 µA**。在 V<sub>DS</sub> = 0.5 V 或 0.8 V 时，理想饱和电流均为 **25 µA**。这些数值来自指定模型和假设。

### 看规格时，先看测量条件

- **转移特性**固定 V<sub>DS</sub> 等条件，扫描 V<sub>GS</sub>，观察 I<sub>D</sub>。某个工作点的跨导 g<sub>m</sub> 是固定其他端电压时 I<sub>D</sub> 对 V<sub>GS</sub> 的局部斜率，单位为西门子（S）。
- **输出特性**对多个固定的 V<sub>GS</sub>，分别扫描 V<sub>DS</sub>，得到一组 I<sub>D</sub> 曲线。用作低损耗开关时，关注规定栅驱动和温度下的导通电阻 R<sub>DS(on)</sub>。
- **输入电容与栅电荷**描述驱动电路在切换时需要转移的电荷。绝缘栅极的稳态漏电通常很小。每次改变栅极电压，驱动电路仍需提供瞬态电流。

例如，Nexperia 2N7002 在结温 25 °C、V<sub>DS</sub> = V<sub>GS</sub>、I<sub>D</sub> = 0.25 mA 时，测得的栅源阈值规格范围为 1.0–2.5 V。同为 25 °C，导通电阻最大值 5.3 Ω 对应 V<sub>GS</sub> = 4.5 V 和 I<sub>D</sub> = 75 mA。前一个测试定义小电流门限，后一个测试才给出指定负载和栅驱动下的导通电阻。见 [Nexperia 2N7002，Rev. 7，表 7 与图 5–7](https://assets.nexperia.com/documents/data-sheet/2N7002.pdf#page=5)。

实际器件还要考虑亚阈值电流、体偏置改变阈值、源漏与体区之间的 PN 结、寄生电容及短沟道效应。上面的一阶式适合解释趋势。预测特定工艺中的电流和延迟，要使用对应的器件模型与工作条件。器件结构演化见 [FAB 的 Planar、FinFET 与 GAAFET](../../chip-development/FAB/wiki/02-front-end-fabrication/transistor-evolution-planar-finfet-gaa.md)。

</details>

## CMOS 反相器与逻辑门 {#cmos-门怎样用充放电实现逻辑运算}

把 PMOS 和 NMOS 接到同一个输出节点，可以控制这个节点的充放电。静态 CMOS 门用 PMOS 建成**上拉网络**，用 NMOS 建成**下拉网络**。分析门的输出时，先判断哪条路径会接通，再判断节点电压会怎样变化。

<details markdown="1">
<summary>沿上拉和下拉路径推导反相器、NAND 与 NOR，再算一次翻转的能量</summary>

### 用两只管构成反相器

反相器的 PMOS 源极接 V<sub>DD</sub>，NMOS 源极接 GND。两个栅极接输入，两个漏极接输出。在常见体硅 CMOS 中，这两个器件的体端分别接 V<sub>DD</sub> 和 GND。以下过程假设供电和输入满足器件的正常工作条件，输出接等效电容负载 C<sub>L</sub>。

[![CMOS 反相器。输入接两只晶体管的栅极，输出是两只管共用的漏极节点。PMOS 把输出接到电源，NMOS 把输出接到地，负载电容从输出接到地。](./img/cmos-inverter.svg)](./img/cmos-inverter.svg)

*黑点表示电气连接。图中的 C<sub>L</sub> 代表下一级输入和连线等效到输出节点的电容，体端连接见正文。*

| 输入 | 管子状态 | 稳态输出 |
| --- | --- | --- |
| 0 | PMOS 导通，NMOS 截止。 | 1 |
| 1 | PMOS 截止，NMOS 导通。 | 0 |

稳定后，逻辑 1 的电压接近 V<sub>DD</sub>，逻辑 0 的电压接近 GND。

输入设置两只管子的栅极电压。输入从高变低时，电荷从 V<sub>DD</sub> 经 PMOS 流入输出节点。输入从低变高时，输出节点通过 NMOS 向 GND 放电。

<div id="用电压电流电阻和电容描述一个节点"></div>
<div id="电容把电流换算成电压变化"></div>

对图中接地的线性负载电容，输出节点一侧的电荷 **Q = C<sub>L</sub>·V<sub>out</sub>**。忽略其他电流路径，按基尔霍夫电流定律（KCL），流入电容的净电流为上拉电流 I<sub>P</sub> 减去下拉电流 I<sub>N</sub>。净电流为正时，输出节点一侧的电荷增加，电压升高。净电流为负时，电荷减少，电压降低。电压变化所需的时间见[电路与时序基础](../../microarchitecture/02-pipeline/electrical-timing-foundations.md)。

### 用串联和并联推导 NAND 与 NOR

对于两输入静态 CMOS 门，A 和 B 各控制一只 PMOS 和一只 NMOS。串联支路要求每个开关都导通，并联支路只需有一个支路导通。

| 门 | 上拉和下拉的接法 | 输出何时为 0 |
| --- | --- | --- |
| NAND（与非） | PMOS 并联，NMOS 串联。 | A 和 B 都为 1。 |
| NOR（或非） | PMOS 串联，NMOS 并联。 | A 和 B 至少有一个为 1。 |

以 A = 1、B = 0 为例。NAND 的 B 控制管关断了串联下拉，B 同时使一个并联上拉支路导通，输出为 1。对同样输入，NOR 的 A 控制管打开一个并联下拉支路，同时断开串联上拉，输出为 0。

| 输入 (A, B) | NAND | NOR |
| --- | --- | --- |
| (0, 0) | 1 | 1 |
| (0, 1) | 1 | 0 |
| (1, 0) | 1 | 0 |
| (1, 1) | 0 | 0 |

在 NAND 或 NOR 后再接一级反相器，就分别得到 AND 或 OR。分析这条路径时，要计入两级的负载与传播延迟。见 [MIT 6.004 的互补网络和组合门](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c3/c3s1/)。

### 电压落在哪个范围，逻辑值才有效

缓慢扫描输入电压并等待输出稳定，可以得到反相器的电压传输曲线。输入接近两个电源轨时，输出分别接近相反的电源轨。中间过渡区可能出现两只管同时导通，输出由两边的电流平衡决定。

| 电平参数 | 在规定的供电、温度和负载条件下 |
| --- | --- |
| V<sub>IL</sub>、V<sub>IH</sub> | 接收端保证识别为低电平的最高输入电压，以及保证识别为高电平的最低输入电压。两者之间的逻辑结果无保证。 |
| V<sub>OL</sub>、V<sub>OH</sub> | 驱动端输出低电平时的最高保证电压，以及输出高电平时的最低保证电压。 |

一对兼容的驱动端和接收端应有正的直流噪声容限。低电平容限为 V<sub>IL</sub> − V<sub>OL</sub>，高电平容限为 V<sub>OH</sub> − V<sub>IH</sub>。例如，若本例的低电平输出上限为 0.10 V，接收低电平上限为 0.25 V，低电平容限为 **0.15 V**。该值只描述所选端口条件下的静态余量。

器件的 V<sub>TN</sub> 用于描述单个 NMOS 的导电。门电路的直流翻转点可用传输曲线上 V<sub>in</sub> = V<sub>out</sub> 的点定义。传播延迟则按约定的输入和输出参考门限计量。分析时应分别取相应的器件参数、接口电平和时序库门限。见 [MIT 6.004 的数字抽象与电平规范](https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/pages/c2/c2s1/)。

### 翻转消耗的能量来自哪里

在理想全摆幅的充放电模型中，输出每次从 0 V 升至 V<sub>DD</sub>，电源向 C<sub>L</sub> 送入 C<sub>L</sub>V<sub>DD</sub> 的电荷，提供能量 C<sub>L</sub>V<sub>DD</sub><sup>2</sup>。其中一半暂存在电容里，一半在上拉路径耗散。随后放电时，存下的能量在下拉路径耗散。

设 f 是每秒的周期数，α 是每周期平均发生的 **0 → 1** 次数，则该节点平均负载切换功率为 P<sub>sw</sub> = αfC<sub>L</sub>V<sub>DD</sub><sup>2</sup>。例如，反相器负载为 50 fF，供电为 0.8 V。电源每次全摆幅充电提供 **32 fJ**。若 f = 1 GHz，平均每四周期发生一次上升，则 P<sub>sw</sub> = **8 µW**。实际门还会消耗两管同时导通时的短路能量、内部节点翻转能量和漏电功率。见 [MIT 6.012 的 CMOS 延迟与功耗](https://ocw.mit.edu/courses/6-012-microelectronic-devices-and-circuits-fall-2009/resources/mit6_012f09_lec16_scaling/)。

</details>

<div id="接下来怎么读"></div>

## 用到哪里

想把一个上升沿画到时间轴上，可从[电容充电到时钟边沿](../voltage-to-clock/README.md)算出输出电压越过门限需要多久。想在一块硅片上找回输入、输出和两根电源线，可以对照[反相器的实物剖面与封装](../inverter-to-package/README.md)。

也可以从这个反相器向里或向外追一步。向里看[栅极怎样控制硅表面的电荷](../bands-to-channel/README.md)，向外看[一组节点的翻转怎样累加成芯片功耗](../switching-energy-and-power/README.md)。

- **时序。** 从输出节点充放电继续算到寄存器的采样边沿。见[电路与时序基础](../../microarchitecture/02-pipeline/electrical-timing-foundations.md)。
- **运算。** 从基本逻辑门进入部分积和累加电路。见[从部分积到 MAC](../../microarchitecture/01-datapath/multiply-accumulate-from-gates.md)。
- **存储。** 从两个反相器维持状态，读到访问管怎样连接存储节点与位线。见 [6T SRAM cell](../../storage/02-sram/foundations/6t-cell-bistable-storage.md)和 [1T1C DRAM](../../storage/03-dram/foundations/1t1c-cell-destructive-read.md)。
- **前道工艺。** 从材料特性进入掺杂、注入和栅极结构。见[掺杂与离子注入](../../chip-development/FAB/wiki/02-front-end-fabrication/doping-and-ion-implantation.md)和[器件演化](../../chip-development/FAB/wiki/02-front-end-fabrication/transistor-evolution-planar-finfet-gaa.md)。
