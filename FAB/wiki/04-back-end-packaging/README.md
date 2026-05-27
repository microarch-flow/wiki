# 后道封装

上级:[芯片制造与封测 Wiki 总览](../01-overview/README.md)
相关:[前道与后道:产业分工和技术差异](../01-overview/front-end-vs-back-end.md), [KGD:HBM/3DIC 时代的必要前提](../03-wafer-test-and-cp/kgd-known-good-die.md), [跨工艺共性问题](../06-cross-cutting-engineering/README.md)

## 这页在回答什么问题

后道封装为什么从“把 die 保护起来并接到板上”演化成架构决策的一部分。本章回答 package 如何影响 die 间带宽、供电、散热、机械可靠性、测试和产品形态。

## 封装在系统中的角色

封装的最低职责是让裸 die 变成可使用的产品：保护硅片、提供机械支撑、把电源和信号引出到板级系统、提供基本热路径，并让终测和系统集成可执行。传统封装中，这些职责已经足够重要，但它们很少改变架构本身。

先进封装改变了这件事。package 不再只是 die 外面的连接层，而是多个 die、HBM stack、interposer、RDL、bridge、substrate、bump、underfill 和散热结构共同组成的系统集成层。它决定 compute die 和 memory stack 能靠多近、die-to-die 能有多少带宽、每 bit I/O 能耗多低、供电和热路径能否闭合。

## 本章结构

```text
04-back-end-packaging
  -> packaging evolution and taxonomy
  -> 2.5D routes
       silicon interposer
       fan-out RDL
       embedded bridge
  -> 3D routes
       TSV
       micro-bump / hybrid bonding
       W2W / D2W
       SoIC-style topology vocabulary
  -> key components
       RDL / bumps / substrate / molding / underfill
  -> HBM case study
       HBM stack + logic package architecture
```

这个顺序是刻意安排的。先建立封装分类，再讲 2.5D 横向集成和 3D 垂直集成，然后拆开 RDL、bump、substrate、underfill 这些组件，最后用 HBM 把所有对象合成一个完整系统。

## 封装的架构变量

| 变量 | 封装对象 | 架构影响 |
| --- | --- | --- |
| Die 数量与位置 | compute die、I/O die、HBM stack | chiplet 切分、memory adjacency、traffic locality |
| 互连密度 | interposer、RDL、bridge、bump、hybrid bonding | D2D 带宽、power-per-bit、接口宽度 |
| Package 尺寸 | substrate、interposer、RDL panel/wafer | HBM 数量、reticle/stitching、warpage 风险 |
| 供电路径 | substrate、top metal、interposer/RDL、decap | IR drop、瞬态响应、峰值频率 |
| 热路径 | die placement、TIM、lid、stack、substrate | 功耗密度、HBM 温度、throttling |
| 测试节点 | CP、KGD、中间模块、final test | 组合良率、失效定位、报废成本 |

## 与前面章节的连接

`02-front-end-fabrication` 解释 die 是如何被制造出来的，`03-wafer-test-and-cp` 解释哪些 die 值得进入高价值封装。本章接着回答：这些 KGD 如何被组合成 package，以及为什么组合以后会产生新的互连、热、供电、应力和测试问题。

后续 `06-cross-cutting-engineering` 会把这些问题重新横向展开。比如热路径在 2.5D 和 3D 中表现不同，warpage 会同时受 substrate、interposer、RDL、underfill 和 package 尺寸影响，PDN 也会跨 die、interposer/RDL、substrate 和 board 分层。

## 一句话理解

后道封装把 KGD 变成产品；先进封装进一步把 package 变成带宽、供电、散热、测试和良率共同约束的系统架构层。

## 架构师启示

如果我在定义一个 AI 加速器，封装路线不能等 floorplan 之后再定。HBM stack 数量、compute die 是否拆分、D2D 接口宽度、package 功耗和目标热设计会共同决定需要传统 substrate、2.5D interposer/RDL/bridge，还是进一步进入 3D 堆叠。

一个具体决策例子：若模型要求多个 compute chiplet 间 TB/s 级互连，架构师必须同时问封装能否提供对应 pitch、routing density、KGD 策略和热路径。否则 D2D 带宽只是逻辑指标，不是可制造产品能力。
