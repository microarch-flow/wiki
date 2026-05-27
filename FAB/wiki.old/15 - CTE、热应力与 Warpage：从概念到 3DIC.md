# CTE、热应力与 Warpage：从概念到 3DIC

上级：[[00 - 先进封装 Wiki 索引]]

相关：[[08 - 3D IC]]、[[09 - W2W 与 D2W]]、[[10 - 共性工程问题]]、[[14 - 为什么台积电领先先进封装]]

## 为什么要先学这个

很多人一开始学 3DIC，会先盯着：

- micro-bump
- hybrid bonding
- TSV
- pitch
- 带宽

但真正进入量产之后，最容易卡住系统的经常不是“能不能连上”，而是：

- 会不会翘
- 会不会裂
- 热循环后还能不能活
- 堆叠后应力会不会把低 k、RDL、bump、bonding interface 搞坏

这些问题的底层都和 `CTE mismatch`、热应力、warpage 有关。

## 1. 什么是 CTE

CTE = `Coefficient of Thermal Expansion`，热膨胀系数。

直观理解：

材料升温会膨胀，降温会收缩。CTE 描述的就是：

`温度每变化 1 度，这种材料的尺寸会变化多少`

如果两种材料的 CTE 不一样，但它们又被硬连在一起，那么升温或降温时，它们就会互相拉扯。

这就是后面所有热机械问题的起点。

## 2. 为什么先进封装里 CTE 问题特别严重

因为先进封装不是一种材料，而是很多材料层层叠起来：

- silicon die
- Cu
- SiO2 / low-k / passivation
- polymer dielectric
- underfill
- mold compound
- substrate
- solder / micro-bump
- lid / TIM

这些材料的 CTE、模量、厚度、玻璃化转变温度都不同。

在先进封装里，温度变化来源很多：

- 制造加热
- bonding / reflow
- underfill / molding 固化
- 测试温循
- 实际工作时的 self-heating

所以封装不是静态结构，而是在不停经历热加载。

## 3. CTE mismatch 会带来什么

### 3.1 局部应力

材料想膨胀/收缩，但被旁边材料约束，就会产生局部应力。

### 3.2 翘曲

如果整体结构上下不对称，或者各层收缩不一致，整个 package 会弯起来，这就是 warpage。

### 3.3 疲劳与裂纹

如果热循环很多次，应力会在薄弱点积累，最后表现为：

- solder fatigue
- RDL cracking
- delamination
- via / trace 失效
- low-k 层损伤
- 键合界面失效

## 4. 在 3DIC 里为什么更敏感

3DIC 比普通封装更敏感，主要因为它同时具备下面几个特征。

### 4.1 die 很薄

3D 堆叠通常要求薄化。die 变薄以后，刚性下降，更容易形变，也更怕应力集中。

### 4.2 互连 pitch 更细

pitch 越细，对位窗口越小，对微小形变越敏感。

### 4.3 垂直堆叠让热更难出去

热更难排走，局部热点更强，温度梯度更复杂。

### 4.4 堆叠结构里 repair 成本更高

平面封装某个 bump 失效已经很麻烦；3D 堆叠里一层出问题，整 stack 可能都受影响。

## 5. 先分清三个概念：CTE、热应力、warpage

### CTE

是材料属性。

### 热应力

是不同材料受热后彼此约束产生的力学响应。

### warpage

是热应力在整体结构尺度上的外在表现之一。

一句话：

`CTE mismatch 是原因，热应力是中间机制，warpage 是常见结果。`

## 6. 它在 3DIC 里具体影响哪些东西

### 6.1 影响 bonding 良率

不管是 micro-bump 还是 hybrid bonding，对平整度、coplanarity、对位都很敏感。warpage 一大，bonding window 就变窄。

### 6.2 影响互连可靠性

热循环会让：

- 微凸点
- Cu pillar
- RDL trace
- TSV 邻近区域
- hybrid bonding interface

承受反复应力。

### 6.3 影响器件内部 BEOL / low-k

高应力不仅伤封装，也可能把器件本体内部脆弱层带坏，尤其先进逻辑里的 low-k 和超细金属层。

### 6.4 影响测试与组装窗口

warpage 太大，会直接影响：

- 贴装
- underfill
- 测试接触
- 后续板级组装

## 7. 为什么 3DIC 里“硅对硅”反而是个优势

这点很关键。

如果两层主要堆叠对象都是 silicon die，那么它们之间的 CTE 更匹配，堆叠界面本身的热机械问题相对更可控。

这也是为什么：

- 真正的 3D silicon stacking
- hybrid bonding
- die-to-die / wafer-to-wafer silicon integration

在高密度垂直互连上有结构优势。

更准确地说：

`3DIC 并没有消灭 CTE 问题，而是把最严重的 CTE mismatch 尽量从 die-to-die 核心连接界面移开，更多转移到外围封装层次去处理。`

## 8. 那台积电在 SoIC / 3DIC 里是怎么缓解这件事的

这里只能基于公开资料和工程逻辑做推断，因为厂商不会公开所有具体 recipe。下面是比较稳妥的理解。

### 8.1 先做 silicon-to-silicon 的高密度堆叠

SoIC 的核心是把高密度垂直连接尽量放在 silicon-to-silicon 体系里完成。

公开资料显示，TSMC SoIC 支持：

- chip-on-wafer
- wafer-on-wafer
- sub-10 µm 级 bond pitch

这意味着其关键高密度连接界面主要发生在匹配性更好的硅体系内部，而不是一上来就跨到有机基板体系。  
来源：TSMC SoIC 官方页与 2024 年报。  
链接：

- https://3dfabric.tsmc.com/schinese/dedicatedFoundry/technology/SoIC.htm
- https://investor.tsmc.com/sites/ir/annual-report/2024/2024%20Annual%20Report_E.pdf

### 8.2 再把 SoIC 集成芯粒放进 CoWoS / InFO 这类更大平台

TSMC 公开强调 SoIC integrated chips 可再进入 CoWoS 或 InFO。  
这背后的工程含义可以理解为：

- 先在最核心的 die-to-die 层面做高密度硅堆叠
- 再在更外层用 2.5D / fan-out 方案处理系统级扩展

这样做的好处是把问题分层处理，而不是把所有热机械矛盾一次性堆在同一界面上。

### 8.3 用更细 pitch 和更短互连降低 I/O 区域的机械负担

SoIC 的公开卖点之一是更短的 die-to-die 连接带来更好的 PI / SI、更低功耗和更小 form factor。  
从工程上看，更短互连也意味着：

- 连接结构更紧凑
- 不需要像大 bump 那样留下更大的机械冗余体积
- 可把更多系统复杂度移到外围去管理

### 8.4 持续改进热性能

TSMC 2024 年报明确写到：

- SoIC CoW Face-to-Back Gen-2 在 2024 年开始生产
- 且具有显著 thermal performance improvement

公开资料没有展开具体工艺，但这至少说明热管理已经是 SoIC 演进的核心方向之一。  
来源：TSMC 2024 Annual Report  
链接：

- https://investor.tsmc.com/sites/ir/annual-report/2024/2024%20Annual%20Report_E.pdf

### 8.5 在更大封装层次用不同平台缓冲热机械问题

当系统尺寸继续变大，台积电不只用 CoWoS-S，还发展了：

- CoWoS-R
- CoWoS-L

从公开描述看，这些路线就是在密度、尺寸、RDL、LSI、热和机械约束之间重新平衡。  
这里可以合理推断：

`当全局尺寸继续放大时，单纯把所有问题压在大硅 interposer 上会越来越难，因此需要通过 RDL interposer、LSI、多层系统级分工来缓冲应力与成本。`

## 9. 行业里通常怎么解决 CTE mismatch

这不只台积电，整个行业基本都在做下面几类事情。

### 9.1 材料匹配

通过选择更合适的：

- underfill
- polymer dielectric
- mold compound
- adhesive
- substrate stack-up

去降低局部 mismatch。

ASE 的公开研究明确表明，不同 PI 和 underfill 组合会显著影响 stress 与 warpage。  
来源：ASE  
链接：

- https://ase.aseglobal.com/blog/technology-papers/2_5d_vs_focos/
- https://ase.aseglobal.com/blog/technology-papers/thermal-mechanical-characterization-of-25-d-and-focos-chip-first-and-chip-last-packages/

### 9.2 结构缓冲

常见手段包括：

- RDL / PI 作为缓冲层
- underfill 分散局部应力
- bridge / RDL interposer 代替整块大硅
- 对称 stack-up

### 9.3 die thinning 与堆叠顺序优化

die 多薄、谁在上谁在下、采用 W2W 还是 D2W、是 face-to-face 还是 face-to-back，这些都会影响热机械表现。

### 9.4 热设计前置

不是最后才想散热，而是从架构阶段就考虑：

- hot die 放哪
- memory 和 logic 相对位置
- 热路径怎么走
- lid / TIM / heat spreader 怎么配

### 9.5 仿真先行

先进封装必须做多物理场 co-design：

- 热
- 机械
- 电
- 封装结构

否则量产阶段会不断遇到不可预期问题。

## 10. 你可以这样建立心智模型

第一层：

`温度变化 -> 各材料想膨胀/收缩`

第二层：

`但材料被绑定在一起 -> 产生热应力`

第三层：

`热应力积累 -> 翘曲、裂纹、可靠性问题`

第四层：

`3DIC 因为更薄、更细、更热、更难修，所以更敏感`

第五层：

`SoIC/3DIC 的思路不是消灭这个问题，而是把高密度核心连接尽量放到更匹配的硅体系里，再把剩余的 mismatch 放到外围封装层次用材料、结构和热设计去处理`

## 11. 现阶段可以记住的结论

### 结论 1

CTE 不是“附属细节”，而是先进封装能否量产的基本约束。

### 结论 2

3DIC 的难点不只是电互连，而是热、应力、warpage 和可靠性耦合。

### 结论 3

SoIC 这类 silicon-to-silicon 堆叠路线的一个重要优势，是在核心高密度界面上获得更好的材料匹配性。

### 结论 4

真正的解决方案不是单一材料或单一工艺，而是：

- 结构设计
- 材料选择
- 键合工艺
- 热设计
- 测试与可靠性验证

一起协同。

## 参考资料

- TSMC SoIC: https://3dfabric.tsmc.com/schinese/dedicatedFoundry/technology/SoIC.htm
- TSMC 2024 Annual Report: https://investor.tsmc.com/sites/ir/annual-report/2024/2024%20Annual%20Report_E.pdf
- ASE 2.5D vs FOCoS: https://ase.aseglobal.com/blog/technology-papers/2_5d_vs_focos/
- ASE Thermal and Mechanical Characterization: https://ase.aseglobal.com/blog/technology-papers/thermal-mechanical-characterization-of-25-d-and-focos-chip-first-and-chip-last-packages/
- Cu-Based Thermocompression Bonding and Cu/Dielectric Hybrid Bonding for 3D ICs: https://pmc.ncbi.nlm.nih.gov/articles/PMC10489970/

