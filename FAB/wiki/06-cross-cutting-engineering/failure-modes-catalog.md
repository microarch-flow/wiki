# 失效模式总览

上级:[跨工艺共性问题](README.md)
相关:[失效分析的工程流程](../05-final-test-and-reliability/failure-analysis-flow.md), [应力、Warpage、CTE 失配](stress-warpage-cte.md), [RDL](../04-back-end-packaging/key-components/rdl-redistribution-layer.md)

## 这页在回答什么问题

先进封装常见失效模式有哪些，它们分别和哪些结构、路线和测试节点相关。本页把失效模式整理成工程索引。

## 六类常见失效

| 类别 | 典型表现 | 相关结构 |
| --- | --- | --- |
| 互连失效 | bump fatigue、micro-bump 开路、bonding defect | bump、hybrid bonding、TSV |
| RDL/金属失效 | RDL cracking、via/trace 开裂 | Fan-out、RDL interposer、CoWoS-R/L |
| 界面失效 | delamination、underfill/mold 界面剥离 | underfill、mold、adhesive、die surface |
| 热机械失效 | warpage、薄 die 形变、热循环疲劳 | large package、3DIC、HBM package |
| 电性能失效 | PI droop、SI error、高速接口误码 | PDN、RDL、interposer、substrate |
| 测试与筛选失效 | 坏件太晚发现、内部缺陷不可见 | KGD、中测、final test、FA |

## 路线与失效模式

| 路线 | 更要关注的失效 |
| --- | --- |
| Si interposer | 大尺寸 warpage、TSV 应力、delamination、module 报废成本 |
| Fan-out/RDL | die shift、RDL cracking、mold shrinkage、warpage |
| Embedded bridge | 桥区与外围平台过渡、局部对位、界面可靠性 |
| 3DIC/hybrid bonding | bonding defect、thin die stress、内部测试盲区、热路径 |
| HBM package | logic-HBM 热耦合、micro-bump、TSV、PDN/SI 耦合 |

## 关键失效的工程直觉

RDL cracking 来自细线、多层 build-up 和热机械应力的叠加。Bump fatigue 来自连接点在热循环和机械载荷下反复受力。Delamination 是界面附着和应力共同失败。Warpage 是结构、材料、热和尺寸耦合后的整体形变。Bonding defect 则常来自平坦度、洁净度、对位和薄 die handling 窗口。

```text
structure + material + thermal load + process window
  -> failure mode
```

## 失效模式和测试节点

| 测试/分析节点 | 更容易捕捉的问题 |
| --- | --- |
| CP / wafer sort | die 内功能和参数问题 |
| KGD screening | 高价值 die 或 stack 的早期筛选 |
| Intermediate test | assembly 或 bonding 后的模块问题 |
| Final Test | package 级功能、接口、分档问题 |
| Stress / reliability | 热循环、疲劳、界面和寿命问题 |
| Failure Analysis | 根因定位和闭环 |

## 一句话理解

失效模式不是可靠性章节的附录，而是理解每条封装路线真实工程边界的索引。

## 架构师启示

架构师选择路线时，要同步问“这条路线最可能怎么坏”。如果选择 Fan-out/RDL，就要提前看 RDL cracking 和 warpage；如果选择 3DIC/hybrid bonding，就要提前看 bonding defect、热路径和测试盲区。
