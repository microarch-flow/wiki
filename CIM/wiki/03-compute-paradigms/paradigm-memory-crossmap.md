# 三种 Paradigm × 三种 Memory：哪些组合是主流、哪些罕见、为什么

上级：[03 Compute Paradigms](./README.md)
相关：[Memory Tech Comparison Matrix](../02-memory-technologies/memory-tech-comparison-matrix.md), [两条正交主线](../01-overview/two-axes-memory-and-paradigm.md)

## 这页在回答什么问题

如果 02 是横轴、03 是纵轴，那么哪些交叉点是真主线，哪些只是研究边界或术语陷阱？这页把 memory technology 和 compute paradigm 合成一张判断表。

## Crossmap

| Memory / Paradigm | Analog CIM | Digital CIM | Mixed-Signal CIM |
| --- | --- | --- | --- |
| SRAM-CIM | 可做 charge/current-domain，但 multi-bit 不自然 | 主流产品化方向，bitwise/bit-serial/popcount | 很常见，bitline 局部累加 + SA/ADC/数字累加 |
| ReRAM-CIM | 最自然，conductance MVM | 可做但削弱 ReRAM 核心优势；离开 array path 不算 CIM | 现实落点，analog MVM + ADC/校正/mapping |
| Flash-CIM | 固定权重 analog 路线，Mythic 代表 | 不主流，变成 NVM + logic 后优势弱 | 现实落点，cell 权重 + 数字校准 |
| PCM-CIM | 有 multi-level analog 潜力，但 drift 重 | 可做但不突出 | 用数字校正补偿 drift |
| MRAM-CIM | 不自然，缺少稳定多级 analog 权重优势 | 只有 read/sense path 参与 compute 时成立 | 弱路线；read/sense path + comparator/SA correction 参与计算时才可能成立 |
| DRAM/HBM/GDDR-PIM | 不属于本 CIM 纵轴 | PIM compute unit 可为 digital processing | PIM 系统可含 mixed circuits，但不是 array-native CIM |

## 三个主流组合

SRAM + digital/mixed-signal 是工程主线。它牺牲理想 analog 能效，换取 CMOS 兼容、确定性和 SoC 集成。

ReRAM/Flash + analog/mixed-signal 是研究和 niche 产品主线。它利用 cell 物理状态做权重和局部 MVM，但必须用数字外围处理误差。

DRAM/HBM/GDDR + PIM digital processing 是系统主线。它不属于 CIM paradigm 矩阵的赢家，而是 memory-bound workload 的 PIM 路线。

## 罕见组合为什么罕见

SRAM pure analog 不自然，因为 SRAM 是稳定二值 cell，multi-bit analog 权重需要大量编码和外围。ReRAM pure digital 不自然，因为它放弃 conductance MVM 的核心优势。MRAM analog 不自然，因为 MRAM 的主流优势是二值非易失可靠性，而不是多级 analog conductance。

DRAM analog CIM 研究存在，但本 wiki 把 DRAM/HBM 主线放在 PIM，因为大模型和 HPC 场景里更重要的是大容量 memory-side processing，而不是把 1T1C cell 改造成通用 analog MAC。

## 一句话理解

主流交叉点只有少数：SRAM 偏 digital/mixed-signal，ReRAM/Flash 偏 analog/mixed-signal，DRAM/HBM/GDDR 偏 PIM digital processing；其他组合要么是研究边界，要么容易越过 CIM/PIM/NMC 术语边界。

## 研究启示

Crossmap 的价值是防止路线错配。后续读论文时，先把方案放进这张表：如果它选择了罕见组合，就必须说明为什么违背 memory 本性仍然划算；如果它落在主流组合，也必须证明外围、系统和软件没有吞掉理论优势。
