# 3D 路线

上级:[封装结构与工艺](../README.md)
相关:[2.5D 路线](../2.5d-routes/README.md), [KGD 的筛选判据与残余风险](../../03-wafer-test-and-cp/kgd-known-good-die.md), [封装工程约束](../../06-cross-cutting-engineering/README.md)

## 这页在回答什么问题

3D 封装路线为什么不只是“把 die 堆起来”，以及它和 2.5D 的根本差异在哪里。本页建立 3DIC 的阅读框架：结构拓扑、连接工艺、制造组织、热应力和测试。

## 3D 路线的核心

3DIC 的核心是把多个 die 沿 Z 向垂直堆叠，并用高密度垂直互连把它们组织成一个更紧密的系统。它追求的是更短互连、更高带宽密度、更低 power-per-bit、更小 footprint，以及更灵活的异构集成。

```text
top die
  ||
vertical die-to-die interconnect
  ||
bottom die / base die
```

2.5D 的主问题是横向并排集成，3D 的主问题是垂直堆叠集成。HBM stack 是 3D memory；logic 与 HBM 并排放到 interposer 上，则是 2.5D 系统里的 3D memory 组件。

## 三个维度必须分开

| 维度 | 它回答的问题 | 例子 |
| --- | --- | --- |
| 结构拓扑 | die 的朝向和堆叠关系 | face-to-face、face-to-back、logic-on-logic |
| 连接工艺 | die 之间如何形成电连接 | micro-bump、hybrid bonding、TSV |
| 制造组织 | 是 wafer 对 wafer，还是 die 对 wafer | W2W/WoW、D2W/CoW |

很多 3DIC 误解来自把这三类词混用。Face-to-face 不是 W2W，hybrid bonding 也不等于某一种制造组织。它们可以交叉组合。

<span class="micro-legacy-anchor" id="本目录阅读顺序"></span><span class="micro-legacy-anchor" id="本章正文"></span>

## 阅读顺序

1. [垂直堆叠的用途](3dic-fundamentals.md)
2. [贯穿硅通孔 TSV](tsv-through-silicon-via.md)
3. [微凸点与混合键合](micro-bump-vs-hybrid-bonding.md)
4. [W2W 与 D2W](w2w-vs-d2w.md)
5. [SoIC 结构与组装](soic-face-to-face-to-back.md)
6. [3DIC 热与应力](3dic-thermal-and-stress-challenges.md)

## 3DIC 的硬问题

3DIC 的收益来自距离缩短，但困难也来自距离缩短。连接 pitch 变小，die 变薄，堆叠更紧，热更难出去，内部节点更难测试，返工空间更小。于是 3DIC 的真正门槛不是概念，而是制造窗口和良率控制。

```text
higher density
  -> tighter bonding window
  -> stronger thermal/stress sensitivity
  -> harder test and repair
```

## 一句话理解

3D 路线把 die 从平面并排推进到垂直堆叠，用更短互连换取带宽和能效，同时把连接、热、应力、测试和良率难度显著放大。

## 架构师启示

架构师选择 3DIC 时，不能只计算 D2D 带宽收益。还要同步评估 die thinning、bonding pitch、热路径、KGD、失效隔离和中间测试节点。否则 3DIC 会从架构收益变成制造和可靠性风险。
