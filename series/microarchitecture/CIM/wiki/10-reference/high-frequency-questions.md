# 高频问题：CIM 领域最容易混淆的概念

上级：[10 Reference](README.md)
相关：[术语表](glossary.md), [CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md), [公司卡片](../08-industry-and-products/company-cards/README.md)

## 这页在回答什么问题

这页回答：CIM 领域最容易被论文、新闻稿和公司材料混用的问题，应该如何快速判定。

**PIM 是 CIM 的一种吗？**  
在本专题互斥的术语约定中，CIM 要求 cell 或 array path 参与计算；PIM 指同 memory die/bank 内独立处理单元。Samsung HBM-PIM 和 SK hynix AiM/AiMX 属于后者。其他文献可能用广义 PIM 包含阵列内计算，比较前须核对定义。
应该去读：[CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md)。

**名字里有 in-memory computing，就一定是 CIM 吗？**  
不是。行业材料经常把 in-memory、processing-in-memory、near-memory、AiM 混用。本 wiki 只看机制：compute 位置在哪里，cell/bitline/wordline/sense path 是否参与计算。
应该去读：[术语表](glossary.md)。

**SRAM 旁边放 MAC array 算 SRAM-CIM 吗？**  
不算。只有 SRAM cell、bitline、wordline、sense amplifier 或 array path 被用于 bitwise compute、popcount、charge sharing/current summation 等计算，才进入 SRAM-CIM。普通 SRAM buffer 加旁路 MAC 只是传统 NPU 结构。
应该去读：[SRAM-CIM 基础](../02-memory-technologies/sram-cim-foundation.md)。

**Analog CIM 一定比 digital CIM 能效高吗？**  
不一定。Analog array 的局部 MAC 能效可能很高，但 ADC/DAC/SA、calibration、noise margin、精度恢复和外围搬移会吞掉收益。Digital CIM 的极限能效不如理想 analog 激进，但验证、测试和精度更可控。
应该去读：[Analog vs Digital](../03-compute-paradigms/analog-vs-digital-tradeoff-map.md)。

**Digital CIM 只是保守妥协吗？**  
不是。Digital CIM 用更可控的精度、DFT、CMOS 兼容性和软件映射换取较低的物理激进程度，在 SRAM-CIM 产品化中反而更现实。  
应该去读：[Digital CIM 深入](../03-compute-paradigms/digital-cim-deep-dive.md)。

**ReRAM-CIM 为什么还没有大规模产品化？**  
核心不是“能不能做 crossbar MVM”，而是多值电导的一致性、retention drift、write-verify、endurance、IR drop、sneak path、ADC 和模型精度补偿能否在长期部署中闭环。
应该去读：[东大 ReRAM case](../09-research-frontier/case-study-u-tokyo-reram-cim.md)。

**CIM 能解决 memory wall 吗？**  
只能缓解特定数据搬移。CIM 对 weight-stationary、低精度、阵列复用高的 workload 更有价值；遇到 activation/KV cache/irregular access/control-heavy 部分，仍会受 buffer、NoC、DRAM、host 和 software fallback 约束。
应该去读：[Memory wall 问题](../01-overview/problem-statement.md) 和 [Workload characterization](../07-workloads/workload-characterization-for-cim.md)。

**为什么 CNN 比 Transformer 更自然适配 CIM？**  
CNN 的卷积权重复用和规则数据流更适合 array-resident weights。Transformer/LLM decode 的 attention、KV cache、sequence length、batch size 和动态控制让映射更复杂；这不代表 CIM 无用，而是需要更精细的 workload partition。
应该去读：[CNN on CIM](../07-workloads/cnn-on-cim.md) 与 [LLM decode](../07-workloads/llm-decode-and-cim.md)。

**CIM 对 LLM decode 到底有没有意义？**  
有局部意义，但不是整模型替代。权重驻留的 GEMV/MLP 子图可能受益，KV cache、attention、sampling、host runtime 和 batch/sequence 动态会限制收益。  
应该去读：[LLM decode and CIM](../07-workloads/llm-decode-and-cim.md)。

**HBM-PIM 为什么不能和 ReRAM-CIM 的 TOPS/W 横比？**  
HBM-PIM 的 system speedup 与 ReRAM-CIM 的 macro TOPS/W 单位和层级不同，不能直接横比；若对相同任务、精度、测量窗口和系统边界获得端到端数据，则可比较。
应该去读：[09 指标术语表](../09-research-frontier/metrics-glossary.md)。

**PIM/NMC 和传统 GPU/NPU + HBM 的差别在哪里？**  
差别在计算是否被推到 memory die/bank 或 memory 近侧，以及 host/controller/runtime 如何表达 offload。传统 GPU/NPU + HBM 仍主要由 accelerator 取数计算。  
应该去读：[DRAM-PIM 深入](../02-memory-technologies/dram-pim-deep-dive.md)。

**09 的 case study 能说明产业成熟吗？**  
不能直接说明。09 的 case study 说明研究问题和证据链；08 才讨论产品化、客户、供应链和商业状态。TSMC 16nm CIM macro 是研究案例，不是 TSMC CIM 产品发布。
应该去读：[研究视角与产业视角](../09-research-frontier/research-vs-industry-perspective.md)。

**UPMEM 到底算什么？**  
UPMEM 的 DPU 和 DRAM bank 在同一 die，执行独立 DPU 代码，数据在 MRAM 与私有 WRAM 间显式 DMA；本 wiki 归 PIM，不是 CIM。DIMM/server 是交付形态，host 负责分发与回收。其他文献可能使用更宽的 near-memory 或 PIM 术语。
应该去读：[UPMEM card](../08-industry-and-products/company-cards/nmc-companies-upmem.md)。

**什么时候应该选择传统 NPU/GPU，而不是 CIM/PIM/NMC？**  
当 workload 动态性强、控制复杂、模型频繁变化、软件生态优先、或数据复用不足时，传统 NPU/GPU 往往风险更低。CIM/PIM/NMC 需要明确的数据搬移瓶颈和可映射子图。  
应该去读：[路线选型决策树](decision-tree-cim-route-selection.md)。

## 一句话理解

高频问题的统一答案是：不要看名字，回到计算位置、cell 参与程度、指标层级和 workload。

## 维护原则

FAQ 只回答最容易误判的问题，每个答案都要给短答、原因和下一步链接。新增问题时避免展开成教程；如果需要长解释，应新建或链接到 02-09 的正文页。

## ADC 共享会减少转换总数吗？

不会自动减少。八个独立样本可均衡路由到两个 ADC 时，每轮各转一个，需要四轮、八次转换；均衡路由到四个 ADC 时需要两轮，仍是八次转换。固定映射时轮数是每个 ADC 所承担样本数的最大值。例如四个样本都只能去 ADC 0 时，共有四个 ADC 仍需四轮。零样本无需转换；有样本而无 ADC 时不可服务。ADC latency 与启动间隔可以不同。若模拟路径在转换前实际合并样本，应按合并后的独立样本重新计数，同时计入误差和动态范围。详见[参数字典](../05-architecture-and-system/cim-modeling-parameter-schema.md#adc-样本转换次数与共享)。
