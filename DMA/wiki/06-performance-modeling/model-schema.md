# 模型数据结构与事件规范

上级：[06 性能建模与调优](./README.md)

相关：[参数与公式速查](./parameter-reference.md)、[从抽象模型到系统诊断](./modeling-method.md)、[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)

## 这页在回答什么问题

各页「建模启示」里各自定义了一个小结构体（`DMAEngineState`、`DMAMetrics`、`DMATuningKnobs`、`ExpandedTransfer`、`MemoryInteraction`、`DMANoCFlow`、`DMAObservability`…），它们互相重叠又不一致。如果照着各页直接落地，会得到一堆字段冲突的对象。

这页把它们收敛成**单一事实来源**：一个统一的 `DMAModel` 顶层数据模型，加上一组**规范事件与条件偏序**。其它页的结构体应理解为这张总表的子集投影，而不是各自独立的定义。

## 顶层数据模型

```text
DMAModel {
  Knobs          # 可调旋钮（Capability）—— 模型输入
  Resources      # 结构容量（Resource）—— 模型输入
  State          # 运行时状态 —— 仿真过程中演化
  Metrics        # 派生指标 —— 模型输出
  Observability  # 可观测投影 —— counter / histogram / 快照
}
```

四个抽象层（`Resource / Topology / Interaction / Capability`，定义见下节）到字段的映射是固定的：

- `Capability` → `Knobs`
- `Resource` → `Resources`
- `Interaction` → 事件及依赖关系（驱动 `State` 演化）
- `Topology` → `Resources` 里的共享点 + 路径定义

### Knobs（Capability，输入）

```text
Knobs {
  burst_len
  data_width
  tile_bytes
  queue_depth
  max_outstanding
  num_channels
  priority_mode      # rr | fixed | age | credit | token
  completion_mode    # interrupt | poll | batch
  stride
  analysis_goal      # bringup | throughput | tail_latency | ai_supply
}
```

`analysis_goal` 来自 [goal-oriented-navigation](../01-overview/goal-oriented-navigation.md) 的「建模启示」：它决定下面哪些 `State` 字段需要启用，避免模型同时保留太多无关细节。

### Resources（Resource + Topology，输入）

```text
Resources {
  inflight_table_size
  resp_buffer_size
  completion_q_depth
  sram_ports
  sram_banks
  mc_ports
  channels
  path[]           # Topology: src_node -> dst_node 路径与共享点
}
```

### State（Interaction 驱动，运行时）

```text
State {
  fetch_q                  # 来自 engine-components 的 cmd_frontend
  issue_q
  inflight_table           # 在飞事务，key = txn_id
  resp_buffer
  completion_q
  outstanding_count
  oldest_inflight_age
  response_queue_occupancy
  completion_backlog
  # L3 才启用：
  sram_port_busy
  bank_conflict_count
  row_hit_state
  injection_rate
  ejection_stall_cycles
}
```

### Metrics（输出）与 Observability

```text
Metrics {
  bytes_moved
  effective_bandwidth
  submit_latency
  service_time
  completion_visibility_latency
  consumer_ready_latency
  tail_percentiles        # P95 / P99
  overlap_efficiency
}

Observability {
  counters                # 见 debug-observability
  histograms              # outstanding / response_latency
  phase_state             # 当前阻塞在哪一段
  oldest_inflight_age
}
```

`Metrics` 与 `Observability` 不重复存储：`Observability` 是 `State` 在每个采样点的投影，`Metrics` 是事件流的统计汇总。

## 规范事件与偏序（canonical event taxonomy）

统一名称不意味着所有事务共享一条线性事件链。每条事件应记录 `descriptor_id`、`subtransaction_id`、协议、方向、观察点、时间，以及成功/错误状态；beat 级事件还要记录 beat index。`request_issue` 是实现选择的发出或接口接受点，必须明确是哪一种。`data_commit` 必须标识是本地 buffer、目标 memory 系统、DRAM 还是 CPU 可见域的哪一个事件。未观测到的事件保持未知，不可从其他事件自动推导。

| 层 | 事件 | 定义与条件 |
| --- | --- | --- |
| descriptor | `descriptor_ready / descriptor_fetch_done / transaction_split` | 描述符可供设备使用、取回、按路径规则拆成子事务 |
| transaction | `request_issue / address_accept / data_accept / response_accept` | 按协议和方向记录地址、数据、响应握手；并非每种协议都有每类事件 |
| data | `data_commit(domain, beat)` | 指定域内的一次数据落位；各 beat 可分别发生 |
| transfer | `transfer_done` | 设备为该任务定义的传输完成条件成立；须列出所有子事务和错误条件 |
| completion | `completion_record / completion_visible / consumer_ready` | 完成记录生成、通知或记录对软件可见、消费者满足数据与所有权条件 |
| resource | `slot_release(resource_kind, id)` | 指定 queue、buffer、outstanding、descriptor 或 completion 槽位释放 |

### AXI4、PCIe 的必要依赖

AXI4 读事务的 AR 在上升沿握手后，R beat 逐个握手。每个已接收的成功 R beat 可写入目标 buffer，故先前 beat 的 `data_commit` 可以早于最后一个 R beat。最后 R beat 的 `RLAST` 握手结束接口读事务；错误 beat 及其后处理按协议和引擎契约处理。

AXI4 写事务中，AW 与各 W beat 相互独立，W 可以先于 AW 被接收。针对同一笔写，接收完 AW 和最后一个带 `WLAST` 的 W beat，才可生成 B；B 握手结束该接口写事务。数据可以逐 beat 在 B 之前被写入某个位置，也可能在允许提前响应的路径中在 B 之后才到达最终位置。`B` 本身不保证 DRAM 已更新，也不保证 CPU cache 可见。必须同时考虑属性、互连、内存系统与设备契约。

PCIe Memory Read 是 non-posted 请求，可由一个或多个带数据的 Completion 返回；需跟踪 tag、片段及错误。Memory Write 是 posted 请求，不会产生针对该 MWr 的事务 Completion。发送端链路 ACK 或本地发送槽释放也不证明目标软件已能看到数据；若系统用读回、屏障或额外 completion 表示完成，必须依据设备、排序和软件契约单独建模。参考 [Arm IHI 0022H](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf?hash=6325311012DDADF238C35A6C0FD734E520754F82&la=en&revision=71bd7c57-2ed7-487b-bc3e-68c4ab56fa5f) 和 [AMD AXI Bridge for PCIe：Completion TLP Errors](https://docs.amd.com/r/en-US/pg055-axi-bridge-pcie/Completion-TLP-Errors)。

各资源的释放条件分别定义。例如，输入数据 FIFO 的一个槽可在数据被下游接收后释放；读 outstanding 条目可以在最后 R beat 握手后释放；completion queue 的槽按设备与软件回收约定释放；descriptor 槽也可能在设备已取得或稍后的约定时点释放。不同槽可以先于或晚于 completion 可见；不存在通用的最后一步 `slot_release`。

### 时间戳与延迟

若某具体设备契约保证 `descriptor_ready ≤ first_request_issue ≤ transfer_done ≤ completion_visible ≤ consumer_ready`，可定义：

```text
submit_latency                = first_request_issue - descriptor_ready
service_time                  = transfer_done - first_request_issue
completion_visibility_latency = completion_visible - transfer_done
consumer_ready_latency        = consumer_ready - completion_visible
```

这是带前提的测量分解，不是通用协议顺序。`transfer_done` 的观察域与任务范围必须与参考设备一致。若设备允许提前通知，或观测不到目标落位，上式中相应区间不能解释成非负等待时间，应分别报告事件和不确定性。completion 记录可见也不自动代表 payload 对 CPU 可见；读取前可能还需要 DMA 同步与所有权交接。

### 按目标选择事件

| 目标 | 需要保留 | 可折叠的条件 |
| --- | --- | --- |
| `throughput` | 协议对应请求、数据、资源占用和释放 | 所折叠的 completion 不限制供数或回收，且定义已验证 |
| `tail_latency` / `bringup` | 上述事件、完成域、错误、独立槽释放和可见性 | 只折叠不影响所测边界的细节 |
| `ai_supply` | 数据到目标 SRAM、consumer-ready、端口冲突 | 与供数无关的描述符细节 |

旧页面的 `submit_ts` 对应具体定义的 `descriptor_ready`，`issue_ts` 对应具体定义的首个 `request_issue`；`transfer_done_ts` 对应约定的 `transfer_done`，不可无条件等同最后 `data_commit`。其它旧名按观察点和协议逐项映射。

## 与各页结构体的关系

| 各页结构体 | 在本模型中的位置 |
| --- | --- |
| `DMATuningKnobs`（optimization-playbook） | = `Knobs` 子集 |
| `DMAEngineState`（engine-components） | = `State` 的 `fetch_q/issue_q/inflight_table/...` |
| `ExpandedTransfer`（address-descriptor） | = `transaction_split` 事件产物 |
| `MemoryInteraction`（dma-and-memory-system） | = L3 `State` 的内存子集 |
| `DMANoCFlow`（dma-and-noc） | = `Resources.path[]` + L3 注入/回压状态 |
| `DMAMetrics`（metrics-bottlenecks） | = `Metrics` |
| `DMAObservability`（debug-observability） | = `Observability` |

## 常见误解

常见误解：`各页结构体可以各自独立实现`。实际上它们重叠且命名冲突，必须收敛到这一张总表，否则字段对不齐。

常见误解：`事件名只是叫法不同，无所谓`。实际上 event-driven 仿真里时间戳语义必须统一，否则四段延迟会算错。

常见误解：`模型应该一次性建全链`。实际上应按 `analysis_goal` 启用事件子集，否则又慢又难解释。

## 一句话理解

一个 `DMAModel` 总表加协议相关事件和条件偏序，是把分散的建模片段拼成接口契约的基础；其余结构体可视为其子集投影。
