# Final Test 的方法与流程

上级:[终测与可靠性](README.md)
相关:[晶圆测试与 CP](../03-wafer-test-and-cp/README.md), [KGD](../03-wafer-test-and-cp/kgd-known-good-die.md), [AI GPU + HBM 封装对象关系](../04-back-end-packaging/hbm-as-case-study/ai-gpu-hbm-package-architecture.md)

## 这页在回答什么问题

Final Test 测什么，为什么它不是简单“通电验货”，以及它如何与 CP、KGD、中间测试和可靠性验证共同构成风险控制链。

## Final Test 的位置

Final Test 发生在封装完成后，测试对象已经是 package 级产品，而不是裸 die。它要验证封装、电连接、功能、性能、功耗、接口和分档是否满足出货要求。

```text
die-level test
  -> assembly
  -> package-level final test
  -> shipment decision
```

在先进封装中，final test 要面对的是多 die、多 stack、多接口的系统对象，失效来源比单 die 产品更复杂。

## Final Test 测什么

| 类别 | 关注点 |
| --- | --- |
| Continuity / shorts | 开短路、连接完整性 |
| Functional test | 逻辑功能、状态机、基本操作 |
| Interface test | HBM、SerDes、D2D、I/O 等接口 |
| Parametric test | 电压、电流、漏电、时序 margin |
| Performance binning | 频率、功耗、温度条件下的分档 |
| Package-level behavior | 热、供电、封装互连对功能的影响 |

Final Test 的核心不是覆盖所有物理细节，而是在可接受测试时间内筛掉不合格成品，并为分档和出货提供依据。

## 为什么先进封装更难测

先进封装把多个对象组装在一起，坏点可能来自 logic die、HBM stack、RDL、interposer、bump、TSV、bonding interface、substrate 或 underfill 相关应力。Final Test 看到的是系统症状，根因可能藏在内部层级。

```text
observed failure at package pins
  -> logic? HBM? interposer? bump? PDN? thermal?
```

因此 final test 必须与 DFT、diagnostic pattern、中间测试和失效分析配合。

## 与 CP/KGD 的关系

CP 和 KGD 是为了避免坏 die 进入高价值组装链。Final Test 是为了验证组装后的 package 是否仍然满足产品要求。两者不是替代关系。

| 阶段 | 目标 |
| --- | --- |
| CP / wafer sort | 尽早筛掉坏 die |
| KGD | 控制进入封装链的物料质量 |
| Intermediate test | 在高成本组装中途拦截问题 |
| Final Test | 判断最终 package 是否可交付 |

## 测试成本与覆盖率

Final Test 会受到测试时间、ATE 资源、探测/接触方式、温度条件和覆盖率的约束。测试越全，时间和成本越高；测试越少，漏测风险越高。先进封装的工程难点是把高风险失效模式放进测试策略，而不是无限堆测试项。

## 一句话理解

Final Test 是 package 完成后的出货关口，用功能、电性、接口、性能和分档测试确认成品是否可交付，但它无法替代前置 KGD 和中间测试。

## 架构师启示

架构师要为 final test 留出可测试性入口。HBM、D2D、NoC、SerDes、PDN 和热管理都需要可观测性，否则 final test 只能看到“系统失败”，却难以判断失败来自逻辑、封装互连还是供电热问题。
