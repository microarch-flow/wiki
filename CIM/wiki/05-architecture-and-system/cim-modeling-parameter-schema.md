# 建模参数字典：从四元组到可实现参数表

上级：[05 Architecture And System](./README.md)
相关：[性能与能效建模](./performance-energy-modeling.md), [指标术语表](../09-research-frontier/metrics-glossary.md), [Peripheral 开销](../04-circuit-and-macro/peripheral-overhead.md), [Dataflow 映射](./dataflow-mapping-on-cim.md), [NoC: 架构探索循环](../../../NoC/wiki/07-evaluation-methodology/architecture-exploration-loop.md)

## 这页在回答什么问题

全 wiki 每页末尾都把知识折叠成 **Resource / Topology / Interaction / Capability** 四元组，但这些提示散在十几页里，无法直接拿来建模。这页把它们汇总成一张**可实现的参数表**：每个参数给出符号、单位、典型量级、它喂入哪个公式项、以及口径注意事项。它的定位是架构探索工具的数据模型定义，而不是又一篇定性说明。

**关于"典型范围"**：表中的数量级取自公开 CIM/PIM 文献的常见区间，仅用于设默认值和做 sanity check。任何强结论都必须用**目标工艺节点与具体论文/silicon 数据重新校准**，并标注证据等级（见[指标术语表](../09-research-frontier/metrics-glossary.md)的证据来源表）。

## 四元组总览

| 维度 | 回答什么 | 在模型里的角色 |
| --- | --- | --- |
| Resource | 有哪些计算/存储/转换单元，各自的能力、面积、能耗、热上限 | 节点属性 |
| Topology | 这些单元怎么连接、归约在哪发生 | 图的边与层级 |
| Interaction | tensor 怎么搬、workload phase 怎么推进、何时同步/校准 | 在图上跑的事件流 |
| Capability | 支持哪些 op、精度、误差模型、calibration 策略 | 约束与可行性判定 |

下面四节是参数清单，第五、六节给出把这些参数组合起来的能量/性能函数形式，第七节给校准锚点，第八节给一个紧凑的可实现 schema。

## Resource 参数

`level` 字段对每个 Resource 都必填（cell / macro / tile / chip / package / system），用于防止跨层级误比。

### Array（cell 阵列）

| 参数 | 符号 | 单位 | 典型量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| 阵列行数 | `rows` | — | 64–512 | T_compute、利用率、IR drop | ReRAM 受 IR drop/sneak path 强约束，单阵列常更小 |
| 阵列列数 | `cols` | — | 64–512 | 并行度、外围 amortization | 列数与 ADC 共享比强相关 |
| 单 MAC 阵列能耗 | `e_mac_array` | fJ/MAC | analog 亚-fJ~数 fJ；digital 数 fJ~数十 fJ | E_array_compute | 仅 array 内，不含外围；analog 低值常忽略 ADC |
| cell 可表达位数 | `cell_bits` | bit | SRAM 1；ReRAM/Flash/PCM 1–4（多态不稳） | 权重映射、多 cell 拼接 | 多态 cell 的有效位数受 variation/retention 限制 |
| 写权重能耗 | `e_write` | pJ/cell 或 pJ/row | SRAM 极低；NVM 写入显著且非对称 | E_calibration、权重 reload | NVM 写慢写贵，决定权重更新频率上限 |

### ADC / DAC / Sense Amp（analog/mixed-signal 外围）

| 参数 | 符号 | 单位 | 典型量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| ADC 位宽 | `adc_bits` | bit | 3–8 | E_adc、有效精度、T_reduction | 与 array 列数、有效精度耦合 |
| ADC 共享比 | `adc_share` | cols/ADC | 1–64 | 吞吐、面积、E_adc 摊销 | 共享越多越省面积，但 throughput 下降 |
| 单次转换能耗 | `e_adc` | pJ/conv | 与 2^bits 近似成比例 | E_adc_dac_sa | 高位 ADC 能耗/面积非线性上升 |
| ADC 面积占比 | `area_adc_frac` | % of macro | mixed-signal 中常达数十% | TOPS/mm²、外围口径 | 见 [Peripheral 开销](../04-circuit-and-macro/peripheral-overhead.md) |
| DAC/输入驱动位宽 | `dac_bits` | bit | 1–4（常 bit-serial 取 1） | T_input_supply、E_dac | 1bit 输入即 bit-serial 展开 |

### Accumulator / 局部逻辑（digital/mixed-signal）

| 参数 | 符号 | 单位 | 典型量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| 累加器位宽 | `acc_width` | bit | 16–32 | E_local_accum、overflow 安全 | INT8 + 深累加需要更宽，影响面积/布线 |
| bit-serial 周期数 | `bs_cycles` | cycle/MAC | =输入位宽（1–8） | T_compute | digital CIM 支持 INT8 时周期线性上升 |
| 局部逻辑能耗 | `e_logic` | fJ/op | 工艺相关 | E_local_accum | popcount/shift-add 随位宽增长 |

### Buffer / NoC / 全局存储 / Host

| 参数 | 符号 | 单位 | 典型量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| tile buffer 容量 | `buf_cap` | KB | 设计相关 | reload 频率、T_memory | 容量错配导致权重/激活反复 reload |
| buffer 访问能耗 | `e_buf` | pJ/byte | SRAM 量级 | E_buffer | 借用 [RAM wiki](../../../RAM/wiki/09-ai-chip-memory-architecture/memory-bound-vs-compute-bound.md) 口径 |
| NoC 带宽 | `bw_noc` | GB/s | 拓扑相关 | T_reduction、T_memory | partial sum traffic 是 CIM 特有压力 |
| NoC 单跳能耗 | `e_noc` | pJ/byte/hop | 工艺/距离相关 | E_noc | 见 [NoC wiki](../../../NoC/wiki/06-ai-noc-specifics/memory-centric-noc.md) |
| HBM/DRAM 带宽 | `bw_mem` | GB/s | HBM 数百~TB/s | T_memory | memory-bound workload 的主导项 |
| DRAM 访问能耗 | `e_dram` | pJ/byte | 远高于片上 SRAM | E_hbm_dram | energy/byte 是 PIM/NMC 收益的核心口径 |
| host 偏移延迟 | `t_host` | µs | 接口相关 | T_host、T_sync | PCIe attached vs SoC 内嵌差异巨大 |

## Topology 参数

| 参数 | 含义 | 喂入 |
| --- | --- | --- |
| `macros_per_tile` | 每 tile 的 macro 数 | tile 级并行度、buffer 压力 |
| `tiles_per_chip` | 每 chip 的 tile 数 | chip 峰值、NoC 规模 |
| `reduction_level` | partial sum 在何处归约（array / macro / tile / NoC） | T_reduction、E_noc 分布 |
| `noc_topology` | mesh / tree / bus 等 | 跳数、拥塞、归约代价 |
| `mem_attach` | global buffer / HBM / host 的挂接方式 | T_memory、T_host |

## Interaction 参数

| 参数 | 含义 | 喂入 |
| --- | --- | --- |
| `weight_reload_rate` | 权重重写频率 | E_write、NVM 路线的可行性判定 |
| `activation_traffic` | 每 phase 输入激活字节量 | T_input_supply、E_buffer |
| `psum_traffic` | partial sum 搬运字节量 | T_reduction、E_noc |
| `workload_phase` | prefill / decode / conv / attention 等 | 决定瓶颈项与利用率 |
| `calib_interval` | 校准触发间隔 | T_calibration、E_calibration |
| `sync_points` | host/runtime 同步点 | T_sync、T_host |

## Capability 参数

| 参数 | 含义 | 喂入 |
| --- | --- | --- |
| `supported_ops` | MVM / GEMM / conv / 是否支持非 MAC | mapping 可行性、fallback 判定 |
| `nominal_precision` | 标称位宽（INT4/INT8/FP8…） | 精度约束 |
| `effective_precision` | 含 ADC/噪声后的有效位数 | accuracy loss、能耗-精度绑定 |
| `error_model` | noise/variation/drift/温漂 的折叠参数 | accuracy loss、calibration 需求 |
| `fallback_path` | 不支持的算子退回到哪（host/GPU/NPU） | T_host、端到端 speedup |

device drift、mismatch 等物理细节在早期探索中**折叠成** `effective_precision`、`error_model`、`e_*` 与 `t_*` 几个参数即可，不必建到器件级。

## 能量子模型：把加法结构展开成函数形式

[性能与能效建模](./performance-energy-modeling.md) 给出 `E_total = E_array + E_adc + E_local_accum + E_buffer + E_noc + E_hbm_dram + E_control + E_calibration + E_host_sync`。本页把主要项展开为可计算式（一阶近似，常数需校准）：

```text
E_array_compute = N_mac * e_mac_array * bs_cycles
E_adc_dac_sa    = N_adc_conv * e_adc + N_dac_drive * e_dac
                  其中 N_adc_conv ≈ (N_mac / (rows * adc_share)) * bs_cycles
E_local_accum   = N_acc_op * e_logic
E_buffer        = bytes_buf * e_buf
E_noc           = psum_traffic * e_noc * avg_hops
E_hbm_dram      = bytes_dram * e_dram
E_calibration   = (runtime / calib_interval) * e_calib_event
```

要点：analog 路线若只报 `E_array_compute` 而省略 `E_adc_dac_sa`，能耗会被严重低估；`bs_cycles` 让 digital CIM 的 INT8 能耗随输入位宽线性放大；`e_dram` 通常比片上能耗高一到两个量级，是 memory-bound workload 的主导项。

## 性能子模型与利用率

```text
T_total = max(T_compute, T_input_supply, T_reduction, T_memory, T_host)
          + T_sync + T_calibration

T_compute = cycles * t_cycle
cycles    = ceil(K / rows) * ceil(N / cols) * bs_cycles / util_array
T_memory  = bytes_dram / bw_mem
T_reduction = psum_traffic / bw_noc
```

**利用率 `util_array`** 是架构探索的核心变量，单独建模：

```text
util_array = (有效 MAC) / (峰值 MAC)
           ≈ dim_fill * weight_fill * (1 - padding_loss)
```

- `dim_fill`：workload 维度对 `rows`/`cols` 的整除程度（`K mod rows`、`N mod cols` 不为 0 时产生 padding 损失）。
- `weight_fill`：weight-stationary 下阵列被有效权重填满的比例；小算子或 depthwise conv 常很低。
- `padding_loss`：tiling/folding 引入的空算损失。

`T_total` 取 max 而非求和，体现 roofline：若 workload 卡在 `T_memory` 或 `T_host`，再提高 `rows*cols` 峰值并行度对 `T_total` 无贡献——这正是工具要替用户看见的结论。

## 校准锚点

模型必须能对齐少量已知参考点才可信。建立一张锚点表，每条记录至少含 `level`、`precision`、`included_cost`、`evidence`：

| 锚点 | 数值（示例口径） | level | 用途 |
| --- | --- | --- | --- |
| TSMC 16nm gain-cell macro | 188.4 TOPS/W、133.5 TFLOPS/W、216kb | macro / silicon | 校准 macro 峰值能效上界，注意是 peak、未含 system | 

详见 [案例：TSMC 16nm CIM Macro](../09-research-frontier/case-study-tsmc-16nm-cim-macro.md)。新增锚点时务必标注层级与是否含外围/data movement，否则不能用于校准 system 级输出。

## 最小可实现 schema

```text
Resource {
  id; level∈{cell,macro,tile,chip,package,system}; type
  array  { rows, cols, e_mac_array, cell_bits, e_write }
  periph { adc_bits, adc_share, e_adc, area_adc_frac, dac_bits, e_dac }
  digital{ acc_width, bs_cycles, e_logic }
  mem    { buf_cap, e_buf }
  link   { bw_noc, e_noc, bw_mem, e_dram, t_host }
  limits { area_mm2, power_w, thermal_cap }
}
Topology { macros_per_tile, tiles_per_chip, reduction_level, noc_topology, mem_attach }
Interaction { weight_reload_rate, activation_traffic, psum_traffic,
              workload_phase, calib_interval, sync_points }
Capability { supported_ops, nominal_precision, effective_precision,
             error_model, fallback_path }
Output(每条结果必带) { level, included_cost, utilization,
             throughput, latency, energy_per_op, energy_per_byte, precision_loss, evidence }
```

`Output` 的字段不可省略：缺 `level`/`included_cost`/`utilization` 的结果无法跨配置比较，工具应在生成结果时强制填写。

## 一句话理解

把四元组落成带单位、范围、公式归属和证据等级的参数表，再给能量/性能/利用率子模型以可计算的函数形式——这样架构探索工具输出的才是可比较、可校准的结论，而不是又一个孤立的 TOPS/W 数字。

## 建模启示

先用本页的一阶函数形式和默认范围把模型跑通，再逐项用目标工艺与论文/silicon 锚点替换常数。早期可折叠器件细节（drift、mismatch → `effective_precision`/`error_model`），但 `level`、`included_cost`、`utilization` 三个字段必须从第一天就强制保留，否则模型规模一大就会重新陷入跨层级误比。
