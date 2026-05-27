# 跨工艺共性问题

上级:[芯片制造与封测 Wiki 总览](../01-overview/README.md)
相关:[后道封装](../04-back-end-packaging/README.md), [终测与可靠性](../05-final-test-and-reliability/README.md), [从架构需求反推工艺与封装选型](from-architecture-to-process-selection.md)

## 这页在回答什么问题

为什么热、应力、PI、SI、良率、测试和失效模式不能被当成单独章节处理。本章把它们作为横向约束，重新穿过前道、CP、封装、终测和架构选择。

## 为什么需要横向章节

前面章节按制造阶段展开：前道制造 die，CP 筛选 die，后道封装组合 die，终测验证成品。但真实产品失败时，根因很少只停留在某一个阶段。

```text
architecture target
  -> process and package choice
  -> thermal / PI / SI / stress / yield
  -> test and reliability feedback
```

例如 HBM 带宽目标会推高 interposer/RDL routing，routing 会影响 SI 和 PI，功耗会影响热路径，热循环会影响 bump fatigue 和 delamination，最终又回到测试覆盖和失效分析。

## 本章结构

| 文档 | 作用 |
| --- | --- |
| thermal-path-and-management | 从 die placement 和 package 结构看热路径 |
| stress-warpage-cte | 从材料和尺寸看热应力、warpage 与可靠性 |
| power-delivery-pi-pdn-decap | 从板级到 die 内看供电完整性 |
| signal-integrity-in-package | 从封装互连看高速信号、回流路径和串扰 |
| yield-economics-across-stages | 从 CP、KGD、中测、封装、终测看有效良率 |
| failure-modes-catalog | 把失效模式和路线绑定起来 |
| from-architecture-to-process-selection | 从架构需求反推工艺和封装路线 |

## 五个横向变量

| 变量 | 它会反向约束什么 |
| --- | --- |
| 热 | die placement、stack 顺序、TIM/lid、功耗上限 |
| 应力/warpage | package 尺寸、材料、RDL 层数、bonding pitch |
| PI/PDN | substrate、interposer/RDL、decap、bump/TSV 电流路径 |
| SI | D2D 链路、HBM 接口、SerDes、return path |
| 良率/测试 | KGD 策略、D2W/W2W、assembly 节点、final test 覆盖 |

这些变量相互耦合。更高带宽会增加功耗和 I/O，功耗会推高热与 PDN 压力，package 变大会加重 warpage，warpage 又会影响 bonding 和测试接触。

## 一句话理解

跨工艺共性问题是把“能不能做出来”推进到“能不能高良率、可测试、可散热、可供电、可长期可靠工作”的工程约束层。

## 架构师启示

架构师要把这些横向变量当成早期设计输入，而不是后期收尾项。若系统目标依赖 HBM、chiplet、2.5D 或 3DIC，那么热、PI、SI、warpage、KGD 和失效隔离必须和架构分解一起进入决策。
