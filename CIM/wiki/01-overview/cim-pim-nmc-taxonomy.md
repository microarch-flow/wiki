# CIM/PIM/NMC 的严格区分

上级：[01 Overview](./README.md)
相关：[两条正交主线](./two-axes-memory-and-paradigm.md), [CIM 整体分类体系](./taxonomy.md)

## 这页在回答什么问题

当论文、公司新闻和媒体文章都使用 “in-memory computing” 时，怎样判断一个对象到底是 CIM、PIM 还是 NMC？这页给出本 wiki 的硬规则，后续所有章节按这个规则命名和归类。

## 本 wiki 的三条定义

**CIM (Compute-in-Memory)**：计算发生在 memory cell 内，或紧邻 cell 的 array path 中，存储单元、bitline、wordline、sense path 等物理结构直接参与计算。关键不是“离 memory 很近”，而是 compute 与 storage 在物理执行路径上同混。

**PIM (Processing-in-Memory)**：在 memory die 或 memory bank 内集成独立 compute unit，但 compute 与 memory cell 分离。PIM 仍然在 memory die 的边界内做 processing，但不要求 bitcell 本身执行乘加。

**NMC (Near-Memory Computing)**：计算靠近 memory，但不在 memory die 上，典型位置包括 HBM base die、logic die、interposer、package-side logic、memory module 附近、CXL memory appliance 或靠近内存控制器的 accelerator。NMC 关注系统距离和带宽路径，不等于 memory array 参与计算。

这三个词不是简单包含关系。本 wiki 不使用 “NMC 包含 PIM，PIM 包含 CIM” 作为定义，因为这种写法会把物理机制、产品边界和系统距离混在一起。我们用两个判断轴：计算位置在哪里，memory cell/array path 是否参与计算。

## 判定表

| 类别 | 计算位置 | Cell/array path 是否参与计算 | 典型对象 | 本 wiki 归类 |
| --- | --- | --- | --- | --- |
| CIM | cell 内或紧邻 cell 的 array path | 是 | SRAM bitline compute、ReRAM crossbar MVM、Flash analog CIM | CIM |
| PIM | DRAM/HBM/GDDR memory die 或 bank 内的独立 compute | 否 | Samsung HBM-PIM、SK hynix GDDR6-AiM/AiMX 的 memory-die processing 语境 | PIM |
| NMC | memory 附近但在 memory die 外 | 否 | HBM base die compute、UPMEM、CXL memory-side accelerator、interposer/logic-side near-memory compute | NMC |

## 边界案例怎么判

HBM base die 上的 compute 在本 wiki 中归 NMC，因为它不在 memory die 上。DRAM/HBM memory die 或 bank 内的独立 compute 才归 PIM；interposer、package logic、standalone logic die 或 memory module 旁的 compute 也归 NMC，除非资料能明确证明计算发生在 memory die/bank 内。

SRAM array 附近加 digital logic 也要细分。如果只是传统 SRAM buffer 旁边放一个 MAC array 或 accumulator，它不是 CIM；只有 SRAM cell、read bitline、wordline activation、sense amplifier 等 array path 参与 bitwise compute、popcount、charge sharing 或 current-domain accumulation，它才进入 SRAM-CIM 的讨论。local accumulator 可以是 CIM macro 的结果路径，但不能单独作为 CIM 判据。

DRAM subarray 内部做 RowClone、Ambit 类位操作与 HBM-PIM 不是同一类。前者如果利用 DRAM cell/bitline 物理行为执行逻辑，更接近 DRAM-CIM 或 in-DRAM bitline compute；后者在本 wiki 语境下指 DRAM/HBM 体系内加入独立 processing unit，更接近 PIM。为了避免混乱，本 wiki 的 02 主线把 DRAM/HBM 重点放在 DRAM-PIM，而不是把所有 DRAM 内计算都叫 CIM。

## 为什么这个区分重要

术语错误会直接导致比较错误。把 Samsung HBM-PIM 与 ReRAM crossbar 放在同一个 “CIM 能效表” 中比较，就会把 system-level memory bandwidth optimization 和 array-level analog MVM 混成一个指标问题。把 UPMEM 这类 NMC 对照误写成 CIM，又会低估 host interface、memory module、programming model 的系统代价。

正确分类后，读者才能问正确的问题：CIM 要问 cell 稳定性、ADC/peripheral、array mapping 和 macro-to-system 衰减；PIM 要问 memory command、bank/channel 粒度、host offload 和 workload memory-bound 程度；NMC 要问离 memory 还有多远、软件接口如何表达、与 CPU/GPU/NPU 的协同成本是否低于搬运收益。

## 本 wiki 的命名纪律

Samsung HBM-PIM、SK hynix AiM/AiMX：归 PIM，不归 CIM。公司卡片使用 `pim-companies-*` 前缀。

UPMEM：归 NMC，用作 CIM/PIM 的对照。公司卡片使用 `nmc-companies-*` 前缀。

Mythic、Axelera：按具体实现归 CIM。Mythic 是 Flash-based analog CIM 的商业化教训；Axelera 作为 SRAM-CIM/digital-friendly 商业化样本处理。

Near-memory、in-memory、AiM、processing-in-memory 这些行业用词在引用资料时可以保留原文，但正文判断必须落回本页定义。

## 常见误解

常见误解：PIM 是 CIM 的一种。实际上，PIM 可以完全不让 cell 参与计算，它的核心是 memory product 内加入 processing unit。

常见误解：NMC 比 PIM/CIM 更“不纯”，所以技术价值更低。实际上，NMC 牺牲了物理近邻程度，但可能获得更好的工艺、软件和可编程性。

常见误解：名称里带 “in-memory” 就应归 CIM。实际上，本 wiki 看机制，不看 marketing name。

## 一句话理解

CIM/PIM/NMC 的分界线不是宣传词，而是计算发生的位置和 memory cell/array path 是否真正参与计算。
