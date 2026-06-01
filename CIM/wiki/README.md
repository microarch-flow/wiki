# CIM Wiki

相关：[知识地图](./SUMMARY.md), [按目标的阅读路径](./10-reference/reading-roadmap-by-goal.md), [建模参数字典](./05-architecture-and-system/cim-modeling-parameter-schema.md)

## 这份 wiki 在回答什么问题

CIM（Compute-in-Memory）领域最大的困难不是单点技术难，而是**术语、层级和指标极易混淆**：有人把 HBM-PIM 叫 CIM，有人把 SRAM 旁加逻辑也叫 CIM，有人用 macro 级 TOPS/W 直接论证系统收益。这份 wiki 的目标是建立一套**不会混乱的坐标系**，让器件、电路、架构、软件、workload 和产业的判断都落在同一套定义上，从而能正确比较路线、论文和产品。

本 wiki 面向把 CIM 知识用于**架构探索与建模**的读者：每一章末尾都有「建模启示 / 研究启示」，把该层知识折叠成可参数化的 Resource / Topology / Interaction / Capability 四元组。如果你的目的是给架构探索工具建模，先读[建模参数字典](./05-architecture-and-system/cim-modeling-parameter-schema.md)，它把散落各章的建模提示汇总成一张可直接实现的参数表。

## 全 wiki 的两个锚点

整份 wiki 由两件事钉死，后续所有命名和比较都必须落回它们：

1. **计算位置三分** — [CIM/PIM/NMC 的严格区分](./01-overview/cim-pim-nmc-taxonomy.md)：CIM 指计算发生在 memory cell 内或紧邻 cell 的 array path 中；PIM 指 memory die/bank 内加独立 compute unit；NMC 指 compute 靠近 memory 但不在 memory die 上。
2. **两条正交主线** — [Memory Technology × Compute Paradigm](./01-overview/two-axes-memory-and-paradigm.md)：横轴是权重/计算依附的 memory 物理对象（SRAM / ReRAM / Flash / PCM / MRAM / DRAM），纵轴是乘加发生的形式（analog / digital / mixed-signal）。

任何指标还必须标注**系统层级**（cell / macro / tile / chip / package / card / system）和**证据来源**（silicon / post-layout / simulation / analytical / vendor demo），否则不可横比。详见 [指标术语表](./09-research-frontier/metrics-glossary.md)。

## 十章地图

| 章 | 主题 | 核心问题 |
| --- | --- | --- |
| [01 Overview](./01-overview/README.md) | 坐标系 | CIM/PIM/NMC 怎么分、两条主线是什么、为什么现在重生 |
| [02 Memory Technologies](./02-memory-technologies/README.md) | 横轴 | 每类 memory 的物理决定哪种 paradigm 自然成立 |
| [03 Compute Paradigms](./03-compute-paradigms/README.md) | 纵轴 | 乘加以 analog / digital / mixed-signal 哪种形式发生 |
| [04 Circuit and Macro](./04-circuit-and-macro/README.md) | 电路与宏 | array、外围、编码、非理想性、精度如何决定 macro 指标 |
| [05 Architecture and System](./05-architecture-and-system/README.md) | 架构与系统 | macro 收益如何活到 tile/chip/system，如何建模 |
| [06 Software Stack](./06-software-stack/README.md) | 软件栈 | 模型如何编译、量化、映射到 array/bank，fallback 如何影响可用性 |
| [07 Workloads](./07-workloads/README.md) | 工作负载 | 什么 workload 适合 CIM/PIM/NMC，瓶颈在 compute 还是 memory |
| [08 Industry and Products](./08-industry-and-products/README.md) | 产业与产品 | 公司材料说的是 macro、chip、prototype 还是量产 |
| [09 Research Frontier](./09-research-frontier/README.md) | 研究前沿 | 指标如何精确比较、open problems、论文怎么读 |
| [10 Reference](./10-reference/README.md) | 速查 | 术语表、决策树、高频问题、按目标的阅读路径 |

## 从哪里开始

- **第一次读**：按 [01 Overview](./01-overview/README.md) 的推荐顺序建立坐标系，再进入 02/03。
- **带着具体目标**：直接看 [按目标的阅读路径](./10-reference/reading-roadmap-by-goal.md)（建立判断力 / 懂电路 / 懂系统 / 懂软件 / 评估 workload / 看产业 / 读论文，每条只给 5–7 篇必读）。
- **要做架构建模**：先读 [建模参数字典](./05-architecture-and-system/cim-modeling-parameter-schema.md) 与 [性能与能效建模](./05-architecture-and-system/performance-energy-modeling.md)，再回头按需补器件/电路细节。
- **要全量目录**：见 [知识地图](./SUMMARY.md)。

## 一句话理解

这份 wiki 不是 CIM 技术综述，而是一套坐标系：先固定计算位置、两条主线、系统层级和证据等级，后面才有资格比较路线、论文、产品，并把知识折叠成可建模的参数。
