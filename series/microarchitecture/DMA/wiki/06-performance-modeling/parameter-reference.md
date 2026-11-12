# 参数与公式速查

上级：[06 性能建模与调优](./README.md)

相关：[模型数据结构与事件规范](./model-schema.md)、[从抽象模型到系统诊断](./modeling-method.md)、[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)

## 这页在回答什么问题

前面各章把 DMA 的因果结构讲清楚了，但「建模启示」里只点了参数名，没给数值、单位和公式。这页把它们集中成一张可直接用于建模的速查表：每个参数的单位、典型范围、由什么硬件量纲决定，以及把它们连起来的一阶解析公式。

> 重要前提：下表的数值是**量级级别的建模起点**，不是规格保证。真实值必须用硬件 counter 或仿真校准（见 [校准与验证](./calibration-validation.md)）。把它们当成 sanity check 的锚点，而不是结论。

## 一阶解析公式

这几条公式是 L1 / L2 模型的骨架，没有它们就只能靠仿真硬跑，也无法判断仿真结果是否合理。

### 1. 路径带宽上界与共享资源

源、互连和目的各有独立资源，且每复制 1 byte 在每段只占用 1 byte 服务量时，理想的持续有效复制带宽满足：

```text
BW_copy ≤ min(BW_src, BW_interconnect, BW_dst)
```

这是上界，不保证达到。还要检查各段是否共享资源。更一般地，资源 `i` 的容量为 `B_i`，每复制 1 byte 占用该资源 `a_i` byte 的服务量，则 `BW_copy ≤ min_i(B_i / a_i)`；前提是单位相同，且 `a_i` 覆盖所有经过该资源的方向。

例如 DMA 复制时，读和写都经过同一条半双工链路；其总服务能力为 `B` byte/s。每复制 1 byte 需要读 1 byte、写 1 byte，因此链路的复制上界为 `B/2`。若读写各有独立、可同时工作的 `B` byte/s 通路，对应上界才可达 `B`。协议开销、仲裁和 memory 限制只会进一步降低有效带宽。单次完成时间还包含启动、流水填充和排空，不能只用 `bytes/BW_copy` 声称精确值。

### 2. Little's Law —— outstanding 该开多大

要靠 outstanding 隐藏 memory/互连延迟，所需的在飞事务数：

```text
outstanding_needed ≈ BW_target × RTT / bytes_per_request
```

- `RTT`：从计入 outstanding 到释放该窗口的平均持续时间；AXI 读可选从 AR 握手到最后 R 握手，具体口径由实现定义。PCIe posted MWr 不等待事务 Completion，必须按实际发送资源回收时间定义，不能套用 read RTT
- `bytes_per_request`：同一统计窗口内每笔事务平均有效字节；窄传输、首尾 mask 或拆分时不能直接等同 `burst_len × data_width`。

在稳定状态、相同事务边界和平均值成立时，公式给平均在途需求，不是性能保证。例：目标 25 GB/s、平均 RTT 100 ns、平均 400 B/请求，平均需要 `25e9×100e-9/400=6.25` 笔，整数容量至少 7；还须有足够请求供给、带宽、允许的并行和返回空间。RTT 随负载可能上升，增槽可能继续提高吞吐，也可能增加排队；不能据此确定唯一拐点。

### 3. Burst / 传输效率

有效带宽相对峰值的折损，主要来自固定开销和边界拆分：

```text
efficiency = useful_bytes / (useful_bytes + overhead_bytes)

eff_bandwidth ≈ peak_bandwidth × efficiency × (1 - boundary_split_penalty)
```

- `overhead_bytes`：仅在与 payload 占用同一个串行瓶颈资源时，才可折算 header、握手或地址的等效字节；AXI 独立地址、数据和响应通道可重叠，不能机械相加
- `boundary_split_penalty`：经测量或模型单独定义的边界损失比例；不得与 `overhead_bytes` 重复计入同一损失

直觉：transfer/burst 越小，固定开销占比越高，效率越低；这就是 `size sweep` 实验里"效率从控制开销主导切到带宽主导"那个拐点的解析来源。

### 4. DRAM 有效带宽与 row hit

在单 bank、每次 miss 的额外时间不能被其他 bank 或排队重叠的简化模型中，可用下式观察 row hit 的影响；它不是通用 DRAM 带宽公式：

```text
eff_bw_dram ≈ peak_bw / (1 + miss_rate × (t_RC_overhead / t_burst))
```

这里 `miss_rate` 包括两类访问，`t_RC_overhead` 表示相对于 row hit、按这两类出现比例加权的平均额外非重叠时间，而不是固定对每次 miss 套用的完整 `tRC`。若 bank 当前关闭，访问新行需要 `ACT`，无需再 `PRE`；若 bank 已打开另一行，则需先满足现有行的时序约束，执行 `PRE`，再执行新行的 `ACT`。已打开目标行才是 row hit。`tRP`、`tRCD`、写恢复、调度和跨 bank 重叠都会影响实测代价；本式只用于所述单 bank 且额外时间不重叠的近似。[dma-and-memory-system](../05-system-integration/dma-and-memory-system.md) 的访问形状还受地址映射、stride、调度和 page policy 共同影响，不应把 `row_hit_prob` 当作与这些条件无关的常数。

### 5. 单次、有限批次与稳态

设 `D=T_dma` 是每 tile 的搬运时间，`C=T_compute` 是计算时间，处理 `N≥1` 个同大小 tile。假设 DMA 与 compute 独立并行、两个 buffer 足以轮换、无其他共享资源冲突与额外开销，且任务之间只有同 tile 的搬运先于计算这一依赖：

```text
T_single = D + C
T_serial(N) = N * (D + C)
T_ideal(N) = D + C + (N - 1) * max(D, C)
steady_interval = max(D, C)       # 完成相邻 tile 的间隔，不是单次总时间
relative_speedup_gain = T_serial(N) / T_ideal(N) - 1
```

例如 `D=2`、`C=5`、`N=3`，理想总时间为 `2+5+2×5=17` cycle，稳态间隔为 5 cycle；串行总时间是 21 cycle。首块仍须先搬运后计算。每个 buffer 必须在前一个使用者释放后才能复用；真实 DMA 的写回和 SRAM 端口还可能与填充、计算冲突。逐项时间线见 [Tiling 与 Double Buffer](../04-programming-model/tiling-double-buffering.md#单次任务与有限批次)。

`relative_speedup_gain` 是相对串行的加速增量，不是“隐藏掉的时间比例”。本页旧的 `overlap_efficiency` 指标若继续使用，应注明采用该定义及 N；有额外开销或不同工作量时范围不必为 0–1。稳态周期并不要求 `D≤C`，但只有 `D≤C` 且其他条件满足时计算侧可无搬运等待。若只看单次任务，双缓冲本身不能让同一 tile 的搬运与依赖它的计算重叠。

### 6. 完成路径与 forward progress

若设备契约保证先在指定域达到 `transfer_done`，再使 completion 可见，并且 consumer 的后续准备串行执行，才可以写成：

```text
T_consumer_ready = T_transfer_done + completion_visibility_latency + consumer_setup
```

此式的三项分别是同一任务的时间点与两段增量，不代表 AXI B、PCIe posted MWr 或一般设备都具有这种顺序。completion 可见也不等于 CPU payload 可见；若通知可提前或存在并行准备，应单独建事件依赖。只有证明后两项不限制稳态供数或回收，吞吐模型才可折叠。参见 [事件与偏序](./model-schema.md#规范事件与偏序canonical-event-taxonomy)。

## 参数速查表

下表按"旋钮 / 结构容量 / 延迟 / 派生指标"分组。范围一栏给的是常见工程区间，跨 DMA 类型差异很大，按需收窄。

### 可调旋钮（Capability）

| 参数 | 单位 | 典型范围 | 由什么决定 | 关联公式 |
| --- | --- | --- | --- | --- |
| `burst_len` | beats | 工作负载和实现决定 | AXI4 INCR 最多 256；FIXED/WRAP 另有约束，且须检查 4KB | 公式 3 |
| `data_width` | byte | 4 ~ 128 | 总线宽度 | 公式 2 |
| `transfer/tile_bytes` | byte | 256B ~ 数 MB | 算子映射、buffer 容量 | 公式 3、5 |
| `queue_depth` | entries | 4 ~ 1024 | submit 路径、ring 大小 | 公式 2 |
| `max_outstanding` | txns | 实现决定 | scoreboard/缓冲/下游容量；同一 ID 可有多笔在途 | 公式 2 |
| `num_channels` | — | 1 ~ 数十 | 多流隔离需求 | — |
| `priority/QoS_mode` | enum | RR / fixed / credit | 多流公平性目标 | — |
| `completion_representation` | enum | CQE / status / token | 设备如何表达命令状态及其完成边界 | 公式 6 |
| `notification_method` | enum | interrupt / polling / hybrid | 软件如何发现完成状态 | 发现延迟 |
| `completion_consume_batch` | 条目数或策略 | 由软件实现决定 | 每次处理多少已就绪 completion | 消费与回收速率 |
| `interrupt_moderation` | 数量阈值 / 时间阈值或关闭 | 由设备和驱动决定 | 多个完成事件何时触发通知 | 通知延迟 |
| `stride` | byte | 由字段位宽、符号和 IP 支持决定 | 数据布局、地址溢出及映射 | 公式 4 |

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
| `completion_visibility_latency` | 由写入和映射可见性路径决定 | 公式 6 的增量，前提是设备保证所述先后顺序；通知和消费另计 |
| `completion_discovery_latency` | 取决 polling 周期、中断投递及 moderation | 完成状态可按契约观察后至软件发现的时间 |

### 派生指标（Metrics，模型输出）

| 指标 | 单位 | 来源公式/事件 |
| --- | --- | --- |
| `effective_bandwidth` | byte/s | 公式 1×3 |
| `outstanding_occupancy` | txns（直方图） | 实时状态 |
| `response_latency` | 分布 + P95/P99 | 事件差 |
| `completion_backlog` | entries | 实时状态 |
| `overlap_efficiency` | 无量纲 | 公式 5 的相对串行加速增量；必须注明 N 与计时边界 |
| `consumer_ready_latency` | time | 公式 6 |

## 怎么用这张表做建模

1. **L1（上界 sanity check）**：按公式 1 的资源服务需求求带宽上界，用 `bytes / BW_upper` 得到传输时间下界；单次任务还需考虑启动与排空。
2. **L2（队列-事务）**：加公式 2、3、6，引入 `max_outstanding / queue_depth / completion_*` 旋钮，开始能解释 stall 和 latency hiding 拐点。
3. **L3（系统耦合）**：加公式 4、5，把 `row_hit_prob`、`sram_ports`、`stride` 展开成真实地址映射，解释多流冲突和尾延迟。

层次选择判据见 [modeling-method](./modeling-method.md)；统一的字段命名见 [model-schema](./model-schema.md)。

## 常见误解

常见误解：`这张表的数值可以直接当模型参数`。实际上它们是校准起点和量级锚点，真实值必须用 counter/仿真标定。

常见误解：`outstanding 越大带宽越高`。公式 2 只给指定 RTT 和目标吞吐下的窗口需求；更大窗口的效果还需看负载、服务及排队。

常见误解：`DRAM 带宽是常数`。公式 4 说明它随 row hit 率变化，而 row hit 率由 DMA 的 stride/burst 和地址映射共同决定。

## 一句话理解

把各页「建模启示」里散落的参数名，落成"单位 + 范围 + 决定因素 + 公式"的速查表，才能让模型从定性骨架变成可计算、可校准的工具输入。
