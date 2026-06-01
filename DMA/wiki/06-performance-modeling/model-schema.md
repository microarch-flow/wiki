# 模型数据结构与事件规范

上级：[06 性能建模与调优](./README.md)

相关：[参数与公式速查](./parameter-reference.md)、[从抽象模型到系统诊断](./modeling-method.md)、[DMA 引擎的组成](../03-dma-microarchitecture/engine-components.md)、[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)

## 这页在回答什么问题

各页「建模启示」里各自定义了一个小结构体（`DMAEngineState`、`DMAMetrics`、`DMATuningKnobs`、`ExpandedTransfer`、`MemoryInteraction`、`DMANoCFlow`、`DMAObservability`…），它们互相重叠又不一致。如果照着各页直接落地，会得到一堆字段冲突的对象。

这页把它们收敛成**单一事实来源**：一个统一的 `DMAModel` 顶层数据模型，加上一条**规范事件链**。其它页的结构体应理解为这张总表的子集投影，而不是各自独立的定义。

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
- `Interaction` → 事件链（驱动 `State` 演化）
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

## 规范事件链（canonical event taxonomy）

这是本页最关键的统一项。同一条 DMA 生命周期，原来在三页里有三套不同命名（scheduling 用 `request_issue/...`，metrics 用 `submit_ts/...`，address-descriptor 用 `descriptor_fetch_done/...`）。它们其实是**同一条链的不同切面**。下面是规范命名，所有页面应以此为准：

```text
[descriptor 层]
  descriptor_ready          # 软件提交 / ring 可见
  descriptor_fetch_done     # DMA 取到任务
  transaction_split         # 展开成子事务（边界/对齐拆分）

[transaction 层]  —— 每个子事务重复
  request_issue             # AR/AW 发出
  response_arrive           # R/B 返回
  data_commit               # 数据真正落位
  boundary_penalty          # （可选）边界拆分附加事件

[completion 层]
  completion_record         # 完成被记录
  completion_visible        # 对软件/下游可见
  slot_release              # 资源槽位释放
  consumer_ready            # 下游可继续推进
```

### 旧命名 → 规范命名对照

| 出处页 | 旧名 | 规范事件 |
| --- | --- | --- |
| metrics | `submit_ts` | `descriptor_ready` |
| metrics | `issue_ts` | `request_issue` |
| metrics | `transfer_done_ts` | `data_commit`(末笔) |
| metrics | `completion_visible_ts` | `completion_visible` |
| metrics | `consumer_ready_ts` | `consumer_ready` |
| scheduling | `request_issue` | `request_issue` |
| scheduling | `response_arrive` | `response_arrive` |
| scheduling | `data_commit` | `data_commit` |
| scheduling | `completion_record` | `completion_record` |
| scheduling | `slot_release` | `slot_release` |
| address-descriptor | `descriptor_fetch_done` | `descriptor_fetch_done` |
| address-descriptor | `transaction_split` | `transaction_split` |
| address-descriptor | `read_issue / write_issue` | `request_issue`(带 dir) |

### 时间戳与四段延迟的对应

[metrics-bottlenecks](./metrics-bottlenecks.md) 的四段延迟，全部能由规范事件相减得到：

```text
submit_latency                = request_issue        - descriptor_ready
service_time                  = data_commit(末)      - request_issue(首)
completion_visibility_latency = completion_visible    - data_commit(末)
consumer_ready_latency        = consumer_ready        - completion_visible
```

## 按 analysis_goal 启用事件集

不是每个模型都要全链。按目标裁剪（与 [goal-oriented-navigation](../01-overview/goal-oriented-navigation.md) 一致）：

| analysis_goal | 必须保留的事件 / 状态 | 可折叠的 |
| --- | --- | --- |
| `throughput` | request_issue / response_arrive / data_commit | completion_visible 与 data_commit 合并 |
| `tail_latency` | 全链，尤其 completion_visible 与 data_commit **不可合并** | — |
| `bringup` | descriptor_ready / completion_visible / slot_release | transaction 层细节 |
| `ai_supply` | request_issue / data_commit / consumer_ready + sram_port / injection | descriptor 取指细节 |

关键约束：**关心 tail latency / hang 时，`data_commit` 与 `completion_visible` 绝不能合并**——大量真实问题正是"数据已到、completion 未见"。

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

一个 `DMAModel` 总表 + 一条规范事件链，是把分散在各页的建模片段拼成可落地工具的"接口契约"；其余结构体都应视为它的子集投影。
