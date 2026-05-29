# Core Data Structures

上级：[08 Simulator Construction](./README.md)

相关：[Simulator Design Spec](./simulator-design-spec.md)、[Router Pipeline Pseudocode](./router-pipeline-pseudocode.md)、[Verification And Calibration](./verification-and-calibration.md)

## 这页在回答什么问题

这页回答：第一版 NoC simulator 的核心状态到底应该落成哪些数据结构，每个结构必须有哪些**带类型的字段**、哪些**不变量**必须始终成立、以及结构之间的**耦合关系**是什么。

读完应该能直接照表落代码，不需要再二次诠释。

## 设计原则

第一版数据结构最重要的不是"通用到包打天下"，而是：

- 清晰表达当前状态
- 支持可解释的状态转移
- 不把未来扩展卡死

因此推荐对象少而清楚，而不是大而全。每个字段要能回答：**谁写、谁读、什么时候写、写完后哪些不变量必须成立**。

## 类型字典

后面的字段表统一使用这些基本类型，先约定清楚：

| 别名 | 底层 | 说明 |
|------|------|------|
| `NodeId` | `uint16` | tile / endpoint 的全局编号 |
| `RouterId` | `uint16` | router 的全局编号；常与 `NodeId` 一一对应 |
| `PortId` | `int8` | router 端口；`-1` 表示本地 / endpoint 方向 |
| `VcId` | `int8` | 0..NUM_VCS-1；`-1` 表示未分配 |
| `Cycle` | `uint64` | 全局周期号，单调递增 |
| `PacketId` | `uint64` | 全局唯一 packet 编号 |
| `FlitId` | `uint64` | 全局唯一 flit 编号 |
| `FlowId` | `uint32` | workload 层面的逻辑流编号，用于依赖关系 |
| `Bytes` | `uint32` | 字节计数 |

## 枚举

下面三个枚举被所有结构和统计共用，**越早冻结越省心**：

```text
FlitType        := HEADER | BODY | TAIL | HEAD_TAIL
TrafficClass    := CONTROL | MEMORY_REQUEST | MEMORY_RESPONSE | STREAM | BULK_DMA
StallReason    := NONE
                 | NO_CREDIT          // 下游 VC 无 credit
                 | SWITCH_CONFLICT    // SA 未授予
                 | VC_ALLOC_FAIL      // VA 未授予
                 | EJECTION_BLOCKED   // 目的端 ejection queue 满
                 | INJECTION_BLOCKED  // 源端注入队列满 / 无 credit
                 | ROUTE_BLOCKED      // 源端依赖 / 路由前置条件未满足
                 | HEADER_NOT_ROUTED  // body/tail 等待 header 建路完成
```

辅助状态枚举（用于 VC / Packet 状态机）：

```text
VcState     := IDLE                  // 无 flit
              | ROUTING               // header 在 RC
              | WAITING_VA            // 已 RC，等待 VA
              | WAITING_SA            // 已 VA，等待 SA
              | ACTIVE                // wormhole 路径已建立，body/tail 流动中
              | BLOCKED_NO_CREDIT     // path 建好，但下游无 credit

PacketState := WAITING_DEPENDENCY     // workload DAG 上游未完成
              | IN_INJECTION_QUEUE
              | IN_FLIGHT
              | EJECTING               // 目的端 ejection 处理中
              | COMPLETED
```

## Packet

`Packet` 偏 workload / flow 语义，是"一个传输请求"的抽象。它在网络里不直接前进，但承载依赖、统计、和 trace 回放需要的全部上下文。

### Packet 字段

| 字段 | 类型 | 必/选 | 写入者 | 语义 |
|------|------|------|--------|------|
| `packet_id` | `PacketId` | 必 | generator | 全局唯一 |
| `src` | `NodeId` | 必 | generator | 源 endpoint |
| `dst` | `NodeId` | 必 | generator | 目的 endpoint（unicast）|
| `traffic_class` | `TrafficClass` | 必 | generator | 用于分类 VC / 调度 |
| `num_flits` | `uint16` | 必 | generator | 一定 ≥ 1 |
| `size_bytes` | `Bytes` | 必 | generator | 用于带宽统计 |
| `flow_id` | `FlowId` | 必 | generator | workload 层的逻辑流，用于聚合统计 |
| `creation_cycle` | `Cycle` | 必 | generator | packet 进入 pending 队列的周期 |
| `ready_cycle` | `Cycle` | 必 | scheduler | 所有依赖满足、可以注入的周期 |
| `injection_cycle` | `Cycle` | 必 | endpoint | 第一个 flit 真正离开 NI 的周期 |
| `completion_cycle` | `Cycle` | 必 | endpoint | tail 被 consumer 取走的周期 |
| `state` | `PacketState` | 必 | scheduler/endpoint | 状态机当前值 |
| `depends_on` | `list<PacketId>` | 选 | generator | workload DAG 上游依赖 |
| `route_hint` | `list<PortId>` | 选 | generator | source routing 时由 generator 预填 |
| `priority` | `uint8` | 选 | generator | 仲裁时使用；缺省 0 |
| `multicast_dsts` | `list<NodeId>` | 选 | generator | 仅 multicast 包；为空表示 unicast |

### Packet 不变量

- `num_flits ≥ 1`，且其中**有且仅有一个 HEADER 和一个 TAIL**；如 `num_flits == 1` 则该 flit 是 `HEAD_TAIL`
- `creation_cycle ≤ ready_cycle ≤ injection_cycle ≤ completion_cycle`
- `state` 只能按 `WAITING_DEPENDENCY → IN_INJECTION_QUEUE → IN_FLIGHT → EJECTING → COMPLETED` 单向推进
- 若 `depends_on` 非空，所有上游 `state == COMPLETED` 后才能进入 `IN_INJECTION_QUEUE`

## Flit

`Flit` 是真正进入网络推进的对象，是 router pipeline 每一拍读写的最小单位。

### Flit 字段

| 字段 | 类型 | 必/选 | 写入者 | 语义 |
|------|------|------|--------|------|
| `flit_id` | `FlitId` | 必 | generator | 全局唯一 |
| `packet_id` | `PacketId` | 必 | generator | 反查 `Packet` |
| `src` / `dst` | `NodeId` | 必 | generator | 复制自 packet，便于 router 不查表 |
| `traffic_class` | `TrafficClass` | 必 | generator | 复制自 packet |
| `flit_type` | `FlitType` | 必 | generator | HEADER/BODY/TAIL/HEAD_TAIL |
| `seq_in_packet` | `uint16` | 必 | generator | 0 即 HEADER |
| `num_flits_in_packet` | `uint16` | 必 | generator | 冗余但便于本地校验 |
| `current_router_id` | `RouterId` | 必 | accept_arriving_flits | 当前所在 router |
| `current_input_port` | `PortId` | 必 | accept_arriving_flits | 在哪个 input port |
| `assigned_vc` | `VcId` | 必 | VA / generator | input VC 编号；HEADER 由 VA 写，body/tail 继承 |
| `next_output_port` | `PortId` | 选 | compute_route | HEADER 经 RC 后写；body/tail 沿用 packet path |
| `next_output_vc` | `VcId` | 选 | run_vc_allocator | HEADER 经 VA 后写 |
| `injection_cycle` | `Cycle` | 必 | endpoint | 离开源 NI 的周期 |
| `enter_current_router_cycle` | `Cycle` | 必 | accept_arriving_flits | 用于 per-hop latency |
| `scheduled_exit_cycle` | `Cycle` | 选 | run_switch_allocator | 用于双缓冲调度 |
| `hop_count` | `uint16` | 必 | move_flit | 经过的 router 数 |
| `stall_cycles_so_far` | `uint32` | 必 | tick_router | 在本 router 累计停顿周期 |
| `last_stall_reason` | `StallReason` | 必 | tick_router | 上一拍归因；用于 attribution |
| `phit_index` | `uint8` | 选 | endpoint | 若 flit 跨多 phit，标记当前 phit 序号 |

### Flit 不变量

- `seq_in_packet == 0 ↔ flit_type ∈ {HEADER, HEAD_TAIL}`
- `seq_in_packet == num_flits_in_packet - 1 ↔ flit_type ∈ {TAIL, HEAD_TAIL}`
- 同一 packet 的所有 flit 必须沿**同一路径**前进（wormhole）：HEADER 一旦 RC 完成，后续 body/tail 的 `next_output_port / next_output_vc` 必须沿用
- `assigned_vc == -1` 当且仅当 flit 还在 endpoint 注入队列里
- `hop_count` 在 `move_flit` 后严格 +1

## VC / Input Buffer State

每个 input port 上的每个 VC 一份。这层是 wormhole 路径占用的核心。

### InputVcState 字段

| 字段 | 类型 | 必/选 | 写入者 | 语义 |
|------|------|------|--------|------|
| `queue` | `deque<Flit>` | 必 | accept/move | 长度 ≤ `buffer_depth` |
| `vc_state` | `VcState` | 必 | tick_router | 状态机 |
| `active_packet_id` | `PacketId` | 必 | VA / release_path_state | 当前占用本 VC 的 packet；空闲时为 0 |
| `routed` | `bool` | 必 | compute_route | HEADER 是否已完成 RC |
| `output_port` | `PortId` | 必 | compute_route | 已建路的下游端口 |
| `output_vc` | `VcId` | 必 | run_vc_allocator | 已分配的下游 VC |
| `vc_alloc_request_cycle` | `Cycle` | 选 | request_vc_allocation | 用于 VA stall 测量 |
| `sa_request_cycle` | `Cycle` | 选 | request_switch | 用于 SA stall 测量 |
| `last_stall_reason` | `StallReason` | 必 | tick_router | 归因 |

### InputVcState 不变量

- `queue.size() ≤ buffer_depth`
- `vc_state == IDLE ↔ queue.empty() ∧ active_packet_id == 0`
- `vc_state ∈ {ACTIVE, BLOCKED_NO_CREDIT}` ⇒ `routed == true ∧ output_port ≥ 0 ∧ output_vc ≥ 0`
- 当 TAIL 离开本 VC 时，必须把 `active_packet_id = 0`、`routed = false`、`output_port = output_vc = -1`、`vc_state = IDLE`（路径释放）

## Router

`Router` 是单个 tile 内的路由器实例，持有所有 input VC、output credit、仲裁中间结果，以及本地 ejection 队列。

### Router 字段

| 字段 | 类型 | 必/选 | 写入者 | 语义 |
|------|------|------|--------|------|
| `router_id` | `RouterId` | 必 | 构造 | 全局编号 |
| `num_input_ports` | `int` | 必 | 构造 | 含 1 个 local 端口 |
| `num_output_ports` | `int` | 必 | 构造 | 通常等于 input ports |
| `num_vcs` | `int` | 必 | 构造 | 每端口 VC 数 |
| `buffer_depth` | `int` | 必 | 构造 | 每 VC 缓冲深度（单位 flit）|
| `input_vcs[port][vc]` | `InputVcState[][]` | 必 | tick_router | 核心状态 |
| `output_credit[port][vc]` | `int[][]` | 必 | accept_returning_credits / move_flit | 必须 ≥ 0 |
| `output_vc_busy[port][vc]` | `bool[][]` | 必 | VA / release_path_state | 是否已被上游某 input VC 持有 |
| `output_vc_holder[port][vc]` | `(PortId, VcId)[][]` | 必 | VA / release_path_state | 谁持有；释放后置 `(-1,-1)` |
| `va_request[input_port][input_vc]` | `(PortId, VcId)` | 选 | request_vc_allocation | 本拍 VA 请求登记 |
| `va_grant[input_port][input_vc]` | `(PortId, VcId)` | 选 | run_vc_allocator | 本拍 VA 授予 |
| `sa_request[input_port][input_vc]` | `PortId` | 选 | request_switch | 本拍 SA 请求登记 |
| `sa_grant[input_port][input_vc]` | `bool` | 选 | run_switch_allocator | 本拍 SA 授予 |
| `pipeline_register[stage]` | `Flit?` | 选 | tick_router | cycle-accurate 实现时的 BW/RC/VA/SA/ST 流水线寄存器 |
| `local_ejection_queue` | `deque<Flit>` | 必 | move_flit (到 local port) | 长度 ≤ `ejection_depth` |
| `pending_credit_returns` | `list<(PortId, VcId, Cycle)>` | 必 | schedule_credit_return | 待回传的 credit，含期望返回周期 |

### Router 不变量

- `output_credit[p][v] ∈ [0, buffer_depth]`
- `output_vc_busy[p][v] == true ↔ 存在 (ip, iv) 使得 input_vcs[ip][iv].output_port==p ∧ input_vcs[ip][iv].output_vc==v ∧ vc_state ∈ {ACTIVE, BLOCKED_NO_CREDIT}`
- 任意 `output_vc[p][v]` **同一时刻只能被一个上游 input VC 持有**（wormhole 互斥）
- `output_vc_busy[p][v] == false ↔ output_vc_holder[p][v] == (-1, -1)`
- 每拍：SA 授予数 ≤ `min(num_input_ports, num_output_ports)`
- `local_ejection_queue.size() ≤ ejection_depth`

## Link

`Link` 是 router 间的物理通道。第一版可简化为定延迟流水线，但接口要为多拍延迟和 credit 反向延迟留好位置。

### Link 字段

| 字段 | 类型 | 必/选 | 写入者 | 语义 |
|------|------|------|--------|------|
| `link_id` | `uint32` | 必 | 构造 | 全局编号 |
| `src` | `(RouterId, PortId)` | 必 | 构造 | 上游 |
| `dst` | `(RouterId, PortId)` | 必 | 构造 | 下游 |
| `forward_latency_cycles` | `uint8` | 必 | 构造 | flit 前向延迟 |
| `return_latency_cycles` | `uint8` | 必 | 构造 | credit 反向延迟 |
| `channel_width_bits` | `uint16` | 必 | 构造 | 用于 phit / 带宽统计 |
| `forward_pipe[i]` | `Flit?[]` | 必 | move_flit / accept_arriving_flits | 长度 = `forward_latency_cycles`；每拍移位 |
| `return_pipe[i]` | `Credit?[]` | 必 | schedule_credit_return / accept_returning_credits | 长度 = `return_latency_cycles` |
| `utilization_bytes` | `Bytes` | 必 | move_flit | 累计统计 |

### Link 不变量

- 任意周期 `Σ(forward_pipe occupied) ≤ forward_latency_cycles`
- 一个 flit 进入 link 那一拍，credit 已经在上游 router 的 `output_credit[src.port][flit.assigned_vc]` 上扣减
- credit 真正回到上游 `output_credit` 的周期 = 下游 router 释放 buffer slot 的周期 + `return_latency_cycles`

## Endpoint / NI

`Endpoint` 是 workload 和网络的边界。对 AI NoC 特别重要：很多关键 stall 不在 router 里，在这里。

### Endpoint 字段

| 字段 | 类型 | 必/选 | 写入者 | 语义 |
|------|------|------|--------|------|
| `endpoint_id` | `NodeId` | 必 | 构造 | 通常等于 NodeId |
| `attached_router` | `(RouterId, PortId)` | 必 | 构造 | 接入的 router 和其 local port |
| `injection_queue` | `deque<Packet>` | 必 | generator / inject | 长度 ≤ `injection_depth` |
| `injection_credit[vc]` | `int[]` | 必 | accept_returning_credits | endpoint→router 的 credit |
| `current_injection_packet` | `PacketId` | 必 | inject | 当前正在拆 flit 的 packet；空 = 0 |
| `current_injection_flit_seq` | `uint16` | 必 | inject | 已经注入到第几个 flit |
| `ejection_queue` | `deque<Flit>` | 必 | accept_arriving_flits (local) | 长度 ≤ `ejection_depth` |
| `ejection_assembly[packet_id]` | `map<PacketId, Packet>` | 必 | consumer | 组装中的 packet（按 seq 收齐 flit）|
| `consumer_rate_flits_per_cycle` | `float` | 必 | 构造 | local consumer 处理速率 |
| `consumer_credit` | `int` | 必 | consumer / tick | 本地消费侧反压 |
| `pending_completion` | `list<PacketId>` | 必 | consumer | 已收齐 tail、等待标 COMPLETED 的 packet |

### Endpoint 不变量

- `injection_queue.size() ≤ injection_depth`；满则记 `INJECTION_BLOCKED`
- `current_injection_packet != 0` 时，必须把该 packet 的所有 flit 连续发完，再切下一个 packet（防止 packet 交错破坏 wormhole）
- `ejection_queue.size() ≤ ejection_depth`；满时下游 router 的 local port credit 不能回传，触发 `EJECTION_BLOCKED` 沿路传播
- `consumer_credit ≥ 0`；为 0 时 ejection 不消费

## Stats

统计对象最好也是一等结构，而不是边跑边打日志。Stats 不只是输出，也是**验证的对照面**。

### Stats 字段

| 字段 | 类型 | 语义 |
|------|------|------|
| `packet_latency_hist[class]` | `Histogram[TrafficClass]` | 按 class 分桶 |
| `packet_hop_count_hist` | `Histogram` | hop 分布 |
| `per_link_utilization[link_id]` | `float` | 链路占用率 |
| `per_link_bytes[link_id]` | `Bytes` | 累计字节 |
| `per_router_port_util[router][port]` | `float` | 端口占用率 |
| `per_router_vc_occupancy[router][port][vc]` | `float` | VC 平均占用 |
| `stall_cycles[reason]` | `uint64[StallReason]` | 各类 stall 累计 |
| `stall_cycles_by_class[class][reason]` | `uint64[][]` | 交叉表 |
| `per_endpoint_injection_blocked[node]` | `uint64` | 注入侧阻塞 |
| `per_endpoint_ejection_blocked[node]` | `uint64` | 弹出侧阻塞 |
| `workload_completion_cycle` | `Cycle` | 整个 workload 的 makespan |
| `per_class_throughput[class]` | `float` | flits/cycle |
| **verification 字段** | | |
| `credit_accounting[router][port][vc]` | `int` | 期望值与实际 `output_credit` 的差；任何时刻应为 0 |
| `flits_in_flight` | `int` | 已注入 - 已完成；workload 结束时应为 0 |
| `vc_holder_consistency_violations` | `uint64` | 每次发现 `output_vc_busy` 与 `output_vc_holder` 不一致就 +1 |
| `wormhole_path_violations` | `uint64` | 同 packet flit 走了不同路径的次数 |
| `tail_release_violations` | `uint64` | TAIL 离开后 VC 状态没被正确清空的次数 |

verification 字段在 release 模式可以关掉，但在 debug / 单测模式必须打开——它们是模型语义稳不稳的体温计。

## 跨结构不变量

下面几条横跨多个对象，是**第一版仿真器最该写成断言的核心规则**。仿真器每拍结束时全部检查通过，"规则正确性"这一关就过了。

1. **Credit 守恒**：对任意 `(router, port, vc)`，
   `output_credit[port][vc] + 占用 = buffer_depth`
   其中"占用 = 下游 input_vcs[port'][vc].queue.size() + Link.forward_pipe 中归属此 VC 的 flit 数 + Link.return_pipe 中归属此 VC 的 credit 数"。
2. **Wormhole 互斥**：对任意 `(router, output_port, output_vc)`，最多有一个 input VC 满足 `output_port==p ∧ output_vc==v ∧ vc_state ∈ {ACTIVE, BLOCKED_NO_CREDIT}`。
3. **VC 持有者一致**：`output_vc_busy[p][v] == true ⇒ output_vc_holder[p][v] ≠ (-1,-1)`，且 holder 指向的 input VC 当前确实持有此输出。
4. **Wormhole 同路径**：同 `packet_id` 的所有 flit 必须沿相同的 (router, output_port) 序列前进。检查方法：用 packet 表记录 HEADER 的实际路径，后续 flit 与之比对。
5. **Tail 释放**：TAIL 离开 input VC 的同一拍，必须有 `(input_vc.vc_state→IDLE, output_vc_busy[p][v]→false, output_vc_holder[p][v]→(-1,-1))`。
6. **Credit 不超发**：任何 `move_flit` 必须满足 `output_credit[p][v] > 0`，且执行后立即扣减；credit 回传只能在下游真正释放 buffer slot 之后调度。
7. **In-flight 闭合**：`workload_completion_cycle` 时刻，所有 Endpoint 的 `injection_queue`、`ejection_queue`、`ejection_assembly` 必须为空；所有 Link 的 `forward_pipe / return_pipe` 必须为空；`flits_in_flight == 0`。
8. **Packet 状态单调**：`PacketState` 转移必须满足前面给出的偏序，不能回退或跳跃。

## 推荐的枚举

最值得固定的是 `FlitType`、`TrafficClass`、`StallReason`、`VcState`、`PacketState`（见上）。越早固定枚举，后面的 trace、stats、case card 越容易保持一致。

## 一句话理解

第一版核心数据结构的任务，是把 wormhole、credit、endpoint 和统计边界都显式化，把每个字段的写入者、读者、不变量都钉死——而不是把一切塞进一个"大状态对象"里。

## 建模启示

实现时建议让：

- `Packet` 偏 workload 语义
- `Flit` 偏网络推进语义
- `InputVcState / Router` 偏资源占用语义
- `Endpoint` 偏边界与反压语义
- `Stats` 偏归因和验证语义

这五层分开、字段类型固定、不变量做成 assert，后续扩展最稳。下一步去 [Router Pipeline Pseudocode](./router-pipeline-pseudocode.md) 看这些字段是如何在每一拍被读写的，再去 [Verification And Calibration](./verification-and-calibration.md) 看这些不变量是如何在最小场景里被对照检验的。
