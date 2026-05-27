# CIM 路线选型决策树

上级：[10 Reference](README.md)
相关：[两条正交主线](../01-overview/two-axes-memory-and-paradigm.md), [Workload Characterization](../07-workloads/workload-characterization-for-cim.md), [产业与产品](../08-industry-and-products/README.md)

## 这页在回答什么问题

这页回答：面对一个 workload、产品目标或研究问题时，应该优先考虑 SRAM-CIM、ReRAM/Flash CIM、DRAM/HBM-PIM 还是 NMC。

第一步：判断目标是不是 cell/array-level compute。

| 判断 | 下一步 |
| --- | --- |
| 需要权重驻留在 array 内，并让 array path 直接做 MAC/bitwise compute | 进入 CIM 路线 |
| 主要想减少 processor 与 HBM/GDDR/DRAM 之间的数据搬移 | 进入 PIM 路线 |
| compute 在 memory 附近但可以独立放在 module/package/base die/host-visible accelerator | 进入 NMC 路线 |
| 只是 SRAM buffer 旁边放 MAC | 不按 CIM 讨论，回到传统 AI accelerator |

第二步：在 CIM 内选 memory technology。

| 目标/约束 | 优先路线 | 代价 |
| --- | --- | --- |
| 标准 CMOS、验证友好、较快产品化、edge AI | SRAM digital/mixed-signal CIM | 容量有限、面积大、大模型需要 folding |
| 极端低功耗、固定权重、高密度 | ReRAM/Flash analog CIM | drift、retention、write-verify、ADC、校准难 |
| 新器件研究、非易失、多值状态 | ReRAM/PCM/MRAM CIM | 工艺集成和可靠性证据不足 |
| 想研究 memory-bound system speedup | 不选 CIM，优先 PIM/NMC | 研究问题从 MAC 能效转到 data movement |

第三步：按 workload 过滤。

| Workload 特征 | 更可能适合 | 不适合的原因 |
| --- | --- | --- |
| CNN/edge vision、权重复用高、模型稳定 | SRAM-CIM、Flash/ReRAM CIM | 如果模型更新频繁，NVM 写入成本上升 |
| LLM decode、GEMV、KV/cache movement、memory bandwidth 压力 | HBM/GDDR-PIM、NMC，部分 CIM 子图 | CIM 容量和动态数据流限制大 |
| Control-heavy、irregular access、低 reuse | NMC 或传统 CPU/GPU/NPU | CIM array 利用率低，fallback 多 |
| Always-on sensor/low-power edge | SRAM-CIM、ReRAM/Flash CIM | 需要精度、温度和长期稳定验证 |

第四步：按研究/产业目标过滤。

| 你的目标 | 阅读/选择建议 |
| --- | --- |
| 写电路论文 | 关注 02/03/04，选具体 cell、array、ADC/SA、non-ideality 问题 |
| 做架构探索 | 关注 05/07/09，建模 macro-to-system、NoC/reduction、data movement |
| 做编译器/runtime | 关注 06/07/09，处理 mapping、quantization、fallback、scheduling |
| 分析公司或产品 | 关注 08/10，先判 taxonomy 和产品层级 |
| 评估新论文 | 先用 09 metrics 和 paper template，再回到对应技术章 |

## 一句话理解

路线选型先问“要减少哪种移动”，再问“能承受哪类工程风险”。

## 维护原则

决策树只给候选路线，不给公司排名或产品推荐。新增分支时必须说明输入条件、排除条件、主要代价和应读章节；如果一个判断需要公司状态或论文证据，应链接到 08 或 09，而不是在本页重复材料。
