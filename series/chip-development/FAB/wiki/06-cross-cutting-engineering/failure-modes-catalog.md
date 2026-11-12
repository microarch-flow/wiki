# 失效模式总览

上级:[跨工艺共性问题](README.md)
相关:[失效分析的工程流程](../05-final-test-and-reliability/failure-analysis-flow.md), [应力、Warpage、CTE 失配](stress-warpage-cte.md), [RDL](../04-back-end-packaging/key-components/rdl-redistribution-layer.md)

## 这页在回答什么问题

先进封装常见失效模式有哪些，它们分别和哪些结构、路线和测试节点相关。本页把失效模式整理成工程索引。

## 机理、症状与测试判定

| 类别 | 机理或物理变化 | 可见症状与验证 |
| --- | --- | --- |
| 互连 | bump 疲劳、键合缺陷 | 接触电阻变化或开路；用连续性测试与截面分析 |
| RDL/金属 | 金属裂纹、via 开裂 | 某路径电阻增加；定位后显微及截面验证 |
| 界面/热机械 | 脱层、翘曲或循环疲劳 | 热阻、接触或形貌变化；超声、热测和截面核验 |
| 电性症状 | PDN droop、眼图恶化 | 电压跌落或误码；需结合负载与测量参考面定位根因 |
| 测试判定 | 漏测或测试接触不良 | 漏检坏件或误判好件；复测接触、pattern 和测试条件 |

例如 delamination 使散热界面热阻增大，导致相同功率下局部温度升高，进而可能出现电性异常。超声检查和热阻复测可协助验证；一个器件的多种症状不能当作多个独立故障计数。目录只提供候选机制；故障率需批次分母、暴露时间及 FA。

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
| KGD screening | 按规定判据筛选 die |
| Stack-level screening | 按规定判据筛选已组装的 HBM stack 或其他堆叠组件 |
| Intermediate test | assembly 或 bonding 后的模块问题 |
| Final Test | package 级功能、接口、分档问题 |
| Stress / reliability | 热循环、疲劳、界面和寿命问题 |
| Failure Analysis | 根因定位和闭环 |

## 一句话理解

失效模式不是可靠性章节的附录，而是理解每条封装路线真实工程边界的索引。

## 架构师启示

架构师选择路线时，要同步问“这条路线最可能怎么坏”。如果选择 Fan-out/RDL，就要提前看 RDL cracking 和 warpage；如果选择 3DIC/hybrid bonding，就要提前看 bonding defect、热路径和测试盲区。
