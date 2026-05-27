# CIM 整体分类体系

上级：[01 Overview](./README.md)
相关：[CIM/PIM/NMC 的严格区分](./cim-pim-nmc-taxonomy.md), [两条正交主线](./two-axes-memory-and-paradigm.md)

## 这页在回答什么问题

在严格区分 CIM/PIM/NMC 之后，整份 wiki 还需要一张更大的分类图：一个方案可以同时属于某个计算位置、某条 memory technology、某种 compute paradigm、某个系统层级和某类 workload。只有把这些维度拆开，比较才不会失真。

## 维度一：计算位置

计算位置是最高优先级，因为它决定术语归类：

| 位置 | 分类 | 关注问题 |
| --- | --- | --- |
| cell/bitline/wordline/sense path | CIM | cell 稳定性、读写扰动、ADC/SA、array mapping |
| memory die/bank 内独立 compute | PIM | bank/channel 粒度、memory command、host offload |
| memory die 外但靠近 memory | NMC | HBM base die、logic die、interposer、接口、软件模型、系统集成 |

这一维度禁止被 marketing name 覆盖。文件名、公司卡片和正文判断都应按这个维度先归类。

## 维度二：Memory Technology

Memory technology 决定权重或数据依附的物理对象：

| 路线 | 主要对象 | 典型优势 | 典型限制 |
| --- | --- | --- | --- |
| SRAM-CIM | 6T/8T/10T SRAM array | CMOS 兼容、读写快、片上集成自然 | 容量小、面积贵、leakage、宏到系统收益衰减 |
| ReRAM-CIM | resistive crossbar | 高密度、非易失、analog MVM 自然 | variation、IR drop、sneak path、write/verify、retention |
| Flash-CIM | floating-gate/charge storage | 非易失、多状态、固定权重 edge 叙事 | 工艺和校准特殊，产品化窗口窄 |
| PCM/MRAM-CIM | phase-change / magnetic memory | 非易失、特定 device 优势 | 写入、耐久、读出和工艺成熟度差异大 |
| DRAM/HBM/GDDR-PIM | memory die/bank 内 processing unit | 容量和带宽强，适合 memory-bound system | compute 能力受限，接口和 runtime 复杂；base-die/interposer compute 归 NMC |

## 维度三：Compute Paradigm

Compute paradigm 决定计算以什么形式发生：

| Paradigm | 适配路线 | 判断重点 |
| --- | --- | --- |
| Analog | ReRAM、Flash、部分 SRAM current/charge-domain | ADC/DAC、噪声、variation、温漂、低比特边界 |
| Digital | SRAM-CIM、部分 MRAM/binary route | bit-serial/parallel、popcount、面积、验证、时序 |
| Mixed-signal | SRAM/ReRAM/Flash 常见折中 | analog/digital 边界、外围开销、校准、指标口径 |

同一个 memory technology 可以有多种 paradigm，同一个 paradigm 也可以落在多种 memory 上。后续 02 和 03 的交叉页会把这个矩阵展开。PIM compute unit 可以采用数字处理逻辑，但它不属于 analog/digital/mixed-signal CIM 纵轴；PIM 的数值格式和执行单元会在 DRAM-PIM 与软件栈章节单独讨论。

## 维度四：系统层级

许多 CIM 误判来自把不同层级指标直接比较：

| 层级 | 证明什么 | 不能证明什么 |
| --- | --- | --- |
| Cell/device | 物理机制能否成立 | 系统收益 |
| Macro | 局部 array + peripheral 能否闭环 | chip 利用率、host 协同 |
| Tile | 多 macro、buffer、local reduction 是否可用 | full-chip NoC 和 software 开销 |
| Chip | 片上系统是否能执行目标 kernel | 端到端客户 workload |
| System/product | 部署环境中的 latency、energy、software friction | 单独反推 cell 优劣 |

后续所有数据锚点都必须注明层级。macro-level TOPS/W 不能直接和 system-level token latency 比。

## 维度五：Workload 适配

Workload 不是最后才看的应用标签，而是反过来决定前面所有选择：

| Workload | 更关键的问题 | 更可能相关的路线 |
| --- | --- | --- |
| CNN / fixed model edge inference | 权重复用、低功耗、固定权重、模型规模 | SRAM-CIM、Flash/ReRAM CIM |
| Transformer prefill | 大 GEMM，成熟 NPU/GPU 已强 | digital CIM 或传统 NPU 对比，收益需谨慎 |
| LLM decode / long context | KV cache、权重读取、memory bandwidth、token latency | DRAM/HBM-PIM、NMC、部分 CIM 子图 |
| Sensor-side / always-on AI | standby power、唤醒延迟、固定模型 | SRAM-CIM、NVM CIM |
| HPC / graph / database memory-bound kernel | 带宽、稀疏访问、host offload | PIM/NMC |

## 一张总图

```text
对象判断顺序:

1. 计算位置 -> CIM / PIM / NMC
2. Memory technology -> SRAM / ReRAM / Flash / PCM / MRAM / DRAM-HBM-GDDR
3. Compute paradigm -> analog / digital / mixed-signal
4. 系统层级 -> cell / macro / tile / chip / system
5. Workload -> CNN / Transformer / LLM decode / edge / HPC / others
```

这个顺序不是写作格式，而是避免比较错误的检查表。

## 一句话理解

本 wiki 的 taxonomy 是多维坐标，不是一棵简单树；先判计算位置，再判 memory、paradigm、层级和 workload，才能避免把完全不同的对象放进同一类结论。
