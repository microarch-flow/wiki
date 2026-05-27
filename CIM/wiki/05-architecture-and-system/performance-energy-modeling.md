# 性能与能效建模：从 Macro 到 System 的指标推导

上级：[05 Architecture And System](./README.md)
相关：[Metrics Glossary](../09-research-frontier/metrics-glossary.md), [RAM: Memory Bound vs Compute Bound](../../../RAM/wiki/09-ai-chip-memory-architecture/memory-bound-vs-compute-bound.md), [NoC: Architecture Exploration Loop](../../../NoC/wiki/07-evaluation-methodology/architecture-exploration-loop.md)

## 这页在回答什么问题

如何把 macro 的能效、面积和吞吐转换成系统级判断？必须先把层级、精度、workload、利用率和是否包含外围统一，否则 TOPS/W、TOPS/mm²、latency 和 energy per task 之间没有可比性。

## 最小能耗模型

```text
E_total =
  E_array_compute
  + E_adc_dac_sa
  + E_local_accum
  + E_buffer
  + E_noc
  + E_hbm_dram
  + E_control
  + E_calibration
  + E_host_sync
```

这个公式不是追求晶体管级精确，而是强迫分析者把隐藏成本显式列出。ReRAM analog CIM 若只给 `E_array_compute`，不能和 SRAM digital CIM 的 full macro energy 比；DRAM/HBM/GDDR-PIM 若给 system offload energy，也不能和 CIM macro TOPS/W 横比。HBM base die、interposer 或 package-side compute 属于 NMC，应以 die-to-die/package bandwidth、energy per byte、host offload latency 和 accelerator utilization 建模。

## 最小性能模型

```text
T_total = max(T_compute, T_input_supply, T_reduction, T_memory, T_host) + T_sync + T_calibration
```

CIM 的峰值并行度只影响 `T_compute`。如果 activation supply、partial sum reduction、HBM access 或 host synchronization 成为瓶颈，继续提高 macro peak TOPS 没有系统价值。

## 三条 Paradigm 的建模差异

Analog CIM 必须建模 ADC bit、ADC sharing、effective precision、calibration interval 和 accuracy loss。它的 peak energy 需要绑定误差模型，否则低能耗可能来自过低有效精度。

Digital CIM 必须建模 bit-serial cycles、accumulator width、local logic energy、routing 和 utilization。它的 precision 更确定，但 INT8/FP8 扩展会让周期和 buffer 成本上升。

Mixed-signal CIM 必须建模 analog array energy 与 digital correction 的边界。需要把 scale、metadata、calibration、tile-level accumulation 和 model retraining cost 放入同一口径。

## Roofline 风格判断

可以把 CIM 系统放在 compute roofline 与 data-movement roofline 之间。若 workload 卡在 HBM/DRAM bandwidth 或 host offload，array compute peak 不是主要变量；若 workload 卡在 local reduction 或 ADC throughput，优化 NoC 或 ADC sharing 比加 macro 数更有效。

## 指标口径表

| 字段 | 必须说明 |
| --- | --- |
| level | macro / tile / chip / system |
| precision | nominal bit、effective bit、model accuracy |
| included cost | ADC/DAC/SA、buffer、NoC、DRAM、host |
| workload | MVM/GEMM/CNN/Transformer 子图 |
| utilization | array、tile、NoC、memory 的有效利用率 |
| evidence | ideal sim、post-layout、silicon measurement |

## 一句话理解

CIM 建模的核心不是一个 TOPS/W 数字，而是把 array、外围、buffer、NoC、memory、host 和误差放进同一层级口径。

## 建模启示

早期探索可用参数化模型：Resource 记录 macro/tile/memory 能力、area 和 thermal cap，Topology 记录连接和归约，Interaction 记录 tensor movement、workload phase 与同步，Capability 记录 op、precision、error 与 calibration。device drift 等细节可折叠成 error/energy/latency 参数，但模型必须保留 utilization、throughput、latency、energy per op、energy per byte、precision loss、level 与 included-cost 字段，防止跨层级误比。
