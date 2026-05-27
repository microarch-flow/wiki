# JEDEC 标准与可靠性认证

上级:[终测与可靠性](README.md)
相关:[Burn-in 与应力测试](burn-in-and-stress-test.md), [失效分析的工程流程](failure-analysis-flow.md), [术语表](../08-reference/glossary.md)

## 这页在回答什么问题

JEDEC 等可靠性标准在芯片交付中起什么作用，为什么标准不是“背测试项目”，而是把寿命、环境、应力和失效判据变成可沟通的工程语言。

## 标准的作用

可靠性认证需要让设计方、制造方、封测方和客户对测试条件、样本量、判据和报告方式有共同语言。JEDEC 类标准提供的就是这种共同框架。

```text
reliability requirement
  -> standard test condition
  -> pass/fail criteria
  -> qualification evidence
```

没有标准，可靠性讨论会变成“我觉得够严”和“你觉得不够严”的争论。

## 标准覆盖什么

标准体系会覆盖多类应力和验证目标：

| 类别 | 关注点 |
| --- | --- |
| Temperature cycling | 热膨胀不匹配、bump fatigue、delamination |
| High temperature storage | 材料稳定性、界面和长期老化 |
| Bias stress | 电压、电场、漏电和介质可靠性 |
| Moisture sensitivity | 吸湿、回流、界面剥离风险 |
| Mechanical / board-level | 板级焊点、跌落、弯曲或机械载荷 |
| ESD / latch-up | 静电和异常电气应力 |

具体产品会选择适用的标准、等级和测试组合。

## 对先进封装的意义

先进封装把更多材料和界面放进 package。标准测试能帮助暴露 RDL cracking、bump fatigue、delamination、warpage、bonding defect、TSV 相关可靠性和热路径问题。它也能约束交付证据：不是只交付功能样品，而是交付通过可靠性门槛的产品。

## 标准不是万能保证

通过标准认证不表示产品在所有场景下都不会失败。标准测试是约定条件下的验证，并不能覆盖所有真实工作负载、散热条件、板级设计和系统使用方式。高性能产品还需要结合实际 power profile、thermal profile、system workload 和客户应用场景做补充验证。

```text
standard qualification
  + product-specific mission profile
  + failure analysis feedback
  = stronger reliability confidence
```

## 为什么要和 failure analysis 结合

可靠性测试发现失效后，真正重要的是定位根因并闭环。若温度循环后出现开路，根因可能是 bump fatigue、RDL crack、delamination 或 substrate 焊点问题。标准告诉你如何施加应力，FA 告诉你为什么失败。

## 一句话理解

JEDEC 等标准把可靠性测试从经验判断变成可沟通、可复现、可交付的工程证据，但它需要和产品场景和失效分析一起使用。

## 架构师启示

架构师不需要背每个标准条款，但要知道目标应用和使用场景会反向影响封装选择。高温、高功耗、长寿命或高可靠应用会让热路径、材料界面、bump pitch、substrate 和 DFT 设计从一开始就进入约束集合。
