# 08 产业与产品

上级：[CIM Wiki](../README.md)
相关：[CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md), [应用负载](../07-workloads/README.md), [研究前沿](../09-research-frontier/README.md)

## 这页在回答什么问题

这一章回答一个工程问题：把 CIM/PIM/NMC 从论文、macro 或样片推进到客户系统时，真正要交付的是什么。

08 的视角不是“哪篇论文指标最高”，而是“谁控制哪段产业资源、产品处在哪个层级、客户能不能接入、量产风险落在哪里”。同一家公司如果也有研究价值，会留到 [09 研究前沿](../09-research-frontier/README.md) 从论文贡献和开放问题切入。

本章使用 [01 的 taxonomy](../01-overview/cim-pim-nmc-taxonomy.md)：

| 分类 | 本章判断口径 | 公司卡片前缀 |
| --- | --- | --- |
| CIM | memory cell、bitline、wordline、sense path 或 array path 直接参与计算，计算与存储物理同混 | `cim-` |
| PIM | DRAM/HBM/GDDR memory die 或 bank 内有独立 compute unit，compute 与 cell 分离 | `pim-` |
| NMC | compute 在 memory 近侧的 module、package、base die、interposer、host-visible memory expansion 路径上 | `nmc-` |

公司宣传中的 “in-memory”、“AiM”、“PIM”、“analog AI” 不能直接决定分类；本 wiki 的基础 taxonomy 仍以计算发生的位置和与 cell/array 的关系为准。Samsung HBM-PIM 与 SK hynix GDDR6-AiM/AiMX 在这里归 PIM，不归 CIM。UPMEM 是一个特殊的产业对照卡：官方口径和 die-level 位置更接近 PIM，但本章把它放在 `nmc-` 文件中，是为了单独讨论 DIMM/server 形态的 near-data 产品化、host+DPU 编程和系统接入；这个对照卡不覆盖 01 章的基础 taxonomy。

| 页面 | 产业问题 |
| --- | --- |
| [产业全景](industry-landscape.md) | startup、memory vendor、foundry/IP、system company 各自掌握什么资源 |
| [价值链与商业化](value-chain-and-commercialization.md) | 从 research macro 到客户部署，中间缺哪些工程环节 |
| [制造与测试挑战](manufacturing-and-test-challenges.md) | CIM/PIM/NMC 在工艺、DFT、封装、热和系统验证上的瓶颈 |
| [公司比较矩阵](company-comparison-matrix.md) | 如何用统一口径比较不同路线，而不是横比宣传 TOPS |
| [公司卡片](company-cards/README.md) | Mythic、Axelera、Samsung、SK hynix、UPMEM 的具体产业状态 |

阅读本章时要持续区分五个层级：macro、test chip、product chip、module/card、system/platform。CIM macro 的 TOPS/W 不能和 PIM card 的 system demo 横比；PIM 的 bandwidth/energy-per-byte 也不能和 analog CIM 的 energy-per-MAC 直接横比。

## 一句话理解

08 章把 CIM/PIM/NMC 从“技术路线”翻译成“产品、供应链、软件接入和客户验证”的问题。

## 产业启示

CIM 产业化的难点不在“有没有更高的单点能效数字”，而在能否把 array/macro、芯片、封装、驱动、编译器、模型适配、客户工作负载和量产测试连成一条可交付链。PIM 和 NMC 的商业化压力更靠近 memory ecosystem、host interface 与 runtime integration；CIM 的压力更靠近制造测试、校准、精度和模型移植。
