# CIM 论文中常见指标的精确定义

上级：[09 研究前沿](README.md)
相关：[论文阅读模板](paper-review-template.md), [性能与能效建模](../05-architecture-and-system/performance-energy-modeling.md), [公司比较矩阵](../08-industry-and-products/company-comparison-matrix.md)

## 这页在回答什么问题

这页回答：CIM/PIM/NMC 论文中的性能、能效、面积和精度指标到底该如何比较。

第一原则：任何数字如果没有说明层级、precision、workload、是否包含外围、是否实测、是否包含 data movement，就不能跨论文比较。

| 指标 | 必须补充的口径 | 常见误读 |
| --- | --- | --- |
| TOPS | MAC 算 1 op 还是 2 ops、INT 几比特、peak 还是 effective | 把 low-bit peak 当真实模型吞吐 |
| GOPS/bit-op | binary/ternary/bit-serial operation 的定义 | 把 bit-level operation 直接等价成 INT8/FP16 MAC |
| MVM/MAC count | matrix-vector size、sparsity、batch、accumulation depth | 把小矩阵满载 MVM 当任意 GEMM 性能 |
| TOPS/W | 是否包含 ADC/DAC/SA/buffer/NoC/DRAM/host | 把 macro energy 当 system energy |
| TFLOPS/W | FP8/FP16/BF16/FP32，是否是等效换算 | 把 mixed precision 等效值当通用浮点性能 |
| energy/MAC | MAC 精度、输入/权重位宽、阵列利用率 | 忽略写权重和 partial sum 搬移 |
| read/write energy | 读一次 array、写一次权重、verify 一次 cell 的边界 | 只看 read energy，忽略 NVM 写入和校验成本 |
| energy/byte moved | memory hierarchy 层级、HBM/DRAM/SRAM/NoC/BUS | 用 op 能耗解释 memory-bound PIM 收益 |
| TOPS/mm2 | 面积是否含外围、controller、buffer、I/O | 只算 array 面积后横比 chip |
| accuracy drop | baseline、dataset、calibration、retraining | 用单模型精度代表所有模型 |
| system speedup | baseline、kernel 范围、host stall、batch size | 把 kernel speedup 当端到端 speedup |

层级定义：

| 层级 | 包含内容 | 使用方式 |
| --- | --- | --- |
| cell/device | 单 cell 或器件状态 | 证明物理机制，不证明系统收益 |
| macro | array、driver、SA/ADC、local accumulation 的一个局部块 | 分析电路效率和非理想性 |
| tile | 多个 macro、local buffer、控制和局部 reduction | 分析映射、reuse、局部调度 |
| chip | 全局 buffer、NoC、I/O、power management、controller | 分析真实 accelerator PPA |
| package | 3DIC、HBM stack、interposer、die-to-die link、thermal | 分析带宽、热和封装良率 |
| card/module | PCIe/M.2/DIMM/HBM stack/board thermal | 分析 host integration 和部署形态 |
| system | host、driver、runtime、真实 workload | 分析客户可感知收益 |

CIM 论文常用 TOPS/W、energy/MAC 和 area efficiency；PIM/NMC 论文更应关注 energy/byte、host offload ratio、bandwidth utilization、stall reduction 和 system speedup。把 PIM 的 system speedup 和 CIM macro TOPS/W 横比，是指标层级错误。

证据来源也必须标注：

| 来源类型 | 可信边界 |
| --- | --- |
| silicon measurement | 最可信，但仍要看是否只测 macro/kernel |
| post-layout simulation | 能反映 layout parasitic，但不等于硅后良率 |
| SPICE/device simulation | 适合看 cell/device 机制，不适合外推系统 |
| architecture simulation | 适合比较 dataflow 和 mapping，但依赖能耗模型 |
| analytical estimate | 适合早期趋势判断，不能支撑强结论 |
| vendor demo/technical blog | 可作为线索，必须区分 marketing claim 和论文证据 |

workload 条件必须至少写清模型族、batch size、sequence length、sparsity、tiling/folding、array utilization 和 fallback 范围。CNN、Transformer encoder、LLM decode、KV cache、MoE gating 对 CIM/PIM/NMC 的瓶颈完全不同。

精度指标要和硬件误差绑定。Analog CIM 需要说明 noise、variation、ADC quantization、retention drift、temperature、write verify 和 compensation；digital CIM 要说明 bit-serial/bit-parallel 精度、popcount、accumulator width、overflow 和 quantization scheme；PIM 要说明 offload kernel 的 numerical format 和 host/GPU fallback。

## 一句话理解

CIM/PIM/NMC 指标的核心不是数字大小，而是数字覆盖了哪一层、哪种精度、哪类 workload 和哪些开销。

## 研究启示

一个好的研究记录必须把指标变成可复现实验口径。对 arch/系统读者来说，最有价值的字段是 layer boundary、included overhead、data movement、effective utilization 和 baseline；没有这些字段，数字越漂亮越容易误导。
