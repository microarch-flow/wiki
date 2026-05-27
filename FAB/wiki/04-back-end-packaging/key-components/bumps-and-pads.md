# 凸点与焊盘:从 C4 到 micro-bump

上级:[关键工艺组件](README.md)
相关:[Micro-bump vs Hybrid Bonding](../3d-routes/micro-bump-vs-hybrid-bonding.md), [CoWoS-S 完整制造流程](../2.5d-routes/cowos-s-complete-process.md), [失效模式目录](../../06-cross-cutting-engineering/failure-modes-catalog.md)

## 这页在回答什么问题

C4 bump、micro-bump、pad 在封装连接中分别做什么，为什么 pitch、材料、underfill 和热循环会共同决定连接可靠性。

## 基本角色

Pad 是 die、interposer、RDL 或 substrate 上用于连接的金属区域。Bump 是在 pad 之间形成的垂直连接体，用来同时承担电连接和机械连接。

```text
die pad
  |
bump / micro-bump
  |
package pad or interposer pad
```

封装连接不是只让电流通过。它还要承受装配过程、热循环、CTE mismatch 和长期工作载荷。

## 从 C4 到 micro-bump

| 类型 | 典型位置 | 主要特点 |
| --- | --- | --- |
| C4 / flip-chip bump | die 到 substrate 或 interposer | pitch 较大，承接封装级连接 |
| Micro-bump | die 到 interposer、die 到 die、HBM stack 内部 | pitch 更细，适合高密度互连 |
| Hybrid bonding pad | 3DIC 高密度连接界面 | 更短、更密，制造窗口更窄 |

Pitch 变小会提高连接密度，也会压缩对位、平整度、应力和测试窗口。

## Bump 连接的工程问题

| 问题 | 影响 |
| --- | --- |
| 对位误差 | 连接开路、短路或接触不稳定 |
| Coplanarity | 局部 bump 无法可靠接触 |
| 热循环 | bump fatigue 和界面失效 |
| 电流密度 | IR drop、电迁移和发热 |
| Underfill | 应力分散和长期可靠性 |

Bump 越细，单个连接的容错空间越小。高密度封装往往不是“连接点更多就更稳”，而是每个连接点都要求更精确。

## Bump fatigue

Bump fatigue 指焊点或微凸点在反复热循环、机械应力或工作载荷下逐渐疲劳，最终导致连接失效。它常出现在 solder bump、micro-bump、Cu pillar 等连接中。

根因来自电连接、机械连接和 CTE mismatch 的叠加。高价值 2.5D/3D 封装中，一个局部连接失效可能导致整个 module 报废，因此 bump 可靠性必须前置考虑。

## 与 hybrid bonding 的边界

Hybrid bonding 不是“更小的 bump”。它用 Cu/介质直接键合减少凸点体积，追求更高密度和更低寄生。相应地，它把风险从 bump fatigue 部分转移到界面洁净度、平坦度、对位和直接键合可靠性。

## 一句话理解

Bump 和 pad 是封装垂直连接的基本接口；pitch 越细，连接密度越高，但对位、应力、热循环和测试窗口也越窄。

## 架构师启示

架构师定义 D2D 接口宽度时，本质上也在定义 bump/pad 数量、pitch、连接面积和可靠性风险。若接口带宽要求推高 micro-bump 密度，必须同步检查 underfill、热循环、测试覆盖和失效隔离策略。
