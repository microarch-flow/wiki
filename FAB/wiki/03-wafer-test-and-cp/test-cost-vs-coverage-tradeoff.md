# 测试覆盖率与成本的权衡

上级:[中测:CP 阶段](./README.md)
相关:[CP 测试的方法和典型流程](./cp-test-methodology.md), [KGD:HBM/3DIC 时代的必要前提](./kgd-known-good-die.md), [Final Test 的方法与流程](../05-final-test-and-reliability/final-test-methodology.md)

## 这页在回答什么问题

为什么测试不能简单追求“越多越好”，也不能为了省成本随意降低覆盖率。测试策略是在 tester time、DFT 面积、覆盖率、漏检风险、封装价值和产品质量之间做 trade-off。

## 成本与覆盖率曲线

测试覆盖率提升会进入边际收益递减区。前面一部分测试能快速抓住开短路、明显逻辑 defect、存储缺陷和严重漏电；继续提高覆盖率，需要更多 pattern、更复杂 DFT、更长 tester time、更严格电压/温度条件和更多 debug 工作。

```text
coverage
  ^
  |                         expensive marginal coverage
  |                    ____/
  |               ____/
  |          ____/
  |     ____/
  +---------------------------------> test cost / time
       cheap high-value screening
```

工程目标不是把所有测试都塞到 CP，也不是把所有问题留给 final test，而是在最便宜的位置发现最昂贵的风险。

## 影响测试策略的变量

| 变量 | 倾向提高 CP 覆盖率的条件 | 倾向控制 CP 成本的条件 |
| --- | --- | --- |
| Die 价值 | 大 die、先进节点、低良率早期 | 小 die、成熟节点 |
| 后续封装价值 | HBM、2.5D、3DIC、多 chiplet | 简单单 die package |
| 失效可隔离性 | stack 后难定位 | package 后仍易定位 |
| 产品可靠性要求 | 服务器、车规、长寿命 | 低成本短寿命消费品 |
| Tester time | 漏检成本高于测试成本 | 测试产能成为瓶颈 |
| DFT 面积 | DFT 能显著降低封装报废 | DFT 面积/功耗不可接受 |

## CP、final test 和 burn-in 的分工

CP 适合做封装前筛选，目标是保护后续高价值 assembly。Final test 适合确认封装后规格，覆盖完整 I/O、package PDN、热条件和产品 binning。Burn-in 或 stress test 适合暴露早期失效和可靠性薄弱点，但成本高、时间长，不能用于所有 defect 的常规筛选。

```text
CP:
  lower cost per rejected bad die
  limited package realism

Final test:
  product-realistic
  later and more expensive failure point

Burn-in / stress:
  reliability-oriented
  high time and equipment cost
```

## 漏检与过杀

测试策略同时面对两类错误：漏检和过杀。漏检是坏 die 被当成 good die 送入后续流程；过杀是好 die 被测试误判为坏 die。漏检会提高后续报废和质量风险，过杀会降低有效良率。

先进封装更怕漏检，因为坏 die 漏到后面会拖累整套 package。但若 CP 条件过于保守，过杀也会浪费本来可用的高价值 die。因此测试 limit、binning、guardband 和 retest 策略需要和产品价值匹配。

## 架构阶段能做什么

测试覆盖率不是测试团队最后独立决定的。架构阶段可以决定是否提供 scan、BIST、loopback、isolation、repair、performance monitor、test access point 和分区 power control。可测试性越早设计，CP 的覆盖率和失效隔离能力越强；越晚补救，测试只能在外部症状上猜内部 defect。

## 常见误解

常见误解是“测试成本只是制造成本的一小部分”。对于高价值复杂封装，测试成本的意义不只是 tester time，而是保护昂贵 package 资源和加速良率学习。

另一个误解是“覆盖率高就一定好”。若覆盖率提升只抓住极少数低风险 defect，却显著增加 tester time 和过杀率，产品经济性可能变差。覆盖率必须和 defect 概率、后续损失和产品质量目标一起评估。

## 一句话理解

测试覆盖率是用时间、DFT 面积和测试成本换取更低漏检、过杀和封装报废风险的系统 trade-off。

## 架构师启示

如果我在定义一颗多 die AI package，应该把 DFT 和 test access 当成架构资源，而不是后端附属逻辑。一个小的 loopback/BIST 开销，可能换来封装前发现 D2D 或 HBM interface defect 的能力。

一个具体决策例子：若某低成本控制 die 后续只进入简单封装，CP 可以偏短；若某 compute die 要和 8 个 HBM stack 进入 2.5D package，即使 CP 每颗多花测试时间，也可能比 package 后报废整套系统便宜。
