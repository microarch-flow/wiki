# NoC 与编译器的完整接口

上级：[Topology 与 Routing](./README.md)

相关：[Source Routing 与 Compiler-Driven NoC](./source-routing-compiler-driven-noc.md)、[从 NoC 知识到 DSL 设计](../06-reference/noc-to-dsl-bridge.md)、[地址空间与路由映射](../04-ai-dataflow-system/address-map-routing.md)、[从 Workload 到 Traffic Trace 操作手册](../05-modeling-evaluation/from-workload-to-traffic-trace.md)

## 读这页前先统一几个词

- `compiler`：这里指 AI 加速器的编译器，负责将模型映射到硬件上执行
- `hardware abstraction`：编译器看到的硬件描述，不是 RTL 细节，而是影响编译决策的关键参数
- `placement`：决定算子和数据放在哪些 tile/SRAM/HBM 上
- `routing`：决定数据在 NoC 中走哪条路径
- `scheduling`：决定通信事件的时序顺序和并发关系
- `cost model`：编译器用来评估不同方案优劣的量化模型

## 为什么需要这页

[Source Routing](./source-routing-compiler-driven-noc.md) 讲了编译器如何生成路由路径。[NoC→DSL bridge](../06-reference/noc-to-dsl-bridge.md) 讲了 DSL 的 5 层架构。但中间缺少一个关键环节：

**编译器到底需要 NoC/DSL 提供什么信息，才能做出好的 placement、routing 和 scheduling 决策？**

这页回答这个问题。它定义的是编译器与 NoC 硬件描述之间的接口契约。

## 编译器的三阶段决策

```text
Stage 1: Placement          Stage 2: Routing          Stage 3: Scheduling
"放在哪里"                   "走哪条路"                 "什么时候发"
                                                      
输入:                        输入:                     输入:
  计算图                       placement 结果            routing 结果
  硬件拓扑                     拓扑 + 链路参数            链路容量
  tile 能力                    路由约束                  依赖关系
  SRAM/HBM 容量                                        
                                                      
输出:                        输出:                     输出:
  算子 → tile 映射             每条流的路径               每个 packet 的注入时间
  数据 → SRAM/HBM 映射         header 编码               并发流的时序编排
  HBM channel 分配                                     DMA descriptor 序列
```

### 三个阶段对 NoC 信息的需求

| 阶段 | 需要知道什么 | 对应 DSL 层 |
|---|---|---|
| Placement | 拓扑图、tile 位置、tile 间距离（hop 数）、SRAM 容量、HBM port 位置 | L1 + tile 描述 |
| Routing | 拓扑连接、链路带宽、路由算法约束、死锁避免规则、VC 分配策略 | L1 + L2 + L3 |
| Scheduling | 链路容量、注入带宽、端口约束、traffic class 优先级 | L2 + L4 |

## 编译器需要的硬件抽象（Hardware Abstraction for Compiler）

### 1. 拓扑与距离信息

编译器做 placement 时，核心输入是一张带权图：

```text
编译器看到的拓扑抽象：

节点: {T0, T1, ..., T15, HBM0, HBM1, ..., HBM7}
边:   每条边标注 (hop_count, bandwidth, latency)

距离矩阵 D[i][j] = tile_i 到 tile_j 的最短 hop 数

示例（4×4 mesh，XY routing）：
     T0  T1  T2  T3  T4  T5  ...
T0 [  0   1   2   3   1   2  ... ]
T1 [  1   0   1   2   2   1  ... ]
T2 [  2   1   0   1   3   2  ... ]
...

编译器用 D[i][j] 作为 placement 的 cost function 的一部分：
  cost = Σ (data_volume[f] × D[src_f][dst_f]) for all flows f
```

**DSL 需要提供**：拓扑图 + 距离计算函数，或者直接导出距离矩阵。

### 2. 链路容量模型

编译器做 scheduling 时需要知道每条链路在每个时间窗口的可用带宽：

```text
链路容量模型：

  link(R_i, R_j):
    physical_bandwidth: 256 bit × 1 GHz = 32 GB/s
    effective_bandwidth: physical_bandwidth × (1 - overhead)
    overhead: header/flit 比例 + flow control 开销 ≈ 10-15%
    
  实际可用带宽 ≈ 27-29 GB/s

多流共享时：
  如果 N 条流共享一条链路，每条流的平均带宽 ≈ link_bw / N
  （round-robin 仲裁下近似均分）
```

**DSL 需要提供**：每条链路的物理带宽、VC 数量、仲裁策略。

### 3. 路由约束

编译器生成 source routing 路径时，必须遵守的硬约束：

```text
硬约束（违反 → 死锁或功能错误）：
  1. 路径必须从 src 到 dst 连通
  2. 路径不能违反死锁自由约束（如 XY routing 的 turn restriction）
  3. 同一 packet 的所有 flit 必须走同一路径（wormhole 约束）
  4. 使用的 VC 必须在路径上每个 router 都存在

软约束（违反 → 性能下降但功能正确）：
  1. 路径应尽量短（减少 hop 和延迟）
  2. 路径应避开已知热点链路
  3. 不同流应尽量分散到不同链路（load balance）
  4. 同一 pipeline stage 的多条流应避免共享瓶颈链路
```

**DSL 需要提供**：路由算法类型 + 合法 turn set + VC 到 traffic class 映射。

### 4. 端点约束

```text
每个 tile 的注入/弹出约束：

  tile T_i:
    max_injection_rate: 32 GB/s per network
    max_ejection_rate: 32 GB/s per network
    injection_ports: [data_noc: 1, control_noc: 1]
    ejection_ports: [data_noc: 1, control_noc: 1]
    
  约束：
    Σ injection_rate(flows from T_i) ≤ max_injection_rate
    Σ ejection_rate(flows to T_i) ≤ max_ejection_rate
```

**DSL 需要提供**：每个 tile 的端口配置和带宽上限。

## 编译器的 Cost Model

编译器在 placement 和 scheduling 中使用的 cost model，本质上是 NoC 性能的简化近似：

### Placement Cost Model

```text
placement_cost(mapping) = 
    α × communication_cost     # NoC 流量和距离
  + β × load_balance_cost      # tile 计算负载均衡
  + γ × memory_cost            # SRAM 容量利用

其中：
  communication_cost = Σ data_volume(f) × hop_count(src_f, dst_f)
                       for all flows f

  这是一个一阶近似——它假设 NoC 延迟和 hop 成正比，
  忽略了拥塞、仲裁竞争、链路共享等动态效应。
```

### Scheduling Cost Model

```text
scheduling_cost(schedule) =
    max_completion_time         # makespan
  + penalty × Σ link_overload  # 链路过载惩罚

其中：
  link_overload(l, t) = max(0, Σ flow_bw(f, t) - link_capacity(l))
                        for all flows f using link l at time t

  这比 placement cost 更精确，因为它考虑了时序重叠和链路竞争。
```

### Cost Model 的精度层次

| 精度 | 考虑什么 | 编译时间 | 适用阶段 |
|---|---|---|---|
| L0: hop-count | 距离 × 数据量 | μs | 粗粒度 placement 搜索 |
| L1: bandwidth-aware | 链路带宽约束 | ms | placement 精化 |
| L2: contention-aware | 多流共享链路的竞争 | 秒级 | scheduling |
| L3: cycle-approximate | 近似仿真 | 分钟级 | 最终验证 |

编译器通常在 L0-L1 做搜索，在 L2 做精化，在 L3 做最终验证。

**DSL 需要支持**：同一硬件描述，能被不同精度的 cost model 消费。

## 编译器 → NoC 的输出接口

编译器最终产生的 NoC 相关输出：

### DMA Descriptor

```text
DMA descriptor 是编译器告诉硬件"搬什么数据"的基本单元：

descriptor {
  src_addr: 0x1000_4000      # 源地址（HBM channel 0, offset 16KB）
  dst_addr: 0x0010_0000      # 目的地址（Tile 0 SRAM）
  length: 32768              # 32KB
  src_node: HBM_port_0       # NI decode 后的源节点
  dst_node: T0               # NI decode 后的目的节点
  network: data_noc           # 使用哪张网络
  traffic_class: weight_data  # 流量类别
  route_hint: [E, E, S, L]   # 可选：source routing 路径
  priority: medium
  depends_on: [desc_id_42]   # 依赖关系：等这个 descriptor 完成后才启动
}
```

### Tile Instruction 中的 NoC 操作

```text
tile instruction stream 中的 NoC 相关操作：

  SEND  dst=T5, size=8KB, channel=data_noc, route=[E,E,S,L]
  RECV  src=T3, size=8KB, channel=data_noc, buffer=sram_bank_2
  WAIT  barrier_id=7          # 等待所有参与者到达
  SYNC  group=[T0,T1,T2,T3]  # 组同步
```

## 完整的信息流

```text
DSL 硬件描述
     │
     ▼
┌──────────────────┐
│  Compiler Input  │ ← DSL 提供给编译器的信息
│  - 拓扑图         │
│  - 距离矩阵       │
│  - 链路带宽       │
│  - tile 参数      │
│  - address map   │
│  - 路由约束       │
│  - VC/QoS 策略   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Compiler      │
│  1. Placement    │ ← 用 L0-L1 cost model
│  2. Routing      │ ← 用 turn restriction + deadlock check
│  3. Scheduling   │ ← 用 L2 contention model
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Compiler Output  │ ← 编译器产出的 NoC 配置
│  - DMA desc.     │
│  - tile instrs   │
│  - route tables  │
│  - schedule      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ DSL L5 层描述     │ ← 可以回填到 DSL 做仿真验证
│  (schedule)      │
└──────────────────┘
```

## DSL 接口设计建议

### 编译器查询 API（DSL 应该支持的查询）

```yaml
compiler_interface:
  # 拓扑查询
  topology:
    - distance(src, dst) → hop_count
    - shortest_path(src, dst) → [node_list]
    - neighbors(node) → [node_list]
    - all_paths(src, dst, max_hops) → [[path], ...]
    
  # 容量查询
  capacity:
    - link_bandwidth(src_router, dst_router) → GB/s
    - injection_bandwidth(tile_id, network) → GB/s
    - ejection_bandwidth(tile_id, network) → GB/s
    - sram_capacity(tile_id) → bytes
    
  # 约束查询
  constraints:
    - legal_turns(routing_algorithm) → [(in_dir, out_dir), ...]
    - vc_for_class(traffic_class) → vc_id
    - deadlock_free(path, vc_assignment) → bool
    
  # 地址查询
  address:
    - resolve(addr) → (node_id, network)
    - hbm_channel(addr) → channel_id
    - region(node_id) → (base_addr, size)
```

### 编译器输出格式（DSL 应该能接收的格式）

```yaml
compiled_schedule:
  flows:
    - id: f0
      src: T0
      dst: T5
      size: 32 KB
      class: weight_data
      network: data_noc
      route: [E, E, S, Local]
      inject_cycle: 0
      
    - id: f1
      src: HBM_port_0
      dst: [T0, T1, T2, T3]     # multicast
      size: 128 KB
      class: activation_data
      network: data_noc
      inject_cycle: 100
      depends_on: [f0]
      
  barriers:
    - id: b0
      group: [T0, T1, T2, T3]
      after: [f0, f1]
      network: control_noc
```

## 本页结论

编译器与 NoC 的接口不是一个简单的参数传递，而是一套分层的信息契约：编译器需要拓扑距离做 placement，需要路由约束做 path generation，需要链路容量做 scheduling，需要 address map 做目标解析。DSL 的核心设计目标之一，是让这套信息能被编译器以不同精度层次查询和使用——从 μs 级的 hop-count 估算到分钟级的 cycle-approximate 验证。
