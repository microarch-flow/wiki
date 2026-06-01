# 参数与公式速查

上级：[06 性能建模与调优](./README.md)

相关：[模型数据结构与事件规范](./model-schema.md)、[从抽象模型到系统诊断](./modeling-method.md)、[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)

## 这页在回答什么问题

前面各章把 DMA 的因果结构讲清楚了，但「建模启示」里只点了参数名，没给数值、单位和公式。这页把它们集中成一张可直接用于建模的速查表：每个参数的单位、典型范围、由什么硬件量纲决定，以及把它们连起来的一阶解析公式。

> 重要前提：下表的数值是**量级级别的建模起点**，不是规格保证。真实值必须用硬件 counter 或仿真校准（见 [从抽象模型到系统诊断](./modeling-method.md) 的校准一节）。把它们当成 sanity check 的锚点，而不是结论。

## 一阶解析公式

这几条公式是 L1 / L2 模型的骨架，没有它们就只能靠仿真硬跑，也无法判断仿真结果是否合理。

### 1. 三端点带宽上界

任何一笔 DMA 路径都受源、互连、目的三端共同钳制：

```text
BW_path = min(BW_src, BW_interconnect, BW_dst)
```

这是 L1 理想带宽模型里 `bw_limit` 的正确取法——不是某一段的峰值，而是三段的最小值。任何单段规格再高，都不能突破其余两段。

### 2. Little's Law —— outstanding 该开多大

要靠 outstanding 隐藏 memory/互连延迟，所需的在飞事务数：

```text
outstanding_needed ≈ BW_target × RTT / bytes_per_request
```

- `RTT`：request 发出到 response 返回的往返延迟
- `bytes_per_request`：单笔事务有效字节（通常 = burst_len × data_width）

含义：outstanding 不是"越大越好"，而是有一个由"带宽目标 × 延迟"决定的**足够点**。超过这个点只会把排队和尾延迟后移（对应 [scheduling-outstanding](../03-dma-microarchitecture/scheduling-outstanding.md) 的核心结论）。

### 3. Burst / 传输效率

有效带宽相对峰值的折损，主要来自固定开销和边界拆分：

```text
efficiency = useful_bytes / (useful_bytes + overhead_bytes)

eff_bandwidth = peak_bandwidth × efficiency × (1 - boundary_split_penalty)
```

- `overhead_bytes`：每笔事务的 header / 握手 / 地址相位等效开销
- `boundary_split_penalty`：misaligned 头部 + 4KB/page/bank 边界拆分导致的额外事务占比

直觉：transfer/burst 越小，固定开销占比越高，效率越低；这就是 `size sweep` 实验里"效率从控制开销主导切到带宽主导"那个拐点的解析来源。

### 4. DRAM 有效带宽与 row hit

外存有效带宽随 row hit 率显著变化：

```text
eff_bw_dram ≈ peak_bw / (1 + miss_rate × (t_RC_overhead / t_burst))
```

含义：stride 访问打断 row hit 序列，每次 miss 都要付 `PRE → ACT` 的代价。这就是 [dma-and-memory-system](../05-system-integration/dma-and-memory-system.md) 里"规格够但访问形状不对就慢"的量化形式。精确建模应把 `row_hit_prob` 由地址映射 + stride 推导，而不是当常数。

### 5. Overlap / 双缓冲上界

计算与搬运重叠后的理想时间：

```text
T_overlap = max(T_compute, T_dma)        # 完美双缓冲
T_serial  = T_compute + T_dma            # 无重叠
overlap_efficiency = T_serial / T_overlap - 1   # 0 ~ 1，越大越好
```

只有当 buffer 数 ≥ 2 且 DMA 能在 compute 消费前补满下一块时，才接近 `T_overlap`。否则会退化到两者之间，这正是 [tiling-double-buffering](../04-programming-model/tiling-double-buffering.md) 要保证的条件。

### 6. 完成路径与 forward progress

软件/下游能继续推进的时间，不等于数据搬完的时间：

```text
T_consumer_ready = T_transfer_done + completion_visibility_latency + consumer_setup
```

只关心吞吐时可忽略后两项；关心真实 forward progress、tail latency 或 hang 时绝不能忽略（对应 [metrics-bottlenecks](./metrics-bottlenecks.md) 的四段延迟拆分）。

## 参数速查表

下表按"旋钮 / 结构容量 / 延迟 / 派生指标"分组。范围一栏给的是常见工程区间，跨 DMA 类型差异很大，按需收窄。

### 可调旋钮（Capability）

| 参数 | 单位 | 典型范围 | 由什么决定 | 关联公式 |
| --- | --- | --- | --- | --- |
| `burst_len` | beats | 4 ~ 64（AXI ≤256） | 协议上限、4KB 边界、data width | 公式 3 |
| `data_width` | byte | 4 ~ 128 | 总线宽度 | 公式 2 |
| `transfer/tile_bytes` | byte | 256B ~ 数 MB | 算子映射、buffer 容量 | 公式 3、5 |
| `queue_depth` | entries | 4 ~ 1024 | submit 路径、ring 大小 | 公式 2 |
| `max_outstanding` | txns | 4 ~ 256 | ID 数、scoreboard 容量 | 公式 2 |
| `num_channels` | — | 1 ~ 数十 | 多流隔离需求 | — |
| `priority/QoS_mode` | enum | RR / fixed / credit | 多流公平性目标 | — |
| `completion_mode` | enum | interrupt / poll / batch | 软件可见尾延迟 | 公式 6 |
| `stride` | byte | 任意 | 数据布局 | 公式 4 |

### 结构容量（Resource）

| 参数 | 单位 | 典型范围 | 说明 |
| --- | --- | --- | --- |
| `inflight_table_size` | entries | = max_outstanding | 在飞事务跟踪表 |
| `reorder/resp_buffer` | entries / byte | 取决乱序深度 | 乱序返回时必需 |
| `completion_q_depth` | entries | 8 ~ 数百 | completion backlog 上限 |
| `sram_ports` | 个 | 1 ~ 4 | 决定 DMA↔compute 端口冲突 |
| `sram_banks` | 个 | 2 ~ 32 | bank conflict 概率 |
| `mc_ports / channels` | 个 | 1 ~ 16 | 外存并行度 |

### 延迟参数（用于 L2/L3，单位按时钟域统一）

| 参数 | 量级（量纲，需校准） | 说明 |
| --- | --- | --- |
| `descriptor_fetch_latency` | 数十 ~ 数百 cycle | 从内存取 descriptor（片上 ring 更快） |
| `submit_latency` | 软件路径，可达 µs 级 | doorbell 到受理 |
| `interconnect_RTT` | 片上数十 cycle / 跨 die 更高 | 公式 2 的 RTT 片上分量 |
| `dram_return_latency` | 数十 ~ 数百 ns，**分布而非均值** | 受 row hit/queue 影响，长尾敏感 |
| `completion_visibility_latency` | 取决 interrupt/poll/batch | 公式 6 |

### 派生指标（Metrics，模型输出）

| 指标 | 单位 | 来源公式/事件 |
| --- | --- | --- |
| `effective_bandwidth` | byte/s | 公式 1×3 |
| `outstanding_occupancy` | txns（直方图） | 实时状态 |
| `response_latency` | 分布 + P95/P99 | 事件差 |
| `completion_backlog` | entries | 实时状态 |
| `overlap_efficiency` | 0~1 | 公式 5 |
| `consumer_ready_latency` | time | 公式 6 |

## 怎么用这张表做建模

1. **L1（上界 sanity check）**：只用公式 1，配合 `bytes / BW_path` 估端到端时间，判断方案是否量级可行。
2. **L2（队列-事务）**：加公式 2、3、6，引入 `max_outstanding / queue_depth / completion_*` 旋钮，开始能解释 stall 和 latency hiding 拐点。
3. **L3（系统耦合）**：加公式 4、5，把 `row_hit_prob`、`sram_ports`、`stride` 展开成真实地址映射，解释多流冲突和尾延迟。

层次选择判据见 [modeling-method](./modeling-method.md)；统一的字段命名见 [model-schema](./model-schema.md)。

## 常见误解

常见误解：`这张表的数值可以直接当模型参数`。实际上它们是校准起点和量级锚点，真实值必须用 counter/仿真标定。

常见误解：`outstanding 越大带宽越高`。公式 2 说明它有一个由带宽×延迟决定的足够点，超过只会后移排队。

常见误解：`DRAM 带宽是常数`。公式 4 说明它随 row hit 率变化，而 row hit 率由 DMA 的 stride/burst 和地址映射共同决定。

## 一句话理解

把各页「建模启示」里散落的参数名，落成"单位 + 范围 + 决定因素 + 公式"的速查表，才能让模型从定性骨架变成可计算、可校准的工具输入。
