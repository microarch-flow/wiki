# DRAM-PIM 基础：为什么在 DRAM Die 上加 Compute Unit

上级：[02 Memory Technologies](./README.md)
相关：[DRAM-PIM 深入](./dram-pim-deep-dive.md), [CIM/PIM/NMC Taxonomy](../01-overview/cim-pim-nmc-taxonomy.md), [RAM: Bank Organization](../../../RAM/wiki/04-dram-foundations/bank-organization-parallelism.md), [RAM: HBM](../../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md), [RAM: DRAM Commands](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md)

## 这页在回答什么问题

DRAM/HBM/GDDR-PIM 为什么放在 memory technology 横轴里，却又不叫 CIM？因为它的目标不是让 DRAM cell 或 bitline 做乘加，而是在 memory die 或 bank 内加入独立 compute unit，减少大容量 memory 与 processor 之间的往返。

## DRAM-PIM 的问题来源

DRAM 的价值是容量和成本，HBM/GDDR 的价值是高带宽。RAM wiki 的 [HBM stacked wide I/O](../../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md) 已经说明，HBM 通过堆叠和宽接口提高带宽；[DRAM commands](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md) 说明 ACT/RD/WR/PRE 等命令路径为什么会影响 PIM interface 设计。PIM 的收益必须穿过这些 memory command 和 controller 约束，而不是只在 compute unit 内成立。

DRAM-PIM 解决的问题是：当数据已经在 memory die/bank 中，能不能把一部分简单、规则、memory-bound 的计算也放到 memory die/bank 内，避免每次都把数据搬回 GPU/CPU/NPU。

这与 CIM 的方向不同。CIM 关注 array path 是否参与计算；DRAM-PIM 关注 memory product 内是否具备 processing capability。

## 本 wiki 的边界

本章的 DRAM-PIM 只指 memory die 或 bank 内的独立 compute unit。HBM base die、logic die、interposer、package-side logic、memory module 旁 accelerator 按 01 章归 NMC。这个边界会在后续公司卡片中继续执行。

Samsung HBM-PIM、SK hynix GDDR6-AiM/AiMX 在公开语境中归 PIM，不归 CIM；如果某个具体实现资料表明 compute 位于 HBM base die 而不是 memory die/bank，则该实现按 NMC 边界案例重评。

## 为什么 DRAM-PIM 更偏 digital processing

DRAM cell 是 1T1C，读出是破坏性读，需要 sense amplifier 恢复数据。它不是为稳定 analog MVM 设计的介质。DRAM cell 物理参与逻辑的研究存在，例如基于 bitline charge sharing 的 in-DRAM operation，但这不是本章 DRAM-PIM 的主线。

DRAM-PIM 更自然走独立 digital processing：在 bank 附近、subarray 周边或 memory die 逻辑区域放入小型 ALU、MAC、SIMD-like unit 或定制操作。它的 compute 能力不如 GPU/NPU 通用，但可以减少 memory-bound kernel 的数据移动。

## 适合的 workload

DRAM-PIM 更适合 memory bandwidth 或 energy per byte 主导的场景：

| Workload | 为什么适合 |
| --- | --- |
| LLM decode / long context | KV cache 和权重读取压力大，batch 小导致 GPU 利用率不稳 |
| Recommendation / embedding | 大表访问、稀疏 gather、数据移动重 |
| HPC memory-bound kernels | 计算简单但扫描/访存量大 |
| Graph / database primitives | 指针、稀疏、过滤和聚合容易受内存路径限制 |

它不适合替代成熟 NPU/GPU 的大规模 dense GEMM 主路径。prefill 阶段的大 GEMM 已被 tensor core/NPU 强优化，PIM 必须证明减少数据移动的收益超过新增接口和调度成本。

## 一句话理解

DRAM-PIM 是 memory die/bank 内的 processing 路线，目标是减少大容量 memory-bound 数据往返，而不是让 DRAM cell 变成 analog MAC。

## 研究启示

DRAM-PIM 的开放问题主要在系统接口而不是 cell 物理：memory command 如何扩展，controller 如何调度，host 如何 offload，哪些 kernel 能在 memory die/bank 内完成，结果何时必须返回 host。产业实现依赖 memory vendor 和系统生态，技术难度不只在 compute unit，而在 JEDEC-like interface、软件栈、客户 workload 和可部署性。
