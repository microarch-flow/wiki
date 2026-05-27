# 材料供应链

上级:[产业地图](README.md)
相关:[应力、Warpage、CTE 失配](../06-cross-cutting-engineering/stress-warpage-cte.md), [Molding 与 Underfill](../04-back-end-packaging/key-components/molding-and-underfill.md), [基板与载板供应](substrate-and-carrier-supply.md)

## 这页在回答什么问题

先进封装材料为什么不是配角，哪些材料决定 RDL、bonding、warpage、热路径、PI/SI 和长期可靠性。

## 材料的三种角色

| 角色 | 影响 |
| --- | --- |
| 电气角色 | 介电损耗、绝缘、导电、PI/SI |
| 力学角色 | CTE、模量、应力缓冲、warpage |
| 工艺角色 | 图形化、键合、填充、固化、量产一致性 |

同一种材料可能同时影响三类指标。例如 RDL dielectric 既影响高频损耗，也影响多层 build-up 应力和图形化窗口。

## 关键材料组

| 材料组 | 典型对象 | 关联工艺 |
| --- | --- | --- |
| Substrate dielectric | ABF、build-up film | FCBGA、large substrate |
| RDL dielectric / Cu | polymer dielectric、Cu、barrier/seed | Fan-out、RDL interposer |
| Bump / bonding | solder、Cu pillar、UBM、hybrid bonding surface | flip-chip、micro-bump、3DIC |
| Underfill / mold | CUF、mold compound、adhesive | stress buffering、Fan-out、reliability |
| Thermal materials | TIM、lid interface、heat spreader material | thermal path |
| Passive / decap | MIM/eDTC 相关材料 | PDN、PI |

## ABF 为什么重要

ABF 是高性能 build-up substrate 的关键绝缘材料之一。公开资料显示，ABF 被广泛用于高性能 CPU 等复杂基板中，用来把纳米级芯片端子连接到毫米级系统端子，并支持激光加工和铜电镀形成微米级线路。

这说明基板材料不是低端外设，而是高端 package 从 die 走向 board 的核心平台能力。

## 材料瓶颈如何表现

| 瓶颈 | 结果 |
| --- | --- |
| CTE 不匹配 | warpage、bump fatigue、delamination |
| 介电损耗高 | 高速链路损耗、SI margin 降低 |
| 固化收缩 | die shift、RDL overlay 风险 |
| 界面附着不足 | delamination、可靠性下降 |
| 一致性不足 | 良率波动、量产窗口变窄 |

## 一句话理解

先进封装材料决定的不只是封装能不能包起来，而是 RDL 能不能细、bonding 能不能稳、package 会不会翘、接口能不能高速工作。

## 架构师启示

架构师不需要指定材料配方，但要知道材料会反向约束 package 尺寸、RDL 层数、bump pitch、热循环寿命和高速接口。越高端的封装，越要把材料窗口看成架构约束。
