# 建模参数字典：从四元组到可实现参数表

上级：[05 Architecture And System](./README.md)
相关：[性能与能效建模](./performance-energy-modeling.md), [指标术语表](../09-research-frontier/metrics-glossary.md), [Peripheral 开销](../04-circuit-and-macro/peripheral-overhead.md), [Dataflow 映射](./dataflow-mapping-on-cim.md), [NoC: 架构探索循环](../../../../interconnect/NOC/wiki/07-evaluation-methodology/architecture-exploration-loop.md)

## 这页在回答什么问题

全 wiki 每页末尾都把知识折叠成 **Resource / Topology / Interaction / Capability** 四元组，但这些提示散在十几页里，无法直接拿来建模。这页把它们汇总成一张**可实现的参数表**：每个参数给出符号、单位、典型量级、它喂入哪个公式项、以及口径注意事项。它的定位是架构探索工具的数据模型定义，而不是又一篇定性说明。

**关于量级**：表中数值只示意可能的设计点，不是统一样本的统计范围，也不是可直接采用的默认值。建模时必须按目标工艺、具体设计及论文或 silicon 数据校准，并标注证据等级（见[指标术语表](../09-research-frontier/metrics-glossary.md)）。

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

| 参数 | 符号 | 单位 | 示意量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| 阵列行数 | `rows` | — | 64–512 | T_compute、利用率、IR drop | ReRAM 受 IR drop/sneak path 强约束，单阵列常更小 |
| 阵列列数 | `cols` | — | 64–512 | 并行度、外围 amortization | 列数与 ADC 共享比强相关 |
| 阵列每次评估能耗 | `e_array_eval` | fJ/eval | 设计相关 | E_array | 以一次实际评估为单位；依活动行列及尾块门控校准 |
| 单有效 MAC 阵列能耗 | `e_mac_array` | fJ/MAC | 设计相关 | 可选的有效 MAC 能耗模型 | 须定义活动率和统计边界；不能与每次评估能耗重复相加 |
| cell 可表达位数 | `cell_bits` | bit | SRAM 1；ReRAM/Flash/PCM 1–4（多态不稳） | 权重映射、多 cell 拼接 | 多态 cell 的有效位数受 variation/retention 限制 |
| 写权重能耗 | `e_write` | pJ/cell 或 pJ/row | SRAM 极低；NVM 写入显著且非对称 | E_calibration、权重 reload | NVM 写慢写贵，决定权重更新频率上限 |

### ADC / DAC / Sense Amp（analog/mixed-signal 外围）

| 参数 | 符号 | 单位 | 示意量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| ADC 位宽 | `adc_bits` | bit | 3–8 | E_adc、有效精度、T_reduction | 与 array 列数、有效精度耦合 |
| ADC 共享比 | `adc_share` | cols/ADC | 设计相关 | ADC 数量、轮数、吞吐 | 分时改变资源和排队；独立样本的转换总数不因此减少 |
| 单次转换能耗 | `e_adc` | pJ/conv | 架构和工作点相关 | E_adc_dac_sa | 用具体 ADC 校准；不假定统一的位宽缩放律 |
| ADC 转换延迟 / 启动间隔 | `adc_latency`, `adc_ii` | 时间 | 实现相关 | 结果时间、吞吐 | 可流水化时二者可以不同 |
| ADC 面积占比 | `area_adc_frac` | % of macro | 设计相关 | TOPS/mm²、外围口径 | 要给器件、面积边界与来源；见 [Peripheral 开销](../04-circuit-and-macro/peripheral-overhead.md) |
| DAC/输入驱动位宽 | `dac_bits` | bit | 1–4（常 bit-serial 取 1） | T_input_supply、E_dac | 仅当多位输入拆为多个 1-bit 平面时才为 bit-serial；纯二值输入可一次评估 |

### Accumulator / 局部逻辑（digital/mixed-signal）

| 参数 | 符号 | 单位 | 示意量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| 累加器位宽 | `acc_width` | bit | 16–32 | E_local_accum、overflow 安全 | INT8 + 深累加需要更宽，影响面积/布线 |
| bit-serial 评估次数 | `bs_cycles` | evaluations/input | 编码和实现相关 | T_compute | 1 bit/次的实现可按输入位数计算；并行和其他编码需单独定义 |
| 局部逻辑能耗 | `e_logic` | fJ/op | 工艺相关 | E_local_accum | popcount/shift-add 随位宽增长 |

### Buffer / NoC / 全局存储 / Host

| 参数 | 符号 | 单位 | 示意量级 | 喂入 | 口径注意 |
| --- | --- | --- | --- | --- | --- |
| tile buffer 容量 | `buf_cap` | KB | 设计相关 | reload 频率、T_memory | 容量错配导致权重/激活反复 reload |
| buffer 访问能耗 | `e_buf` | pJ/byte | SRAM 量级 | E_buffer | 借用 [RAM wiki](../../../../storage/01-memory-hierarchy/03-performance/memory-bound-vs-compute-bound.md) 口径 |
| NoC 带宽 | `bw_noc` | GB/s | 拓扑相关 | T_reduction、T_memory | partial sum traffic 是 CIM 特有压力 |
| NoC 单跳能耗 | `e_noc` | pJ/byte/hop | 工艺/距离相关 | E_noc | 见 [NoC wiki](../../../../interconnect/NOC/wiki/06-ai-noc-specifics/memory-centric-noc.md) |
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

## 能量子模型

先明确计数边界。一次独立模拟样本转成一个数字结果，计一次 ADC conversion。对实际选择的编码、bit slice、行块、列块、输入和重试进行累加。模拟合并发生在转换前时，样本数按合并后的实际输出计算；同时记录其精度、动态范围和误差代价。

```text
E_adc = N_adc_conv * e_adc
E_dac = N_dac_drive * e_dac
E_array = N_array_eval * e_array_eval
E_total = E_array + E_adc + E_dac + E_sense_if_present
          + E_local_accum + E_buffer + E_noc + E_hbm_dram
          + E_control + E_calibration + E_weight_write + E_background + E_host_sync
```

`E_weight_write` 包含普通重装，以及 NVM 实际 program/verify 重试；`E_background` 为所选驻留与等待窗口内漏电/背景功耗积分。若这些费用已计入 array、buffer 或 calibration，则不再重复相加。

`e_adc` 不包含未列出的 reference、sample/hold 等开销时，需要另计；避免同一电路重复计入。`e_array_eval` 是每次评估的 fJ；`e_mac_array` 是每有效 MAC 的 fJ，两者不是同一单位。可选用 `sum(e_array_eval[i])`，或在所选模型适用时用 `N_valid_mac * e_mac_array`，但不能把两者相加。尾块是否与满块耗能相同取决于活动行列和门控，不能只用有效 MAC 数推断。`N_array_eval` 与每次评估能耗均应按实际位串行及映射确定，不能对已经包含 bit-serial 成本的单位能耗再次乘 `bs_cycles`。

## ADC 样本、转换次数与共享

假设 `S` 个独立样本同时就绪，`A` 个 ADC 中每个在一个启动间隔内可接收一个样本。需要区分可路由关系：

```text
N_adc_conv = S
对固定映射：n[a] = 分配给 ADC a 的样本数；rounds = max_a(n[a])
```

当所有样本可以分配到任意 ADC、且分配均衡时，`rounds = ceil(S / A)`。假设 ADC 的启动间隔相同，没有重试和额外等待，最后一次完成为 `first_start + (rounds - 1) * adc_ii + adc_latency`。这些条件不成立时，应按实际 mux、映射和资源状态逐项调度。

8 个独立样本均衡分配到 2 个 ADC：8 次转换、4 轮；分给 4 个 ADC：仍是 8 次转换、2 轮。反例：4 个有效样本都只能到 ADC 0，即使设备共有 4 个 ADC，也需 4 轮。`S=0` 时没有转换或最后完成事件；`S>0` 且 `A=0` 时不可服务。若 ADC latency 为 3、II 为 1，同一时刻就绪的 8 个样本用 2 个 ADC，从周期 0 启动，到周期 6 最后完成；不能将 4 轮直接乘以 latency。

`adc_share` 的单位是列/ADC；均匀整除的例子里 `A=cols/adc_share`，不整除或不规则连接时应描述实际映射。空列是否转换取决于门控。改变共享度也可能改变 ADC、mux、buffer 和 reference 的能耗，不能据此保证总能耗不变。

[ISAAC](https://users.cs.utah.edu/~rajeev/pubs/isca16-old.pdf)展示了用 sample/hold 保存列输出、共享 ADC 并与后续 array read 交叠的实例。上面的八样本例是独立假设，不是该论文的实测值。模拟器应记录样本产生、ADC 接纳、完成、队列占用与阻塞；ADC latency 和 II 应分别配置。

## 性能子模型与利用率

下面只描述**假设**的单 macro、一个输入向量的 array 评估次数；相邻评估能否重叠由 issue interval 与 latency 决定，ADC、供数和归约可能另行排队：

```text
array_evaluations = ceil(K / rows) * ceil(N / cols) * bs_cycles
if array_evaluations > 0:
    last_array_done = first_issue + (array_evaluations - 1) * array_issue_interval
                      + array_eval_latency
else: no array completion event
```

例如 `K=9, rows=8, N<=cols, bs_cycles=1`，需要两个行块，因此是 2 次评估。行维填充率为 `9/16`；这个指标解释空置容量，但不能再用 `2/(9/16)` 调整评估次数，否则尾块被扣两次。列尾块同理。

报告利用率时，分别定义 `dimension_fill`（尾块）、`weight_active_fraction`（有效权重或门控）、`schedule_busy_fraction`（输入不足或竞争造成的空闲）。只在其损失未被事件调度或 `ceil` 计入时使用相应因子，并说明是否真正影响执行周期或只影响能耗。稀疏权重若没有跳过机制，不能自动减周期。

对独立持续流且各阶段有足够缓冲并可完全重叠时，`max(II_array, II_adc, II_input, II_reduction, II_memory)` 可作为稳态启动间隔的粗略下界。各 II 必须按同一个工作量单位定义，并计入这个工作量所需的所有 array 评估和 ADC 转换。单次请求延迟还要计算启动、依赖、排队、排空和同步；不能无条件取 max。模拟器应沿实际事件依赖与资源日程计算，报告启动间隔、延迟和各阶段阻塞。

## 校准锚点

模型必须能对齐少量已知参考点才可信。建立一张锚点表，每条记录至少含 `level`、`precision`、`included_cost`、`evidence`：

| 锚点 | 数值（示例口径） | level | 用途 |
| --- | --- | --- | --- |
| 16nm 216kb 动态 gain-cell macro | 133.5 TFLOPS/W：MXINT8 输入 × MXINT8 权重 → FP32；91.9 TFLOPS/W：BF16 × BF16 → FP32 | macro / silicon | 对应模式的测量锚点，未包含 system；[作者论文摘要](https://scholars.nthu.edu.tw/esploro/outputs/journalArticle/A-Microscaling-Multi-Mode-Gain-Cell-Computing-in-Memory-Macro/9957829937806774) |

详见 [案例：TSMC 16nm CIM Macro](../09-research-frontier/case-study-tsmc-16nm-cim-macro.md)。新增锚点时务必标注层级与是否含外围/data movement，否则不能用于校准 system 级输出。

## 最小可实现 schema

```text
Resource {
  id; level∈{cell,macro,tile,chip,package,system}; type
  array  { rows, cols, array_issue_interval, array_eval_latency, e_array_eval, e_mac_array, cell_bits, e_write }
  periph { adc_bits, adc_count, adc_share, adc_latency, adc_ii, e_adc,
           area_adc_frac, dac_bits, e_dac, sample_hold_capacity, sample_to_adc_routes }
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

先用本页的一阶函数形式和明确标注为假设的参数把模型跑通，再逐项用目标工艺与论文/silicon 锚点替换常数。早期可折叠器件细节（drift、mismatch → `effective_precision`/`error_model`），但 `level`、`included_cost`、`utilization` 三个字段必须从第一天就强制保留，否则模型规模一大就会重新陷入跨层级误比。
