# 术语表

上级：[10 Reference](README.md)
相关：[CIM/PIM/NMC 分类](../01-overview/cim-pim-nmc-taxonomy.md), [两条正交主线](../01-overview/two-axes-memory-and-paradigm.md), [指标术语表](../09-research-frontier/metrics-glossary.md)

## 这页在回答什么问题

这页回答：本 wiki 中高频术语的精确定义是什么，哪些词不能混用。

| 术语 | 本 wiki 定义 | 常见误用 |
| --- | --- | --- |
| CIM | compute 在 memory cell 内或紧邻 cell 的 array path 中发生，cell/bitline/wordline/sense path 参与计算 | 把任何 in-memory marketing name 都叫 CIM |
| PIM | memory die 或 bank 内有独立 compute unit，compute 与 cell 分离 | 把 Samsung HBM-PIM、SK hynix AiM/AiMX 归到 CIM |
| NMC | compute 靠近 memory，但不在 memory die 上，如 base die、interposer、package-side、module-side、CXL memory-side accelerator | 把 near-memory 等同于低价值或等同 CIM |
| In-memory computing | 行业宽泛用语，需要回落到 CIM/PIM/NMC 判定 | 直接按名字归 CIM |
| Near-data computing | compute 靠近数据所在位置，可能是 PIM 或 NMC | 和 CIM 混用 |
| Memory-side processing | memory product 或 memory 近侧执行部分处理 | 不说明 die/module/package 位置 |
| 物理同混 | storage structure 与 compute execution path 共享物理结构 | 只要距离近就叫同混 |
| Cell-level compute | cell 状态直接参与逻辑或 MAC | 把 bank-level unit 叫 cell-level |
| Array-path compute | bitline、wordline、SA 等 array path 参与计算 | 把 local accumulator 单独当判据 |
| Memory technology | 计算依附的存储介质或 memory product，例如 SRAM、ReRAM、Flash、PCM、MRAM、DRAM/HBM/GDDR | 用 memory 名称推断 compute paradigm |
| Compute paradigm | 计算如何发生：analog、digital、mixed-signal | 把 SRAM-CIM 自动等同 digital，或把 ReRAM-CIM 自动等同可量产 analog |
| SRAM-CIM | SRAM cell/bitline/sense path 被改造成计算路径 | 把所有使用 SRAM 存权重的 NPU 都叫 SRAM-CIM |
| ReRAM/RRAM-CIM | ReRAM 电导/电阻态直接表示权重并参与 MVM/MAC | 只看 crossbar 理想能效，忽略 drift、IR drop、sneak path |
| Flash-CIM | Flash/floating-gate 状态作为 analog 权重，代表案例是 Mythic 路线 | 认为成熟 Flash 工艺自动解决 analog 推理可靠性 |
| PCM-CIM | PCM 相变/电阻状态参与存算 | 忽略 drift 和写入代价 |
| MRAM-CIM | MRAM 非易失状态用于 CIM，更多偏 binary/digital-like | 假设天然适合高精度 analog |
| DRAM/HBM/GDDR-PIM | DRAM/HBM/GDDR memory die/bank 内加入 processing unit | 把它塞进 analog/digital CIM 三分法 |
| HBM-PIM | HBM memory die/bank 内加入 PIM compute unit | 写成 HBM-CIM |
| GDDR-PIM / AiM | GDDR memory chip 内加入 compute function | 写成 CIM 公司路线 |
| Gain-cell CIM | 用 gain-cell macro 支持 CIM，常见于研究型 SRAM/DRAM-like macro | 和标准 6T SRAM-CIM 混为一谈 |
| Embedded NVM | 嵌入式非易失存储，如 eFlash/ReRAM/MRAM/PCM | 认为只要 NVM 就适合 CIM |
| 6T/8T/10T SRAM cell | SRAM bitcell 变体，影响读写隔离和 compute path | 只看 bit 数不看 read disturb |
| DRAM 1T1C cell | DRAM capacitor + access transistor 结构 | 和 HBM-PIM 的独立 compute 混淆 |
| Crossbar array | 交叉阵列结构，ReRAM/PCM 等 analog MVM 常见 | 忽略 sneak path 和 IR drop |
| Conductance state | 用电导状态表达权重 | 认为电导状态长期不漂移 |
| Multi-level cell | 一个 cell 存多个状态 | 只看密度，不看 state margin |
| Retention | 状态长期保持能力 | 只在存储中重要，忽略对推理精度影响 |
| Endurance | 可写擦次数或状态更新寿命 | 忽略 retraining/personalization 影响 |
| Write verify | 写入后校验状态是否达到目标 | 忽略其能耗和延迟 |
| Read disturb | 读操作扰动存储状态 | 只在 DRAM/Flash 中考虑，忽略 CIM 读计算压力 |
| Analog CIM | 用电流、电压、电荷或电导等连续物理量执行乘加或累加 | 认为 analog 一定比 digital 更好 |
| Digital CIM | 用 bitwise、bit-serial、popcount、local digital accumulation 等数字方式在 array 近侧计算 | 把普通 SRAM buffer + MAC array 也叫 CIM |
| Mixed-signal CIM | array 内或近侧使用 analog/charge/current domain，外围使用数字控制、转换和累加 | 忽略 ADC/DAC/SA 的面积和功耗 |
| Bit-serial / bit-parallel | 多 bit 操作按 bit slice 多周期或并行完成 | 只看能耗，不看 latency/面积 |
| Bitwise compute / popcount | 位操作和统计 1 的数量，binary CIM 常见 | 直接等同高精度 MAC |
| Current/charge/voltage/time-domain accumulation | 用电流、电荷、电压或时间表达累加 | 忽略 variation、泄漏、线性度或 timing error |
| MVM / MAC | matrix-vector multiplication / multiply-accumulate | 不说明矩阵规模、precision 或 MAC 算 1 op 还是 2 ops |
| Weight-stationary / activation-stationary | 权重或输入尽量驻留以减少搬移 | 忽略 partial sum 和 fallback |
| CIM macro | 一个局部 compute-memory array block，可能包含 driver、SA/ADC、local accumulator | 把 macro 指标外推成 chip/system 指标 |
| Wordline / bitline / source line | array 内访问和读出路径，也是 CIM compute path 的核心对象 | 只当传统读写控制线 |
| Sense amplifier / ADC / DAC | 读出判决和数模转换外围 | 不计入面积/功耗 |
| Local accumulator | macro/tile 近侧 partial sum 累加器 | 单独作为 CIM 判据 |
| Peripheral | array 周边 driver、SA、ADC/DAC、buffer、controller 等 | 只报 array-only 指标 |
| IR drop / sneak path | 线阻压降和 crossbar 非目标路径电流 | 理想阵列里常被忽略 |
| Device variation / mismatch / thermal drift | 器件差异、不匹配和温度漂移 | 当成可完全校准 |
| Calibration | 硅后或运行时校准误差 | 认为一次校准长期有效 |
| Noise-aware / quantization-aware training | 训练中模拟硬件噪声或低比特量化 | 用软件掩盖硬件问题而不计成本 |
| Tiling / folding / duplication | 大 tensor 映射到有限 array 的切分、复用和复制 | 忽略 latency、容量和写入成本 |
| Tile | 多个 macro 加局部 buffer、control、reduction 组成的更大单元 | 忽略 tile 间互连和调度 |
| Bank/channel/rank | DRAM/HBM/GDDR 组织层级 | 和 CIM tile 混用 |
| HBM stack / TSV / base die | HBM 堆叠、垂直互连和逻辑/接口 die | 忽略 base die compute 在本 wiki 归 NMC |
| Memory controller | 管理 memory command/timing 和访问调度 | PIM 中会成为关键协同点 |
| Host offload / runtime / kernel mapping | host 下沉任务、运行时调度和算子映射 | 认为硬件峰值自动可用 |
| Reduction network | 合并 partial sum 的网络 | 忽略其成为瓶颈 |
| Data movement | 数据在 array/tile/chip/memory/host 间移动 | 只看 compute energy |
| Memory wall / von Neumann bottleneck | 计算与 memory 分离导致的带宽、延迟、能耗瓶颈 | 认为 CIM 完全解决 |
| CNN / Transformer / attention / KV cache / LLM decode | 主要 AI workload 和子结构 | 用 CNN 结论直接判断 LLM |
| Memory-bound / compute-bound | 受数据搬移或计算吞吐限制 | 不做 workload profiling |
| Sparsity | 稀疏性，可减少计算/搬移但增加控制复杂度 | 假设免费跳零 |
| INT8/INT4/binary/ternary/mixed precision | 量化和混合精度格式 | 跨精度比较 TOPS |
| Model adaptation / compiler mapping / runtime scheduling | 模型、编译和运行时为硬件约束做适配 | 忽略软件成本 |
| Macro-level / chip-level / system-level | 指标或证据覆盖的层级 | 混用论文、产品和系统指标 |
| Test chip / prototype / customer evaluation / product chip / volume production | 从验证到量产的成熟度口径 | 把 demo 当量产 |
| Silicon measurement / simulation-only | 实测或仿真证据 | 把仿真当硅后结果 |
| Peak TOPS/W / TOPS/mm2 / TFLOPS/W / energy/MAC / energy/byte | 论文常见指标 | 详细口径见 [09 指标术语表](../09-research-frontier/metrics-glossary.md) |

几个特殊命名纪律：

- Samsung HBM-PIM：PIM，不是 CIM。
- SK hynix GDDR6-AiM/AiMX：PIM，不是 CIM。
- UPMEM：本 wiki 归 NMC 对照；官方材料常使用 PIM 口径，但正文分类以 01 taxonomy 为准，不能当 cell-level CIM。
- Mythic：Flash-based analog CIM。
- Axelera：SRAM-based digital CIM。

## 一句话理解

本 wiki 的术语表先看计算位置和 cell/array path，再看公司或论文使用的名字。

## 维护原则

术语表只维护短定义和误用提醒，详细机制回链到 02-09。新增术语时必须先确认它属于分类、介质、范式、电路、系统、软件、产业成熟度还是指标口径，避免把 glossary 写成另一份正文教程。
