# 终测与可靠性

上级:[芯片制造与封测 Wiki 总览](../01-overview/README.md)
相关:[晶圆测试与 CP](../03-wafer-test-and-cp/README.md), [后道封装](../04-back-end-packaging/README.md), [跨工艺共性问题](../06-cross-cutting-engineering/README.md)

## 这页在回答什么问题

封装完成后为什么还需要 final test、burn-in、stress test、reliability qualification 和 failure analysis。本章回答芯片如何从“封装完成”变成“可以交付、可长期工作的产品”。

## 终测不是全部测试点

前面的 `03-wafer-test-and-cp` 已经解释了 wafer sort、CP、binning 和 KGD。先进封装里，测试不能只放在最后，因为 logic die、HBM stack、interposer、substrate 和组装步骤都很贵。越晚发现坏件，损失越大。

本章关注封装完成后和产品认证阶段的测试与可靠性：

```text
wafer sort / CP
  -> KGD
  -> assembly and intermediate checks
  -> final test
  -> burn-in / stress / qualification
  -> failure analysis and feedback
```

Final test 是出货前的重要关口，但它不是整条风险控制链的全部。

## 本章结构

| 文档 | 回答的问题 |
| --- | --- |
| Final Test 的方法与流程 | 成品 package 如何做功能、电性、性能和分档测试 |
| Burn-in 与应力测试 | 为什么要用温度、电压、功耗和循环应力提前暴露潜在缺陷 |
| JEDEC 标准与可靠性认证 | 标准如何把可靠性验证变成可交付门槛 |
| 失效分析的工程流程 | 出现问题后如何定位根因并反馈到设计、工艺和测试 |

## 先进封装让可靠性更难

先进封装中的失效对象更多：logic die、HBM stack、RDL、TSV、micro-bump、hybrid bonding interface、underfill、mold、substrate 都可能成为失效源。失效还可能跨层耦合：warpage 会影响 bonding，delamination 会改变热路径，PI 噪声会表现为功能不稳定，热循环会触发 bump fatigue。

```text
more objects
  -> more interfaces
  -> harder fault isolation
  -> stronger need for staged test and reliability feedback
```

## 可靠性的工程目标

可靠性不是“测试更严”这么简单。它要回答三件事：

| 问题 | 工程含义 |
| --- | --- |
| 能否筛掉早期失效 | burn-in、stress test、screening |
| 能否承受目标使用条件 | 温度、湿度、电压、热循环、机械应力 |
| 出问题能否定位根因 | failure analysis、失效复现、设计/工艺反馈 |

## 一句话理解

终测与可靠性把封装后的芯片从“能点亮”推进到“可筛选、可认证、可交付、可长期工作”的产品状态。

## 架构师启示

架构师不能把可靠性留给最后的测试团队。若架构使用多 HBM stack、3DIC、fine-pitch RDL 或 hybrid bonding，就必须在早期考虑 DFT、测试访问、热循环、失效隔离和中间测试节点，否则 final test 很难补救结构性风险。
