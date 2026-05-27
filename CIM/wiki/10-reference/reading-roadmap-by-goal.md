# 按目标的阅读路径

上级：[10 Reference](README.md)
相关：[学习路径](../01-overview/learning-roadmap.md), [术语表](glossary.md), [论文阅读模板](../09-research-frontier/paper-review-template.md)

## 这页在回答什么问题

这页回答：不同目标的读者应该按什么顺序读这份 CIM wiki，才能避免被细节淹没。

**目标：30 分钟建立判断力。**

1. [CIM/PIM/NMC 的严格区分](../01-overview/cim-pim-nmc-taxonomy.md)
2. [两条正交主线](../01-overview/two-axes-memory-and-paradigm.md)
3. [Memory tech comparison](../02-memory-technologies/memory-tech-comparison-matrix.md)
4. [Paradigm crossmap](../03-compute-paradigms/paradigm-memory-crossmap.md)
5. [高频问题](high-frequency-questions.md)

读完应能回答：一个对象是 CIM/PIM/NMC 哪类，属于哪条 memory technology 和 compute paradigm，哪些宣传指标不能横比。

**目标：理解电路和 macro。**

1. [SRAM-CIM 基础](../02-memory-technologies/sram-cim-foundation.md)
2. [ReRAM 作为计算元件](../02-memory-technologies/reram-as-compute-element.md)
3. [Analog CIM](../03-compute-paradigms/analog-cim-fundamentals.md)
4. [ADC/DAC/SA](../04-circuit-and-macro/adc-dac-sa-in-cim.md)
5. [非理想性与误差源](../04-circuit-and-macro/non-idealities-and-error-sources.md)

读完应能回答：论文指标属于哪一层，ADC/非理想性/外围是否被计入，结果能否外推到系统。

**目标：理解架构和系统。**

1. [从 macro 到 system](../05-architecture-and-system/from-macro-to-system.md)
2. [Dataflow 映射](../05-architecture-and-system/dataflow-mapping-on-cim.md)
3. [互连与 reduction](../05-architecture-and-system/interconnect-and-reduction.md)
4. [性能与能效建模](../05-architecture-and-system/performance-energy-modeling.md)
5. [Workload characterization](../07-workloads/workload-characterization-for-cim.md)

读完应能回答：一个 macro 如何变成 tile/chip/system，哪些细节必须建模，哪些可以折叠。

**目标：理解软件栈。**

1. [编译流程总览](../06-software-stack/compilation-flow-overview.md)
2. [权重映射到 array](../06-software-stack/weight-mapping-to-arrays.md)
3. [CIM 专用量化](../06-software-stack/quantization-for-cim.md)
4. [模型适配策略](../06-software-stack/model-adaptation-strategies.md)
5. [Runtime 与调度](../06-software-stack/runtime-and-scheduling.md)

读完应能回答：模型如何切到 array/bank，量化和 fallback 如何影响真实可用性。

**目标：评估 workload 是否适合 CIM/PIM/NMC。**

1. [Workload characterization](../07-workloads/workload-characterization-for-cim.md)
2. [CNN on CIM](../07-workloads/cnn-on-cim.md)
3. [Transformer on CIM](../07-workloads/transformer-on-cim.md)
4. [LLM decode and CIM](../07-workloads/llm-decode-and-cim.md)
5. [路线选型决策树](decision-tree-cim-route-selection.md)

读完应能回答：一个 workload 的瓶颈是 compute、memory、reduction、control 还是 software。

**目标：看公司和产业。**

1. [产业与产品 README](../08-industry-and-products/README.md)
2. [公司比较矩阵](../08-industry-and-products/company-comparison-matrix.md)
3. [公司卡片](../08-industry-and-products/company-cards/README.md)
4. [制造与测试挑战](../08-industry-and-products/manufacturing-and-test-challenges.md)

读完应能回答：公司材料说的是 macro、chip、card、prototype、evaluation 还是量产产品。

**目标：读论文和找研究问题。**

1. [研究视角与产业视角](../09-research-frontier/research-vs-industry-perspective.md)
2. [指标术语表](../09-research-frontier/metrics-glossary.md)
3. [论文阅读模板](../09-research-frontier/paper-review-template.md)
4. [近期研究主题](../09-research-frontier/recent-progress-themes.md)
5. [Open problems](../09-research-frontier/open-problems.md)

读完应能回答：下一篇论文解决的是单点优化还是真 open problem，指标是否可比较。

如果时间很少，只读四篇：[CIM/PIM/NMC 的严格区分](../01-overview/cim-pim-nmc-taxonomy.md)、[两条正交主线](../01-overview/two-axes-memory-and-paradigm.md)、[Workload characterization](../07-workloads/workload-characterization-for-cim.md)、[指标术语表](../09-research-frontier/metrics-glossary.md)。这四篇能避免大多数误判。

## 一句话理解

阅读路径应该由目标驱动：术语、器件、电路、系统、软件、workload、产业和研究不能混成一条线性目录。

## 维护原则

本页只维护“目标 -> 最少阅读集合 -> 读完能回答什么”。不要复制 01 的章节依赖说明，也不要把每章内容重新解释一遍；每条路径保持 5-7 个链接以内。
