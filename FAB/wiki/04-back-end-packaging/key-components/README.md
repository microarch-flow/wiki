# 关键工艺组件

上级:[后道封装](../README.md)
相关:[2.5D 路线](../2.5d-routes/README.md), [3D 路线](../3d-routes/README.md), [跨工艺共性问题](../../06-cross-cutting-engineering/README.md)

## 这页在回答什么问题

先进封装里反复出现的 RDL、bump、pad、substrate、carrier、molding、underfill 到底各自承担什么角色。本页把路线名拆成底层组件，帮助后续理解失效模式和架构约束。

## 为什么要单独看组件

封装路线的名字会变化，但底层组件反复出现。Si interposer、Fan-out、bridge、3DIC、HBM package 都会碰到互连、支撑、保护、供电、散热和应力问题。理解组件，才能看懂不同路线为什么会卡在相似位置。

```text
package route
  -> RDL / bump / substrate / molding / underfill
  -> PI / SI / thermal / stress / yield
```

## 本目录组件

| 文档 | 回答的问题 |
| --- | --- |
| RDL | 封装级重布线如何形成，为什么它会成为 Fan-out 和 RDL interposer 的底座 |
| Bumps and pads | C4、micro-bump、pad 如何连接 die 与封装层次 |
| Substrate and carrier | 基板和载体如何支撑供电、信号、机械和制造流程 |
| Molding and underfill | 保护层如何影响可靠性、warpage 和界面失效 |

这些组件不是孤立零件。RDL 的应力会影响 bump 可靠性，underfill 会改变 warpage 和界面应力，substrate 会影响供电、信号和整包尺寸上限。

## 从组件看路线

| 路线 | 最关键组件 |
| --- | --- |
| Fan-out/RDL | RDL、molding、carrier、bump |
| Si interposer | TSV、micro-bump、substrate、underfill |
| Embedded bridge | local silicon bridge、RDL/substrate、transition region |
| 3DIC | hybrid bonding/micro-bump、TSV、thin die handling |
| HBM package | micro-bump、TSV、substrate/interposer、thermal materials |

路线差异很大，但制造难度往往落回这些具体对象。

## 一句话理解

先进封装不是平台名的堆叠，而是 RDL、bump、substrate、molding、underfill 等组件共同闭合互连、供电、散热、应力和良率。

## 架构师启示

架构师定义封装时，不应只写“采用 2.5D”或“采用 3DIC”。更可执行的规格要落到组件层：需要多少 RDL 层、什么 bump pitch、基板承载多少电流、underfill 是否能支撑热循环、哪些界面最怕 delamination。
