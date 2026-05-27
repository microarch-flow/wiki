# CIM 研究的 Open Problems

上级：[09 研究前沿](README.md)
相关：[近期研究主题](recent-progress-themes.md), [可靠性与误差容忍](../05-architecture-and-system/reliability-and-error-tolerance.md), [软件栈](../06-software-stack/README.md)

## 这页在回答什么问题

这页回答：CIM/PIM/NMC 研究里哪些问题仍然没有被真正解决，哪些只是实现优化。

| 问题 | 主要影响路线 | 为什么仍然难 |
| --- | --- | --- |
| Analog non-ideality 到模型精度的闭环 | ReRAM/Flash/PCM/SRAM analog CIM | 噪声、mismatch、retention、temperature、ADC 量化会随模型和时间变化 |
| Peripheral overhead | analog/mixed-signal CIM | ADC/DAC/SA、driver、calibration 往往吞掉 array 节省的能耗和面积 |
| 容量与数据搬移 | SRAM digital CIM | SRAM 容量有限，大模型需要 folding、tiling、off-chip transfer |
| 写入与更新成本 | ReRAM/Flash/PCM CIM | 固定权重推理友好，频繁更新和 personalization 成本高 |
| Cross-layer co-design | 全部 CIM | 电路、量化、mapping、training 和 runtime 必须同时设计 |
| PIM command/runtime | DRAM/HBM/GDDR-PIM | memory controller、ISA/API、kernel library 和 host synchronization 缺少统一抽象 |
| Benchmark 真实性 | 全部 | 小模型、满载阵列、理想 mapping 容易高估收益 |
| Testing/yield modeling | CIM/PIM | 研究论文很少完整覆盖 DFT、坏点、PVT、长期漂移和量产测试时间 |

一个问题是否属于 open problem，要看它是否跨层。比如“把 ADC 从 6 bit 降到 4 bit”本身是电路优化；如果它牵动模型精度、training、calibration、array size、throughput 和 software fallback，就变成系统级 open problem。

为了避免把工程优化都写成 research frontier，可以用下面的区分：

| 单点工程优化 | 变成真 open problem 的条件 |
| --- | --- |
| 降低某个 ADC 的能耗 | ADC 精度、面积、throughput、模型精度和 calibration 无法同时满足 |
| 调整 SRAM-CIM array size | array size 牵动 folding、NoC/reduction、buffer 容量和外部 DRAM 访问 |
| 改一个 ReRAM write-verify 策略 | write energy、retention、endurance、推理精度和部署寿命互相冲突 |
| 增加一个 PIM 指令 | host command model、memory consistency、runtime、kernel library 和 controller 复杂度无法收敛 |
| 优化一个 benchmark kernel | 真实模型图需要 fallback、同步、数据重排，kernel speedup 无法转化为 system speedup |

对 analog CIM，最大的研究缺口是可预测性。论文可以通过 calibration 或 retraining 恢复一个模型的精度，但真实系统需要在温度、老化、批次差异、输入分布变化和长时间部署下维持可靠性。研究还需要更好的 error model，把 device/macro 非理想性传递到 layer-level 和 application-level accuracy。

对 digital SRAM-CIM，最大的研究缺口是系统收益。digital route 比 analog 更可控，但 SRAM 容量小，片上 NoC/reduction 和外部 DRAM 访问可能吃掉 macro 能效。需要更多从 macro 到 chip/system 的 mapping study，而不是只报告单宏 peak。

对 ReRAM/PCM/Flash CIM，最大的研究缺口是长期可用性。多值状态、高密度和非易失性很诱人，但写入 verify、retention drift、endurance、temperature compensation 和 fault tolerance 必须和 workload 生命周期绑定。

对 PIM/NMC，最大的研究缺口是软件抽象。HBM/GDDR/DIMM 近侧计算如果没有稳定 command model、runtime、compiler pass 和 library，就只能服务少量手写 kernel。研究需要回答什么样的 memory-side primitive 足够通用，同时又不会把 memory 产品复杂度推高到无法接受。

## 一句话理解

CIM/PIM/NMC 的 open problems 大多不是单点电路问题，而是跨 device、macro、architecture、software 和 workload 的闭环问题。

## 研究启示

下一阶段有价值的研究会把“漂亮 macro”放进更真实的系统约束里：包含外围、数据搬移、编译映射、错误恢复、测试和 workload 分布。对架构探索来说，真正值得建模的是这些跨层状态变量，而不是只把 TOPS/W 当常数填进表格。
