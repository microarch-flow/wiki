# Parameter Reference

上级：[08 Simulator Construction](./README.md)

相关：[Core Data Structures](./core-data-structures.md)、[Credit Based Flow Control](../02-router-microarchitecture/credit-based-flow-control.md)、[Allocator Design VC Switch](../02-router-microarchitecture/allocator-design-vc-switch.md)、[Topology Design Metrics](../03-topology/topology-design-metrics.md)、[NOC Meets Memory System](../05-system-integration/noc-meets-memory-system.md)

## 这页在回答什么问题

这页回答：第一版 NoC simulator 一共有多少个**可调参数**、每个参数的**默认值 / 范围 / 单位**、出自哪个**公式或建模决策**、以及对照已知工业/学术工具（gem5-Garnet、BookSim、OpenSoC）的取值如何。

读完应能：
- 一眼看到任一参数的"建议起点"
- 直接对照已有工具的默认值，发现自己的配置是否偏离合理区间
- 找到该参数被消费的所有页面，做 sweep 时不漏地方

## 使用规则

| 列 | 含义 |
|----|------|
| 参数 | 在 simulator 代码 / 配置 / 文档里的规范名 |
| 单位 | bytes / cycle / count / ratio / …… |
| 默认 | 建议起点（来源标注）|
| 范围 | 合理 sweep 区间 |
| 出自 | 哪个公式或决策定义了它 |
| 消费者 | 哪个数据结构 / 函数 / 公式读它 |
| 工业参考 | gem5-Garnet / BookSim / NVIDIA NVSwitch 公开值 |

## 1. 拓扑参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `topology_type` | enum | `MESH_2D` | mesh/torus/ring/cmesh/fat_tree/dragonfly | [topology-design-metrics](../03-topology/topology-design-metrics.md) | `TopologyClosedForm`、placement | Garnet 默认 MESH |
| `num_nodes` `N` | count | 16 | 4..1024 | 同上 | 全部 | - |
| `mesh_k` | count | `sqrt(N)` | 2..32 | mesh/torus 公式 | diameter, bisection | Garnet 8 |
| `fat_tree_arity` `k` | count | 4 | 2..16 | fat-tree 公式 | radix, diameter | - |
| `fat_tree_levels` `L` | count | `log_k(N)` | 2..5 | 同上 | 同上 | - |
| `dragonfly_a / g / p` | count | 4/8/4 | - | dragonfly 公式 | radix, global link | Cray Cascade a=16 |
| `concentration` `c` | count | 1 | 1..8 | cmesh 公式 | radix, hop | - |
| `tile_pitch_um` | µm | 500 | 100..2000 | 物理约束 | wire span → forward_link_latency | TSMC N5 大 IP 约 500 |

## 2. 链路参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `link_width_bits` | bits | 128 | 64..512 | 设计选择 | bandwidth, serialization | Garnet 128, NVLink 256 |
| `phit_width_bits` | bits | 128 | 64..256 | 同上 | serialization_cycles | Garnet 128 |
| `forward_link_latency` | cycle | 1 | 1..6 | [R 公式: forward](../02-router-microarchitecture/credit-based-flow-control.md#forward_link_latency) | `Link.forward_pipe`、R | Garnet 1, BookSim 1 |
| `return_link_latency` | cycle | 1 | 1..6 | [R 公式: return](../02-router-microarchitecture/credit-based-flow-control.md#credit_return_latency) | `Link.return_pipe`、R | Garnet 1 |
| `link_frequency_GHz` | GHz | 1.0 | 0.5..2.0 | 工艺 / allocator 选择 | bandwidth, contention | Garnet 1.0 |
| `link_bandwidth_GBps` | GB/s | 16 | 4..128 | `width · freq / 8` | `Stats.per_link_bytes` | NVLink 50, HBM 51.2/ch |
| `signal_um_per_cycle` | µm | 2000 | 500..4000 | 工艺常数 | wire_propagation_cycles | 14nm 约 2000 |

## 3. Router 参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `num_input_ports` `P` | count | 5 | 3..16 | topology radix | `Router.input_vcs`、allocator | Garnet 5 (mesh) |
| `num_output_ports` | count | =`P` | - | 同上 | 同上 | - |
| `num_vcs` `V` | count | 4 | 1..16 | 路由 / class 需求 | `InputVcState`、allocator | Garnet 4, BookSim 8 |
| `buffer_depth_per_vc` | flits | 8 | 2..32 | [R 公式推导](../02-router-microarchitecture/credit-based-flow-control.md#推导使链路饱和的最小-buffer_depth) | `InputVcState.queue` | Garnet 4, BookSim 8 |
| `ejection_depth` | flits | 16 | 4..64 | `max(R, burst+2)` | `Router.local_ejection_queue` | Garnet 4 |
| `t_BW` | cycle | 1 | 1 | 流水线固定 | R, pipeline_register | Garnet 1 |
| `t_RC` | cycle | 1 | 0..2 | 同上 | R | Garnet 1 |
| `t_VA_pipeline` | cycle | 1 | 1..3 | allocator 选择 | R | Garnet 1 |
| `t_SA_pipeline` | cycle | 1 | 1..3 | 同上 | R | Garnet 1 |
| `t_ST` | cycle | 1 | 1..2 | 流水线固定 | R | Garnet 1 |
| `router_total_pipeline_cycles` | cycle | 5 | 3..8 | Σ above | R 公式整体 | Garnet 5 |

## 4. Allocator 参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `allocator_type` | enum | `SEPARABLE` | separable/iSLIP/wavefront | [allocator 三方案对比](../02-router-microarchitecture/allocator-design-vc-switch.md#三者对比表) | VA、SA | Garnet separable |
| `iSLIP_iterations` | count | 2 | 1..4 | iSLIP 模型 | t_pipe, η | Garnet 1 |
| `eta_VA` | ratio | 0.70 | 0.5..0.97 | 同上 | E[VA_contention] | derived |
| `eta_SA` | ratio | 0.70 | 0.5..0.97 | 同上 | E[SA_contention] | derived |
| `priority_rotation` | enum | `ROUND_ROBIN` | RR/oldest/class | 公平性 | allocator 内部 | - |
| `K_VA` `K_SA` | count | 2 | 1..P | 流量 contention | E[*_contention] | 由 trace 派生 |

`eta_*` 是模型层效率参数，由 `allocator_type + iSLIP_iterations` 派生，**不应直接 sweep**。

## 5. Endpoint / NI 参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `injection_depth` | packets | 16 | 4..256 | 注入侧 buffer | `Endpoint.injection_queue` | Garnet 16 |
| `injection_vcs` | count | =`V` | - | endpoint↔router 配对 | `Endpoint.injection_credit` | - |
| `consumer_rate_flits_per_cycle` | flits/c | 1.0 | 0.25..4.0 | [SRAM 反推公式](../05-system-integration/noc-meets-memory-system.md#从-sram-反推-ejection-最大稳态吞吐) | ejection drain | Garnet ∞ (默认无限) |
| `outstanding_request_max` | count | 32 | 8..256 | DMA 深度 | injection_rate_cap | NVIDIA 64+ |
| `dma_burst_flits` | flits | 8 | 2..32 | DMA 设计 | injection 节奏 | - |

## 6. Workload / Traffic 参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `traffic_pattern` | enum | `uniform_random` | uniform/hotspot/transpose/trace | screening | trace generator | BookSim 标配集 |
| `injection_rate` | flits/c/node | 0.1 | 0.01..1.0 | latency-throughput curve | injection scheduler | BookSim sweep |
| `packet_size_flits` | flits | 5 | 1..32 | workload | `Packet.num_flits` | Garnet 5 |
| `flit_size_bytes` | bytes | 16 | 4..64 | `link_width_bits / 8` | bandwidth | Garnet 16 |
| `traffic_classes` | enum set | 5 类 | - | [simulator-design-spec](./simulator-design-spec.md) | class-aware VC 分配 | - |
| `workload_phase_boundaries` | bool | `false` | - | trace 选项 | barrier 模拟 | - |

## 7. Memory / HBM 参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `hbm_channels` | count | 8 | 4..32 | HBM 选择 | hbm_service_bw | HBM2e 8, HBM3 16 |
| `hbm_channel_bw_GBps` | GB/s | 51.2 | 32..103 | HBM 物理 | hbm_service_bw | HBM3 51.2~102 |
| `hbm_round_trip_ns` | ns | 100 | 60..150 | HBM 时序 | injection_rate_cap | HBM3 80~120 |
| `hbm_scheduling_efficiency` | ratio | 0.75 | 0.5..0.9 | controller 设计 | effective bw | 0.7~0.85 公开数据 |
| `hbm_burst_size_bytes` | bytes | 256 | 64..512 | HBM 协议 | ejection_depth 下界 | HBM3 256 |
| `sram_num_banks` | count | 8 | 1..64 | tile SRAM 设计 | bank_port_bw | 典型 8~32 |
| `sram_port_per_bank` | count | 1 | 1..4 | 同上 | 同上 | - |
| `sram_bank_width_bytes` | bytes | 32 | 8..128 | 同上 | 同上 | - |
| `sram_conflict_factor` | ratio | 1.0 | 1.0..8.0 | [access pattern 表](../05-system-integration/noc-meets-memory-system.md#bank-conflict-参数化) | effective bw | 由 workload 派生 |

## 8. 模拟控制参数

| 参数 | 单位 | 默认 | 范围 | 出自 | 消费者 | 工业参考 |
|------|------|------|------|------|--------|---------|
| `warmup_cycles` | cycle | 10000 | 1000..100000 | 稳态检测 | stats 起点 | BookSim 10k |
| `measurement_cycles` | cycle | 100000 | 10000..1M | 同上 | stats 终点 | BookSim 100k |
| `random_seed` | int | 0 | 任意 | 可复现 | trace generator | - |
| `simulation_mode` | enum | `event` | analytical/event/cycle | [layers](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md) | core loop | - |
| `verification_mode` | bool | `true` (dev) | true/false | [verification](./verification-and-calibration.md) | 不变量 assert | - |
| `trace_output_level` | enum | `summary` | none/summary/flit/all | 调试 | logging | - |
| `confidence_interval` | ratio | 0.95 | 0.9..0.99 | 统计 | result reporting | BookSim 95% |

## 与工业工具的关键对照

抓三组容易踩坑的对照点：

### Garnet (gem5)

- 默认 `buffer_depth = 4`：在 `R ≈ 5~8` 的典型流水线下是**偏小**的，会高估 NO_CREDIT stall。我们的默认 `8` 更接近 BookSim 取值
- 默认 `t_pipe = 5`：与我们一致
- Garnet 没有 `consumer_rate` 概念（ejection 视作无限快）：移植 Garnet 配置时务必显式设置 `consumer_rate_flits_per_cycle` 否则会过度乐观

### BookSim

- 默认 `vc=8, buffer=8`：BookSim 是 cycle-accurate flit 级，参数取得更激进。简单复制到第一版会让 router 面积膨胀
- BookSim 不建模 HBM：所有"memory port"都是 perfect sink。AI workload 必须叠加我们的 HBMModel

### NVIDIA NVSwitch / DGX

- `link_bandwidth ≈ 50 GB/s/link`、`hbm_channel_bw ≈ 100 GB/s`：与我们默认匹配
- `dragonfly_a/g/p` 在 NVSwitch 上对应 NVLink fabric topology
- 公开材料显示其 `OS_max > 64`，所以 NVIDIA 工作负载下 HBM injection 通常**不**是瓶颈

## sweep 时的参数依赖

不是所有参数都能独立调。下面是必须**联动 sweep** 的组合，否则结论会失真：

| 联动组 | 原因 |
|--------|------|
| `(allocator_type, link_frequency_GHz)` | iSLIP/wavefront 频率上限不同，单维 sweep 错误推荐复杂 allocator |
| `(buffer_depth_per_vc, R)` | R 由其他参数派生；buffer 必须 ≥ R |
| `(topology_type, num_nodes, mesh_k)` | mesh_k = sqrt(N)，N 变 k 必须变 |
| `(ejection_depth, hbm_burst_size_bytes)` | burst 超过 ejection 容量会触发瞬时 stall |
| `(injection_rate, traffic_pattern)` | 不同 pattern 的饱和点不同，scan 范围要重新校准 |
| `(consumer_rate, sram_conflict_factor)` | 后者直接决定前者 |
| `(num_vcs, num_traffic_classes)` | VC 数应 ≥ class 数 + 死锁避免需求 |

## 参数依赖图（高层）

```
topology_type, N ──┬─→ TopologyClosedForm ──→ diameter, avg_hop, bisection, radix, wire_span
                   │
                   └─→ tile_pitch + signal_um → forward_link_latency
                                              ↓
allocator_type, V ──→ (t_pipe, η, frequency_GHz)
                                              ↓
                                           R 公式 ──→ buffer_depth_per_vc
                                                                  ↓
trace (placement, pattern) ──→ K_VA, K_SA ──→ E[contention] ────────┘
                                                                  ↓
HBM/SRAM params ──→ injection_rate_cap, consumer_rate ──→ Endpoint ↓
                                                                  ↓
                                                       Stats、verification ←
```

## 一句话理解

参数表的价值不是查阅方便，而是**让每个参数都有明确的"来源公式 / 消费位置 / 联动依赖"**——这样 sweep 是科学的，结论是可解释的，而不是参数空间里的盲目搜索。

## 建模启示

落地建议：

1. 把这张表落成一份 `params.yaml`，每个字段同时记录值、单位、来源页 URL、消费者函数名
2. simulator 启动时校验联动约束（如 `buffer_depth >= computed_R`），不满足直接报警
3. 每次发新 case card 必须附带 `params.yaml` 全量，避免 reviewer 凭记忆推参数值
4. 跨实验对比时，先 diff `params.yaml`——参数差异比结果差异更早暴露问题

这张表不是静态文档，而是 simulator、trace generator 和 case card 之间的共享契约。
