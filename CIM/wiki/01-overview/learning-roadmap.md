# 学习路径与章节依赖关系

上级：[01 Overview](./README.md)
相关：[CIM/PIM/NMC 的严格区分](./cim-pim-nmc-taxonomy.md), [两条正交主线](./two-axes-memory-and-paradigm.md)

## 这页在回答什么问题

如果目标不是背名词，而是形成对 CIM/PIM/NMC 论文、产品和架构路线的判断力，应该按什么顺序读？这页给出依赖关系，避免一开始掉进 cell 细节或公司宣传里。

## 最短判断力路径

先读 01 的两篇锚点，再进入 02/03 的最小闭环：

1. [Memory Wall 与 Von Neumann Bottleneck](./problem-statement.md)
2. [CIM/PIM/NMC 的严格区分](./cim-pim-nmc-taxonomy.md)
3. [两条正交主线](./two-axes-memory-and-paradigm.md)
4. [SRAM-CIM 基础](../02-memory-technologies/sram-cim-foundation.md)
5. [ReRAM 作为计算元件](../02-memory-technologies/reram-as-compute-element.md)
6. [DRAM-PIM 基础](../02-memory-technologies/dram-pim-foundation.md)
7. [Analog CIM 基础](../03-compute-paradigms/analog-cim-fundamentals.md)
8. [Digital CIM 基础](../03-compute-paradigms/digital-cim-fundamentals.md)
9. [Paradigm × Memory Crossmap](../03-compute-paradigms/paradigm-memory-crossmap.md)

这条路径的目标是先建立分类直觉：看到一个对象时，能判断它是 CIM、PIM 还是 NMC，属于哪条 memory technology，采用哪种 compute paradigm。

## 架构建模路径

如果目标是服务 archax 或类似架构探索工具链，先从系统收益衰减和可建模变量读起：

1. [问题定义](./problem-statement.md)
2. [Macro 原语](../04-circuit-and-macro/cim-macro-primitives.md)
3. [Peripheral 开销](../04-circuit-and-macro/peripheral-overhead.md)
4. [从 Macro 到 System](../05-architecture-and-system/from-macro-to-system.md)
5. [Dataflow Mapping](../05-architecture-and-system/dataflow-mapping-on-cim.md)
6. [Memory Hierarchy with CIM](../05-architecture-and-system/memory-hierarchy-with-cim.md)
7. [性能与能效建模](../05-architecture-and-system/performance-energy-modeling.md)
8. [Workload Characterization](../07-workloads/workload-characterization-for-cim.md)

这条路径不要求把 CIM 立即建成完整模型。更现实的目标是分清哪些细节是 Resource、Topology、Interaction、Capability 层面的状态变量，哪些可以在早期架构探索中折叠成能耗、延迟、精度损失或利用率参数。

## 论文阅读路径

如果目标是读 CIM 论文，推荐先建立指标和非理想性口径：

1. [CIM/PIM/NMC taxonomy](./cim-pim-nmc-taxonomy.md)
2. [Analog vs Digital Tradeoff Map](../03-compute-paradigms/analog-vs-digital-tradeoff-map.md)
3. [ADC/DAC/SA in CIM](../04-circuit-and-macro/adc-dac-sa-in-cim.md)
4. [Non-Idealities and Error Sources](../04-circuit-and-macro/non-idealities-and-error-sources.md)
5. [Metrics Glossary](../09-research-frontier/metrics-glossary.md)
6. [Paper Review Template](../09-research-frontier/paper-review-template.md)
7. [Open Problems](../09-research-frontier/open-problems.md)

这条路径的核心是防止被 macro-level TOPS/W、ideal MVM 和局部 accuracy 指标误导。读每篇论文时必须记录层级、精度、workload、是否包含 ADC/DAC/buffer/control、是否有 silicon measurement。

## 产业判断路径

如果目标是看公司和产品，先读 taxonomy，再读产品化路径：

1. [CIM/PIM/NMC taxonomy](./cim-pim-nmc-taxonomy.md)
2. [三大 memory 路线对比](../02-memory-technologies/memory-tech-comparison-matrix.md)
3. [Manufacturing and Test Challenges](../08-industry-and-products/manufacturing-and-test-challenges.md)
4. [Value Chain and Commercialization](../08-industry-and-products/value-chain-and-commercialization.md)
5. [Company Comparison Matrix](../08-industry-and-products/company-comparison-matrix.md)
6. [Samsung HBM-PIM](../08-industry-and-products/company-cards/pim-companies-samsung-hbm-pim.md)
7. [SK hynix AiM/AiMX](../08-industry-and-products/company-cards/pim-companies-sk-hynix-aim.md)
8. [UPMEM](../08-industry-and-products/company-cards/nmc-companies-upmem.md)

这条路径的目标是把“技术路线”与“商业路线”拆开。一个对象可能技术上不如论文激进，但因为供应链、客户入口和软件接口更稳，反而更接近产品化。

## 章节依赖关系

```text
01 taxonomy + two axes
  -> 02 memory technologies
  -> 03 compute paradigms
  -> 04 circuit and macro
  -> 05 architecture and system
  -> 06 software stack
  -> 07 workloads
  -> 08 industry and products
  -> 09 research frontier
  -> 10 reference
```

实际阅读时可以按目标跳转，但写作和维护必须按这个依赖关系。02/03 之前不能谈公司路线，04/05 之前不能相信 macro 指标，06/07 之前不能说“支持某个模型”，08/09 必须区分产业视角和研究视角。

## 一句话理解

先建立 taxonomy 和两轴矩阵，再读器件、电路、系统、软件、workload 和产业；否则越读越多，只会把不同层级的对象混在同一张表里。
