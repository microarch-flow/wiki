# CP 测试的方法和典型流程

上级:[中测:CP 阶段](./README.md)
相关:[为什么必须在 wafer 阶段测试](./why-wafer-sort-exists.md), [测试覆盖率与成本的权衡](./test-cost-vs-coverage-tradeoff.md), [Final Test 的方法与流程](../05-final-test-and-reliability/final-test-methodology.md)

## 这页在回答什么问题

CP 不是简单“探针点一下”，它由接触、上电、结构测试、功能测试、存储测试、参数测试、binning 和 wafer map 生成组成。理解流程，是为了知道哪些 defect 能在封装前拦住，哪些必须留给后续测试。

## 典型流程

```text
wafer load
  -> alignment / probe card contact
  -> continuity / short-open test
  -> power-up / leakage / IDD checks
  -> scan / logic structural test
  -> memory BIST / repair / redundancy record
  -> limited functional patterns
  -> speed / voltage / leakage binning
  -> wafer map and die disposition
```

这个流程会按产品类型调整。高价值 AI/HPC die 会投入更多 test time 来减少坏 die 漏到封装后；成本敏感小 die 会更严格控制 CP 时间，因为每秒 tester time 都会进入成本。

## CP 测什么

| 测试类型 | 目的 | 能拦截的问题 | 主要限制 |
| --- | --- | --- | --- |
| Continuity / short-open | 确认 pad、基本连接和供电路径 | 开短路、接触异常 | 覆盖功能 defect 很弱 |
| Leakage / current | 检查异常电流和工艺偏差 | 漏电过大、短路、异常 die | 不能定位复杂逻辑问题 |
| Scan / ATPG | 结构化覆盖逻辑路径 | stuck-at、transition、部分桥接 defect | 依赖 DFT 插入和 pattern 质量 |
| Memory BIST | 测 SRAM/ROM 等存储宏 | bitcell defect、array fault | 需要 repair/冗余策略配合 |
| Limited functional | 覆盖关键工作模式 | 系统级逻辑错误 | wafer 环境下模式和速度受限 |
| Speed/leakage bin | 做初步分档 | 慢 die、高漏电 die | 封装后热和电源条件不同 |

CP 的覆盖率来自 DFT，而不是 tester 魔法。没有 scan chain、BIST、test mode、isolation 和可观测点，tester 无法直接看到内部复杂状态。

## Probe 接触本身也是约束

CP 需要 probe card 接触 wafer 上的 pad 或 bump。接触会受 pad pitch、平整度、污染、针痕、接触电阻和电流能力影响。先进节点和先进封装接口变密后，wafer-level probing 本身也变难。

这会影响 die pad planning 和 DFT。若关键接口只在封装后连接，CP 阶段就无法完整测试；若希望封装前覆盖 D2D 或 HBM PHY 的关键路径，需要设计专门的 test access、loopback 或 built-in self-test。

## CP 与 final test 的分工

CP 负责封装前筛选，不负责确认所有产品规格。Final test 发生在 package 后，可以测试完整 I/O、package PDN、热环境、封装应力后行为和系统级接口。两者之间的边界不是谁更重要，而是谁能在更低成本位置发现哪类问题。

```text
CP: cheap enough to screen many die before package
Final test: complete enough to verify product after package
```

## 常见误解

常见误解是“CP 覆盖率越高越好”。实际覆盖率提升会增加 tester time、DFT 面积、pattern 开发和调试成本。高价值复杂封装值得提高 CP 覆盖率，低成本产品可能选择更短 CP 加强 final test。

另一个误解是“CP pass 就是 good die”。更准确地说，CP pass 是在 CP 条件和 coverage 下未发现问题。进入高价值封装的 die 需要达到 KGD 标准，而 KGD 的含义取决于后续封装风险和测试覆盖。

## 一句话理解

CP 是一套封装前风险筛选流程，覆盖率由 DFT、probe access、测试时间和产品价值共同决定。

## 架构师启示

如果我定义 chiplet 接口，应该在架构阶段就问这个接口如何在 wafer 阶段测试。没有 loopback、BIST 或 scan access，D2D PHY 的关键 defect 可能只能在封装后暴露，导致昂贵 package 报废。

一个具体例子：HBM PHY 或 die-to-die link 若只能和真实 HBM/interposer 组装后验证，CP 阶段就无法把相关 defect 拦住。架构师需要和 DFT/physical/package 团队共同定义 wafer-level test mode，而不是把测试留到后端。
