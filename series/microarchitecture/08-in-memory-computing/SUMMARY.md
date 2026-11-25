# 知识地图

本页是全 wiki 的完整目录树。入口与导读见 [README](./README.md)；按目标的最少阅读集合见 [按目标的阅读路径](./10-reference/reading-roadmap-by-goal.md)。

- [CIM Wiki 首页](./README.md)

## 01 Overview — 坐标系

- [章导读](./01-overview/README.md)
- [Memory Wall 与 Von Neumann Bottleneck](./01-overview/problem-statement.md)
- [同一个点积，挪到存储旁边或阵列里面怎么算？](./01-overview/cim-pim-nmc-taxonomy.md)
- [两条正交主线：Memory Technology × Compute Paradigm](./01-overview/two-axes-memory-and-paradigm.md)
- [早期 PIM 原型未规模采用与 AI 时代的新机会](./01-overview/why-cim-now-and-why-not-before.md)
- [CIM 整体分类体系](./01-overview/taxonomy.md)
- [学习路径与章节依赖关系](./01-overview/learning-roadmap.md)

## 02 Memory Technologies — 横轴

- [章导读](./02-memory-technologies/README.md)
- [SRAM 原本一次读出一个字，怎样让阵列参与计算？](./02-memory-technologies/sram-cim-foundation.md)
- [位线上的电压，怎样变成可累加的数字部分和？](./02-memory-technologies/sram-cim-deep-dive.md)
- [把乘加器放在 DRAM bank 旁，一条命令怎样算起来？](./02-memory-technologies/dram-pim-foundation.md)
- [多组 bank 各算出部分和，谁把它们合成最后的答案？](./02-memory-technologies/dram-pim-deep-dive.md)
- [一格 ReRAM 怎样存下权重，两行电流又怎样算出点积？](./02-memory-technologies/reram-as-compute-element.md)
- [理想列电流应该是 4.6 µA，为什么实际读数会偏？](./02-memory-technologies/reram-cim-deep-dive.md)
- [Flash CIM：Mythic 的路线及其工程现实](./02-memory-technologies/flash-cim-niche.md)
- [PCM 和 MRAM 作为 CIM 介质](./02-memory-technologies/pcm-mram-for-cim.md)
- [三大 Memory 路线全景对比](./02-memory-technologies/memory-tech-comparison-matrix.md)

## 03 Compute Paradigms — 纵轴

- [章导读](./03-compute-paradigms/README.md)
- [Analog CIM：用电流/电压代表乘累加结果](./03-compute-paradigms/analog-cim-fundamentals.md)
- [Analog CIM 深入：非理想性、噪声、Variation、温漂](./03-compute-paradigms/analog-cim-deep-dive.md)
- [Digital CIM：Bitwise Compute 与 SRAM 阵列的结合](./03-compute-paradigms/digital-cim-fundamentals.md)
- [Digital CIM 深入：Bit-Serial、Bit-Parallel、Popcount](./03-compute-paradigms/digital-cim-deep-dive.md)
- [Mixed-Signal CIM：在哪一段切换、为什么切换](./03-compute-paradigms/mixed-signal-cim.md)
- [Analog vs Digital 全景对比](./03-compute-paradigms/analog-vs-digital-tradeoff-map.md)
- [三种 Paradigm × 三种 Memory 交叉图](./03-compute-paradigms/paradigm-memory-crossmap.md)

## 04 Circuit and Macro — 电路与宏

- [章导读](./04-circuit-and-macro/README.md)
- [CIM Macro 的基本原语：Array、Driver、Sense、Accumulator](./04-circuit-and-macro/cim-macro-primitives.md)
- [ADC/DAC/Sense Amp：Analog CIM 的咽喉](./04-circuit-and-macro/adc-dac-sa-in-cim.md)
- [数据编码：Bit-Serial、Binary、Unary、Stochastic](./04-circuit-and-macro/data-encoding-strategies.md)
- [精度与量化在电路层的实现约束](./04-circuit-and-macro/precision-and-quantization-at-circuit.md)
- [非理想性总览：Noise、Mismatch、Variation、Retention](./04-circuit-and-macro/non-idealities-and-error-sources.md)
- [Peripheral 开销：为什么 ADC/控制常吃掉主要功耗与面积](./04-circuit-and-macro/peripheral-overhead.md)
- [Macro 设计的决策框架：从 Workload 到 Macro 参数](./04-circuit-and-macro/macro-design-tradeoff-framework.md)

## 05 Architecture and System — 架构与系统

- [章导读](./05-architecture-and-system/README.md)
- [从 Macro 到 System：Tile、Bank、Chip 三级组织](./05-architecture-and-system/from-macro-to-system.md)
- [Dataflow 在 CIM 上的映射：Weight Stationary 的契合与边界](./05-architecture-and-system/dataflow-mapping-on-cim.md)
- [CIM 阵列间的互连与 Reduction：与 NoC 的关系](./05-architecture-and-system/interconnect-and-reduction.md)
- [CIM 系统的存储层次：On-Array、Buffer、Main Memory](./05-architecture-and-system/memory-hierarchy-with-cim.md)
- [性能与能效建模：从 Macro 到 System 的指标推导](./05-architecture-and-system/performance-energy-modeling.md)
- [建模参数字典：四元组到可实现参数表](./05-architecture-and-system/cim-modeling-parameter-schema.md)
- [可靠性与误差容忍：Analog 路线的核心系统问题](./05-architecture-and-system/reliability-and-error-tolerance.md)
- [CIM 加速器与 Host 的集成：PCIe Attached 到 SoC 内嵌](./05-architecture-and-system/cim-system-integration-with-host.md)

## 06 Software Stack — 软件栈

- [章导读](./06-software-stack/README.md)
- [CIM 编译流程总览：模型到算子再到 Macro 映射](./06-software-stack/compilation-flow-overview.md)
- [权重到 Array 的映射：Tiling、Duplication、Folding](./06-software-stack/weight-mapping-to-arrays.md)
- [CIM 专用的量化策略：低比特、非对称、Calibration](./06-software-stack/quantization-for-cim.md)
- [模型适配：Noise-Aware Training、QAT、Retraining](./06-software-stack/model-adaptation-strategies.md)
- [Runtime 与调度：Write 慢、Read 快的非对称性](./06-software-stack/runtime-and-scheduling.md)
- [不同 CIM/PIM 路线的软件栈差异](./06-software-stack/software-stack-comparison.md)

## 07 Workloads — 工作负载

- [章导读](./07-workloads/README.md)
- [什么样的 Workload 适合 CIM、什么样的不适合](./07-workloads/workload-characterization-for-cim.md)
- [CNN：CIM 的标准应用场景及其上限](./07-workloads/cnn-on-cim.md)
- [Transformer：Attention 与 KV Cache 的新挑战](./07-workloads/transformer-on-cim.md)
- [LLM Decode 阶段：Memory-Bound 工作负载与 CIM 的契合度](./07-workloads/llm-decode-and-cim.md)
- [Edge AI：能效需求驱动下 CIM 的现实定位](./07-workloads/edge-ai-and-cim.md)

## 08 Industry and Products — 产业与产品

- [章导读](./08-industry-and-products/README.md)
- [CIM 产业全景：Startup、IDM、IP 公司、学术孵化](./08-industry-and-products/industry-landscape.md)
- [公司全景对比矩阵](./08-industry-and-products/company-comparison-matrix.md)
- [CIM 商业化路径：从论文到 Tape-Out 到量产](./08-industry-and-products/value-chain-and-commercialization.md)
- [制造与测试挑战](./08-industry-and-products/manufacturing-and-test-challenges.md)
- [公司卡片](./08-industry-and-products/company-cards/README.md)
  - [Axelera：SRAM-CIM 商业化的代表](./08-industry-and-products/company-cards/cim-companies-axelera.md)
  - [Mythic：Flash-Based Analog CIM 的代表与教训](./08-industry-and-products/company-cards/cim-companies-mythic.md)
  - [Samsung HBM-PIM：属于 PIM 不是 CIM](./08-industry-and-products/company-cards/pim-companies-samsung-hbm-pim.md)
  - [SK hynix AiM/AiMX：属于 PIM 不是 CIM](./08-industry-and-products/company-cards/pim-companies-sk-hynix-aim.md)
  - [UPMEM：同 die 可编程 PIM 对照案例](./08-industry-and-products/company-cards/nmc-companies-upmem.md)

## 09 Research Frontier — 研究前沿

- [章导读](./09-research-frontier/README.md)
- [研究视角与产业视角的差异](./09-research-frontier/research-vs-industry-perspective.md)
- [CIM 论文中常见指标的精确定义](./09-research-frontier/metrics-glossary.md)
- [CIM 论文阅读模板](./09-research-frontier/paper-review-template.md)
- [近期研究主题：超低比特、3D 集成 CIM、新型 Cell](./09-research-frontier/recent-progress-themes.md)
- [CIM 研究的 Open Problems](./09-research-frontier/open-problems.md)
- [案例：TSMC 16nm CIM Macro](./09-research-frontier/case-study-tsmc-16nm-cim-macro.md)
- [案例：东大 ReRAM CIM](./09-research-frontier/case-study-u-tokyo-reram-cim.md)
- [案例：Samsung HBM-PIM 的研究视角](./09-research-frontier/case-study-samsung-hbm-pim-research-angle.md)

## 10 Reference — 速查

- [章导读](./10-reference/README.md)
- [按目标的阅读路径](./10-reference/reading-roadmap-by-goal.md)
- [CIM 路线选型决策树](./10-reference/decision-tree-cim-route-selection.md)
- [高频问题：最容易混淆的概念](./10-reference/high-frequency-questions.md)
- [术语表](./10-reference/glossary.md)
- [资料入口说明](./10-reference/source-notes.md)
