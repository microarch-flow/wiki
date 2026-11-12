# 02 Memory Technologies

上级：[CIM Wiki](../README.md)
相关：[两条正交主线](../01-overview/two-axes-memory-and-paradigm.md), [CIM/PIM/NMC 的严格区分](../01-overview/cim-pim-nmc-taxonomy.md)

## 这页在回答什么问题

为什么 CIM/PIM 不能只按 analog、digital、mixed-signal 来讲，还必须先按 memory technology 拆开？因为 cell 物理、读写路径、容量、工艺和可靠性决定了哪些 compute paradigm 自然成立，哪些只是论文里可以做但工程上不划算。

## 本章的横轴

本章按 memory technology 组织，而不是按公司或论文名组织。每条路线都要回答两个问题：第一，计算是否真的发生在 memory cell 或 array path 中；第二，这类 memory 更自然地走 analog、digital 还是 mixed-signal。

| 路线 | 归类 | 主导 paradigm | 核心判断 |
| --- | --- | --- | --- |
| [SRAM-CIM](./sram-cim-foundation.md) | CIM | digital / mixed-signal | 最接近 CMOS 产品化，但容量和面积限制明显 |
| [ReRAM-CIM](./reram-as-compute-element.md) | CIM | analog / mixed-signal | 最像 array-native MVM，但非理想性和写入成本最重 |
| [Flash-CIM](./flash-cim-niche.md) | CIM | analog / mixed-signal | 适合固定权重 edge niche，商业窗口窄 |
| [PCM/MRAM-CIM](./pcm-mram-for-cim.md) | CIM 研究分支 | 取决于 device | PCM 偏 analog multi-level，MRAM 更偏 binary/digital-like |
| [DRAM/HBM/GDDR-PIM](./dram-pim-foundation.md) | PIM | independent digital processing | 重点是 memory die/bank 内 processing，不是 array-native CIM |

HBM base die、interposer、package-side logic 或 memory module 旁 compute 按 01 章定义归 NMC，不放入 DRAM-PIM 主线。

## 推荐阅读顺序

1. [SRAM-CIM 基础](./sram-cim-foundation.md)
2. [SRAM-CIM 深入](./sram-cim-deep-dive.md)
3. [ReRAM 作为计算元件](./reram-as-compute-element.md)
4. [ReRAM-CIM 深入](./reram-cim-deep-dive.md)
5. [DRAM-PIM 基础](./dram-pim-foundation.md)
6. [DRAM-PIM 深入](./dram-pim-deep-dive.md)
7. [Flash CIM](./flash-cim-niche.md)
8. [PCM/MRAM for CIM](./pcm-mram-for-cim.md)
9. [Memory Tech Comparison Matrix](./memory-tech-comparison-matrix.md)

## 一句话理解

Memory technology 决定 CIM/PIM 的物理边界：SRAM 追求工程可落地，ReRAM/Flash 追求阵列原生 MVM，DRAM/HBM/GDDR-PIM 追求大容量 memory-side 系统收益。

## 研究启示

本章后续研究应避免把 “memory 更靠近 compute” 当成统一结论。每条路线都要先证明它满足 01 章的计算位置定义，再证明它的主导 paradigm 与该 memory 的物理特性匹配；否则普通 memory + 旁路数字逻辑、PIM、NMC 和真正 CIM 会再次混在同一张表里。
