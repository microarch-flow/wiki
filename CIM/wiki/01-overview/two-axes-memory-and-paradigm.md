# 两条正交主线：Memory Technology × Compute Paradigm

上级：[01 Overview](./README.md)
相关：[CIM/PIM/NMC 的严格区分](./cim-pim-nmc-taxonomy.md), [CIM 整体分类体系](./taxonomy.md), [03 Paradigm × Memory Crossmap](../03-compute-paradigms/paradigm-memory-crossmap.md)

## 这页在回答什么问题

为什么只按 SRAM、ReRAM、DRAM 分类不够，按 analog、digital、mixed-signal 分类也不够？CIM/PIM/NMC 的设计空间必须同时看 memory technology 横轴和 compute paradigm 纵轴，否则会把物理介质、计算机制和产品路线混成一团。

## 横轴：Memory Technology

横轴回答“计算依附在哪类 memory 物理对象或 memory product 上”。本 wiki 的横轴先抓三条主线：

| 横轴路线 | 本质问题 | 典型归类 |
| --- | --- | --- |
| SRAM-CIM | 片上 SRAM cell/bitline/sense path 能否被改造成低功耗计算宏 | CIM |
| ReRAM/新器件 CIM | 非易失器件的电导、电阻态或相变状态能否直接承载权重和 MVM | CIM |
| DRAM/HBM/GDDR-PIM | memory die 或 bank 内加入 processing unit 后，能否减少 processor-memory 往返 | PIM |

Flash、PCM、MRAM 会在 02 章作为 NVM 分支处理。Flash CIM 更像 niche 路线，Mythic 是代表案例；PCM/MRAM 与 ReRAM 共享部分“非易失、多状态、写入代价、可靠性”问题，但 device physics 和工程成熟度不同。

## 纵轴：Compute Paradigm

纵轴回答“乘法、累加和读出以什么计算范式发生”。

| 纵轴路线 | 计算方式 | 主要收益 | 主要代价 |
| --- | --- | --- | --- |
| Analog CIM | 用电流、电压、电荷等连续物理量表达乘加 | 阵列内并行、局部能效高 | ADC/DAC、噪声、variation、校准、精度上限 |
| Digital CIM | 用 bitwise logic、bit-serial、popcount、local digital accumulation 执行 | 精度可控、验证友好、CMOS 流程兼容 | 面积和布线增加，能效上限不如理想 analog 激进 |
| Mixed-signal CIM | 阵列内保留 analog/charge/current 域收益，外围做数字控制、转换和累加 | 在能效和可控性之间折中 | 边界复杂，指标容易被外围口径美化 |

PIM 不应直接塞进 analog/digital/mixed-signal CIM 三分法，因为 PIM 的 compute unit 可以是独立 digital processing block。它仍然需要讨论数值格式和软件栈，但它不是“array-native compute paradigm”的同一层问题。HBM base die、interposer、package-side logic 上的 near-memory compute 不属于这里的 DRAM/HBM/GDDR-PIM 横轴，而应作为 NMC 边界案例处理。

## 交叉矩阵

| Memory technology | Analog | Digital | Mixed-signal | 结论 |
| --- | --- | --- | --- | --- |
| SRAM-CIM | 可用 charge/current-domain 做局部计算，但受 noise、read disturb、ADC/SA 约束 | 最工程友好，常见于 bitwise、bit-serial、popcount 类宏 | 很常见，用模拟局部累加加数字外围 | SRAM 主流更偏 digital/mixed-signal |
| ReRAM-CIM | 最自然，电导态与 Ohm/Kirchhoff 对 MVM 贴合 | 存在但会削弱 multi-level conductance 的密度/并行优势 | 常见，array analog MVM 加数字校准/累加 | ReRAM 的吸引力主要来自 analog/mixed-signal MVM |
| Flash-CIM | Mythic 类路线代表，用浮栅/电荷状态表达权重 | 不主流，失去 Flash 多状态模拟存储优势 | 需要数字外围和校准 | niche，适合固定权重 edge 推理叙事 |
| PCM/MRAM-CIM | PCM 有 analog multi-level 潜力，MRAM 更偏 binary/可靠存储 | MRAM 更容易走 binary/digital-like 路线 | 取决于 device 和读出链路 | 仍偏研究/特定场景 |
| DRAM/HBM/GDDR-PIM | 不是主线，DRAM cell analog 计算不是本 wiki DRAM-PIM重点 | memory die/bank 内 processing unit 多为 digital | memory-side digital compute 加系统协同 | 重点是 PIM 系统路线，不是 CIM paradigm；base-die/interposer compute 归 NMC |

## 为什么两条轴必须同时出现

只说 SRAM-CIM 不够，因为 SRAM-CIM 可以是 digital bitwise，也可以是 charge-domain/mixed-signal；这两者在 ADC、精度、测试、可量产性上差别很大。只说 analog CIM 也不够，因为 ReRAM analog MVM 和 SRAM current-domain CIM 的 device variation、写入方式、容量和工艺路线完全不同。

后续 02 章从横轴出发：每篇 memory technology 都必须说明它主要适合哪条 compute paradigm，以及另外两条为什么弱。后续 03 章从纵轴出发：每篇 compute paradigm 都必须说明它主要落在哪些 memory technology 上，以及在其他 memory 上为什么不自然。

## 与其他 wiki 的连接

SRAM-CIM 要连接 RAM wiki 的 [6T SRAM cell](../../../RAM/wiki/02-sram-foundations/6t-cell-bistable-storage.md)、[SRAM array organization](../../../RAM/wiki/02-sram-foundations/sram-array-organization.md) 和 [scratchpad vs cache](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md)，因为 CIM 是 SRAM array 的一种非平凡使用方式，不是普通 cache。

DRAM/HBM-PIM 要连接 RAM wiki 的 [bank organization](../../../RAM/wiki/04-dram-foundations/bank-organization-parallelism.md)、[HBM stacked wide I/O](../../../RAM/wiki/05-dram-protocol-families/hbm-stacked-wide-io.md) 和 [DRAM command timing](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md)，因为 PIM 的难点在 command、bank/channel 粒度和 host 协同。

系统互连和 reduction 要连接 NoC wiki 的 [memory-centric NoC](../../../NOC/wiki/06-ai-noc-specifics/memory-centric-noc.md) 与 [reduction and collective networks](../../../NOC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md)，因为 CIM macro 一旦组成 tile/chip，瓶颈会从 array 移到数据流、归约和互连。

## 一句话理解

Memory technology 决定“计算依附在哪里”，compute paradigm 决定“计算如何发生”；CIM/PIM/NMC 的真实判断必须同时落在这两个坐标上。
