# 三大 Memory 路线全景对比

上级：[02 Memory Technologies](./README.md)
相关：[两条正交主线](../01-overview/two-axes-memory-and-paradigm.md), [Paradigm × Memory Crossmap](../03-compute-paradigms/paradigm-memory-crossmap.md)

## 这页在回答什么问题

SRAM-CIM、ReRAM/新器件 CIM、DRAM-PIM 到底应该怎么横向比较？不能只比 TOPS/W，也不能只比是否非易失；必须同时看 cell 物理、计算范式、容量、写入代价、外围开销、系统层级和成熟度。

## 路线对比矩阵

| 维度 | SRAM-CIM | ReRAM-CIM | Flash-CIM | PCM-CIM / MRAM-CIM | DRAM/HBM/GDDR-PIM |
| --- | --- | --- | --- | --- | --- |
| 归类 | CIM | CIM | CIM | CIM 研究分支，MRAM 需 read/sense path 参与计算 | PIM |
| 计算位置 | SRAM array path | resistive crossbar | Flash cell/read path | NVM cell/read path；旁路数字逻辑不算 CIM | memory die/bank 内 compute unit |
| 主导 paradigm | digital / mixed-signal | analog / mixed-signal | analog / mixed-signal | PCM 偏 analog，MRAM 仅在 array path 参与时偏 digital | independent digital processing |
| 容量 | 片上容量有限 | 高密度潜力 | 非易失固定权重 | 取决于 device | 大容量，高带宽 |
| 写入 | 快 | write/verify 复杂 | program 成本高 | PCM 写重，MRAM 较耐久 | DRAM 正常读写，compute unit 执行 |
| 精度风险 | bitline/SA/ADC 或 bit-serial 代价 | variation、IR drop、drift、ADC | threshold drift、校准 | PCM drift / MRAM multi-level 不自然；普通 MRAM + 旁路数字逻辑不算 CIM | 算子集合和数据格式受限 |
| 工艺成熟度 | 最高 | 研究/原型较多 | niche 产品尝试 | 分化明显 | memory vendor 主导 |
| 更适合 | edge SoC、小模型、固定子图 | fixed-weight edge MVM | always-on/fixed model | 特定非易失场景 | LLM decode、KV cache、HPC memory-bound |

## 不能直接横比的指标

Macro-level TOPS/W 不能和 system-level token latency 横比。SRAM-CIM macro 的 TOPS/W 可能包含不同程度的 buffer、SA、ADC 和 controller；ReRAM-CIM 的 MVM 能效可能只覆盖 array 或包含部分 ADC；DRAM-PIM 的收益可能以 bandwidth utilization、energy per byte 或 host offload 表达。不同路线连“op”的定义都不一致。

合理的比较方式是先统一层级：

```text
cell/device -> macro -> tile -> chip -> system/product
```

再统一精度、workload 和是否包含外围。否则表格越大，误导越强。

## 路线选择的第一性问题

如果目标是片上 edge inference，模型不大且需要低功耗，SRAM-CIM 是最现实的起点，因为它的 CMOS 兼容和验证路径更稳。ReRAM/Flash 可以在固定权重和极低功耗上更激进，但要承担 device 与校准风险。

如果目标是大模型 decode、long context 或 memory-bound HPC，DRAM/HBM/GDDR-PIM 更值得看，因为瓶颈不在片上小 macro，而在大容量 memory-side access。此时讨论 analog CIM 的低能耗 MVM 可能偏离真实瓶颈。

如果目标是研究新型 cell 或 3D 集成，ReRAM/PCM 等路线有更大探索空间，但 maturity label 应保持清楚：paper、test chip、prototype、product 和 volume deployment 是不同阶段。

## 常见误解

常见误解：ReRAM-CIM 理论密度高，所以一定优于 SRAM-CIM。实际上，ReRAM 的 device 和 ADC/校准风险可能让系统收益低于工程稳健的 SRAM-CIM。

常见误解：DRAM-PIM 不是真 CIM，所以不重要。实际上，对 LLM decode 和 memory-bound workload，PIM/NMC 可能比 array-native CIM 更贴近瓶颈。

常见误解：非易失 memory 一定适合 CIM。实际上，非易失只解决待机和权重驻留问题，不解决写入、漂移、读出、精度和软件映射。

## 一句话理解

SRAM-CIM 赢在工程可落地，ReRAM/Flash 赢在阵列原生 MVM 潜力，DRAM-PIM 赢在大容量 memory-side 系统问题；三者不是同一指标上的线性优劣。

## 研究启示

后续研究比较应从 “路线适合什么问题” 出发，而不是追求统一冠军。SRAM-CIM 需要证明 macro-to-chip 收益，ReRAM/Flash 需要证明非理想性和校准可控，DRAM-PIM 需要证明 software/runtime 与 memory command 改造值得。最有价值的横评不是峰值表，而是同一 workload、同一层级、同一精度口径下的端到端拆解。
