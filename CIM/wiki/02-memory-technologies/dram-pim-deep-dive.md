# DRAM-PIM 深入：HBM-PIM、AiM/AiMX、Bank-Level vs Channel-Level

上级：[02 Memory Technologies](./README.md)
相关：[DRAM-PIM 基础](./dram-pim-foundation.md), [Samsung HBM-PIM](../08-industry-and-products/company-cards/pim-companies-samsung-hbm-pim.md), [SK hynix AiM/AiMX](../08-industry-and-products/company-cards/pim-companies-sk-hynix-aim.md), [RAM: DRAM Commands](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md)

## 这页在回答什么问题

DRAM/HBM/GDDR-PIM 的设计空间在哪里？同样叫 PIM，把 compute 放在 bank 附近、channel 附近、memory die 逻辑区域或系统卡上，得到的是完全不同的带宽、编程模型和产品形态。

## Bank-Level 与 Channel-Level

Bank-level PIM 把 compute 放得更靠近 bank 或 subarray 周边。收益是局部数据不需要穿过完整外部接口，适合高局部性、简单操作和高并行 bank 级执行。代价是每个 bank 可放的逻辑很小，面积、功耗和 DRAM 工艺限制明显，支持复杂算子很难。

Channel-level 或 die-level PIM 把 compute 放在更共享的位置，能用更集中的控制和更灵活的数据路径，但离 cell 更远，局部带宽优势下降。它适合把多个 bank 的数据聚合处理，却更依赖 controller、command 和 runtime 协同。

这个 trade-off 类似 NoC 中“局部 reduction vs 全局 reduction”的问题：越局部，数据少搬但逻辑受限；越集中，逻辑灵活但搬运增加。

## 与 Analog/Digital/Mixed-Signal 的关系

DRAM/HBM/GDDR-PIM 的主线是 memory die/bank 内独立 digital processing。它可以支持整数、浮点或定制低比特格式，但这些数值格式属于 PIM execution unit 的设计，不属于 analog/digital/mixed-signal CIM 纵轴。

Analog DRAM-CIM 研究可以利用 DRAM cell/bitline charge sharing 做逻辑或近似计算，但那是 in-DRAM bitline compute，不是本篇 HBM/GDDR-PIM 主线。Mixed-signal 在 PIM 语境中更多体现为 memory-side digital compute 与 analog DRAM I/O、sense path、PHY 的系统协同，也不是 array-native CIM macro 的 mixed-signal paradigm。

## HBM-PIM 的系统价值

HBM-PIM 的价值来自大容量高带宽 memory 与 AI/HPC workload 的距离缩短。它不是 ReRAM crossbar 式 analog MVM，也不应和 SRAM-CIM macro TOPS/W 直接比较。应该问的是：哪些操作被 offload 到 memory die/bank 内？减少了多少 processor-memory 往返？host stall 是否下降？token latency 或 kernel energy 是否改善？

如果结果仍然频繁回到 GPU/CPU 做 softmax、normalization、sampling 或复杂控制，PIM 的收益会被同步和数据回传削弱。LLM decode 和 long context 是更自然的观察点，因为它们的 memory-bound 特征比 dense prefill GEMM 更明显。

## AiM/AiMX 的边界

SK hynix GDDR6-AiM/AiMX 展示了 memory vendor 从 component 走向 solution 的路径。GDDR6-AiM 属于 PIM 语境；AiMX 作为 accelerator card 或 demo system 时，评价层级已经从 memory device 上升到 card/system。它不应被放进 CIM macro 指标表，而应在 08 章按产品形态和系统集成评估。

这类对象最容易被误读：一方面它比单个 research macro 更接近系统展示；另一方面 demo card 不等于大规模客户部署。评价时要区分 memory die capability、controller hub、board-level integration、software runtime 和 benchmark workload。

## 与 NMC 的边界

HBM base die、interposer、package-side logic 上的 compute 在本 wiki 中归 NMC。这个边界会让某些 “HBM near-memory” 方案从 DRAM-PIM 移到 NMC 讨论。这样做不是降低其价值，而是避免把 memory die/bank processing 与 package-level accelerator 混成同一类。

## 指标口径

DRAM-PIM 至少需要记录：

| 指标 | 为什么重要 |
| --- | --- |
| host offload ratio | 判断真正下沉了多少工作 |
| energy per byte moved | 判断减少搬运是否转成系统收益 |
| bandwidth utilization | 判断 PIM 是否改善 memory-bound 路径 |
| supported operation set | 判断能跑 kernel 还是只能做演示操作 |
| command/controller changes | 判断生态改造成本；参考 RAM wiki 的 [DRAM command path](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md) |
| result return frequency | 判断 host synchronization 是否吞掉收益 |

## 一句话理解

DRAM/HBM/GDDR-PIM 的核心不是阵列乘加，而是 memory die/bank 内 processing 与 host/controller/runtime 的协同；实现位置越靠近 bank，逻辑越受限，系统接口越关键。

## 研究启示

DRAM-PIM 的研究应从真实 memory-bound workload 出发，而不是从“在内存里加算力”出发。关键开放问题包括 memory command 如何表达 compute、多个 bank 如何调度、结果如何与 host 协同、PIM 与 GPU/NPU fallback 的边界如何自动划分。产业上，memory vendor 具备供应链优势，但客户采用取决于软件栈和端到端收益，而不是单个 PIM operation 的峰值数字。
