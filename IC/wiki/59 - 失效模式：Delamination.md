# 失效模式：Delamination

上级：[[48 - 失效模式层：先进封装常见失效总览]]

相关：[[15 - CTE、热应力与 Warpage：从概念到 3DIC]]、[[39 - 供应链地图：材料]]

## 这是什么

Delamination 指的是不同材料层之间发生界面剥离。

在先进封装里，界面很多：

- die / underfill
- mold / RDL
- adhesive / carrier
- dielectric / metal 邻近层

所以 delamination 是非常常见的一类风险。

## 为什么会发生

主要原因通常包括：

- CTE mismatch
- 界面附着不足
- 热循环应力
- 工艺过程中的空洞、污染或界面缺陷

## 为什么它危险

因为界面一旦剥离，会带来一连串连锁问题：

- 局部应力重新分布
- 热路径恶化
- 电连接可靠性下降
- moisture / 长期可靠性风险上升

## 哪些结构更容易担心它

- Fan-out / molding 相关结构
- 多材料异构 stack
- 大尺寸 package
- 3DIC / hybrid bonding 相关界面复杂结构

## 你应该怎么用这个概念

以后看到：

- 多种材料强耦合
- 高温固化
- 大尺寸系统

就要问：

`这个结构里最脆弱的界面在哪里？`

这往往比问“材料强度多大”更有用。

