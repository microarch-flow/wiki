# 不同 CIM/PIM 路线的软件栈差异

上级：[06 Software Stack](./README.md)
相关：[CIM/PIM/NMC Taxonomy](../01-overview/cim-pim-nmc-taxonomy.md), [RAM: DRAM Commands](../../../RAM/wiki/05-dram-protocol-families/commands-act-rd-wr-pre.md), [NoC: Memory-Centric NoC](../../../NoC/wiki/06-ai-noc-specifics/memory-centric-noc.md), [BUS: DMA Interface](../../../BUS/wiki/04-microarchitecture-integration/axi-dma-system-interface.md), [FAB: Test Methodology](../../../FAB/wiki/05-final-test-and-reliability/final-test-methodology.md)

## 这页在回答什么问题

为什么不能说“CIM 软件栈”只有一种？SRAM-CIM、ReRAM/Flash CIM、DRAM/HBM/GDDR-PIM 和 NMC 的硬件边界不同，compiler/runtime 要表达的能力、限制和 host 接口也不同。

## 路线对比

| 路线 | compiler maturity | IR/mapping burden | runtime/host burden | 最大风险 |
| --- | --- | --- | --- | --- |
| SRAM digital CIM | 较接近数字 NPU | bit-serial/popcount、array residency | buffer/NoC scheduling | 和普通 SRAM + MAC 的收益边界 |
| SRAM mixed-signal CIM | 中等 | scale、SA/ADC、local correction | calibration metadata | PVT 与校准状态进入 runtime |
| ReRAM/Flash analog CIM | 重 | weight programming、variation-aware mapping | write/verify、drift、ADC、QAT | 模型适配和硅后差异 |
| PCM/MRAM CIM | 研究性强 | 特定 read/sense-path 或 resistance-state | health/remap 复杂 | 成熟度和场景很窄 |
| DRAM/HBM/GDDR-PIM | 依赖 memory vendor | memory command、bank/channel offload | host runtime、result return | 生态、controller、算子能力 |
| NMC | 接近 accelerator SDK | data placement、DMA、package bandwidth | coherency/offload latency | 和 GPU/NPU/CPU 协同成本 |

## 三条 Paradigm 的软件成熟度

Digital CIM 最接近现有 compiler/runtime。它仍要解决 array shape、bit-plane 和 residency，但 deterministic behavior、数字验证和标准量化让工具链风险较低。

Analog CIM 的软件栈更重。它需要硬件 profile、calibration、noise-aware training、variation-aware mapping 和 silicon-specific validation。没有这些，array-native MVM 很难稳定交付。

Mixed-signal CIM 介于两者之间。它希望保留 analog 局部能效，同时用数字 correction 降低风险；软件栈必须把边界、metadata 和 correction 变成一等对象。

## CIM/PIM/NMC 边界

Samsung HBM-PIM、SK hynix AiM/AiMX 这类 DRAM/HBM/GDDR memory-side processing 属于 PIM，不是 CIM compiler 后端。它们的软件重点是 memory-side command、controller/runtime、bank/channel scheduling 和 host offload。UPMEM、HBM base die、interposer 或 package-side compute 属于 NMC 对照，软件上更像靠近 memory 的 accelerator。

SRAM buffer + MAC、memory 旁边 ALU、普通 HBM-adjacent accelerator 不算 CIM；只有 cell、bitline、wordline、sense path 或紧邻 array path 参与计算，CIM software 才需要处理本章的 array mapping、encoding 和 calibration。

## 一句话理解

软件栈差异来自硬件边界：CIM 要编译到 array，PIM 要 offload 到 memory die/bank，NMC 要调度靠近 memory 的 accelerator。

## 工具链启示

工具链应先按 taxonomy 选择后端：CIM 后端关注 array/tile mapping、encoding、calibration；PIM 后端关注 memory command 和 bank/channel runtime；NMC 后端关注 DMA、package bandwidth 和 accelerator API。软件栈成熟度要看 mapping automation、quantization burden、runtime burden、fallback cost、host integration 和 debug/test difficulty；它比单个 macro TOPS/W 更接近产品化门槛。
