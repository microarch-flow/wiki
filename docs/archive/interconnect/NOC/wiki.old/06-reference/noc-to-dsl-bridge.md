# 从 NoC 知识到 DSL 设计

上级：[06 术语与检查清单](./README.md)

相关：[NoC 分类框架](../01-overview/taxonomy.md)、[Source Routing 与 Compiler-Driven NoC](../03-topology-routing/source-routing-compiler-driven-noc.md)、[多网络组织](../04-ai-dataflow-system/multi-network-organization.md)、[Simulator 设计规格](../05-modeling-evaluation/simulator-design-spec.md)

## 本页目标

将 wiki 中积累的 NoC 知识转化为 DSL 设计决策。回答三个问题：

1. DSL 需要描述 NoC 的哪些层次？
2. 哪些 NoC 概念应该成为 DSL 的一等公民？
3. DSL 应该在什么抽象层次上工作？

## DSL 需要描述的 5 个层次

```text
L5  Scheduled Communication    编译器产生的具体数据搬运事件
     ───────────────────────
L4  Traffic Specification      流量类型、通信模式、QoS
     ───────────────────────
L3  Routing Rules              合法路径、路由算法、死锁约束
     ───────────────────────
L2  Network Resources          VC、buffer、arbiter、pipeline 参数
     ───────────────────────
L1  Physical Topology           router、link、endpoint 的图结构
```

每层描述什么：

| 层 | 回答的问题 | 示例 |
|---|---|---|
| L1 Physical Topology | 谁和谁物理相连？ | 4×4 mesh, 256-bit link, 1ns/hop |
| L2 Network Resources | 网络有什么能力？ | 4 VC, 8-deep buffer, credit flow control |
| L3 Routing Rules | 从 A 到 B 能不能走、怎么走？ | XY routing, no deadlock |
| L4 Traffic Specification | 有哪些流量、什么特征？ | data class, control class, multicast group |
| L5 Scheduled Communication | workload 在具体 schedule 下怎么用网络？ | cycle 1200: tile_0 → tile_7, 4KB, data_noc |

### 为什么需要 5 层而不是 1 层

如果 DSL 只有一层（如 `topology: mesh`），无法表达：

- 同一 mesh 上跑不同 routing 算法的效果差异（需要 L3）
- 同一 routing 下不同 VC 配置的性能差异（需要 L2）
- 同一网络上 data 和 control 互相干扰的问题（需要 L4）
- 同一架构在 GEMM 和 MoE 下的表现差异（需要 L5）

5 层设计让你在**不改变底层硬件描述**的情况下，替换上层的 routing/traffic/schedule 来做对比实验。

## NoC 概念 → DSL 构造的映射表

### 一等公民（DSL 中的 struct / node）

这些概念必须在 DSL 中有对应的语法结构，因为它们是组成互连的基本单元：

| NoC 概念 | DSL 构造 | 为什么是一等公民 |
|---|---|---|
| Router | `router` node | 网络的基本交换单元 |
| Link | `link` edge | 连接 router 的物理通道 |
| Endpoint / Tile | `endpoint` node | 流量的源和汇 |
| Network | `network` container | 多网络设计需要独立描述每张网络 |
| Cluster | `cluster` group | 层次化设计的基本分组单位 |

### 参数（DSL 中的 attribute）

这些是 struct 的配置项，改变它们不会改变图结构：

| NoC 概念 | DSL attribute | 所属 struct | 典型值范围 |
|---|---|---|---|
| link_width | `width` | link | 64-512 bit |
| link_latency | `latency` | link | 1-3 cycle |
| buffer_depth | `buffer_depth` | router | 4-16 flit |
| vc_count | `vc_count` | router | 2-8 |
| routing_algorithm | `routing` | network | xy, source, adaptive |
| arbiter_policy | `arbiter` | router | round_robin, priority, age |
| flow_control | `flow_control` | network | credit, ready_valid |
| pipeline_stages | `pipeline` | link | 0-3 |

### 通信原语（DSL 中的 traffic primitive）

这些是描述 workload 通信行为的基本操作：

| 通信模式 | DSL primitive | 参数 |
|---|---|---|
| Point-to-point | `unicast` | src, dst, size, class |
| One-to-many | `multicast` | src, dst_group, size, replication_strategy |
| Many-to-one | `reduce` | src_group, dst, size, op, strategy |
| Many-to-many | `all_to_all` | group, size, class |
| Pipeline forwarding | `stream` | src, dst, bandwidth, channel |
| Synchronization | `barrier` | group, class |
| DMA transfer | `dma_transfer` | src_mem, dst_mem, size, route |

## DSL 抽象层次选择

同一架构可以在不同精度下评估。DSL 应该支持描述同一硬件，然后由不同精度的 evaluator 来分析：

### Level 0: Analytical（公式驱动）

```yaml
# DSL 描述不变，evaluator 用公式计算
evaluate:
  mode: analytical
  metrics:
    avg_hop: (R + C) / 3
    bisection_bw: min(R, C) * link_width
    theoretical_throughput: bisection_bw / avg_traffic_load
```

适合：快速筛选候选拓扑，<1 秒出结果。

局限：不考虑 contention、buffer、arbitration。

### Level 1: Cycle-Approximate（简化 pipeline）

```yaml
evaluate:
  mode: cycle_approximate
  simplifications:
    - router_delay: fixed 1 cycle
    - no_vc_arbitration
    - infinite_buffer
```

适合：topology + placement 联合探索，秒级出结果。

局限：低估拥塞、不暴露死锁。

### Level 2: Cycle-Accurate（完整 router pipeline）

```yaml
evaluate:
  mode: cycle_accurate
  router_pipeline: [RC, VA, SA, ST, LT]
  flow_control: credit
  vc_count: 4
  buffer_depth: 8
```

适合：bottleneck 诊断、参数调优，分钟级出结果。

局限：仿真时间较长，不适合大规模 sweep。

### 推荐工作流

```text
L0 Analytical → 筛选 3-5 个候选拓扑
  ↓
L1 Cycle-Approximate → 对比候选的 placement 敏感度
  ↓
L2 Cycle-Accurate → 对最优候选做 bottleneck 诊断和参数调优
```

## 现有 NoC 配置语言参考

### BookSim 配置格式

```text
topology = mesh;
k = 4;                    // 4×4
n = 2;                    // 2D
routing_function = dim_order;
num_vcs = 4;
vc_buf_size = 8;
wait_for_tail_credit = 0;
traffic = uniform;
injection_rate = 0.1;
```

优点：简洁，参数化。

局限：
- 只能描述规则拓扑（mesh/torus/fly 等），不支持 irregular
- 不支持多网络
- 不支持 multicast/reduce 等 collective 原语
- traffic 只能从内置模式选择，不能描述 workload-specific 流量

### Garnet (gem5) 配置

```python
network = GarnetNetwork()
network.num_rows = 4
network.vcs_per_vnet = 4
network.ni_flit_size = 16
network.routing_algorithm = 0  # XY
```

优点：与 gem5 全系统仿真集成。

局限：
- 配置不是独立的 DSL，绑定在 gem5 Python 中
- 拓扑通过 Python 脚本生成，不是声明式
- 不支持 AI workload 特有的 traffic pattern
- 不支持多物理网络（只有 virtual network）

### 你的 DSL 可以做得更好的地方

| 维度 | BookSim / Garnet | 你的 DSL 目标 |
|---|---|---|
| 拓扑描述 | 只支持规则拓扑 | 支持规则 + irregular + hierarchical |
| 多网络 | 不支持 / 仅 virtual | 支持多物理网络 + overlay |
| 通信原语 | 只有 unicast | 支持 multicast、reduce、stream、barrier |
| Traffic 描述 | 内置 synthetic | 支持 workload trace + synthetic + 混合 |
| 抽象层次 | 单一（cycle-accurate） | 支持 analytical / approximate / accurate |
| 与编译器的接口 | 无 | 支持 placement + routing + schedule |

## 一个完整的 DSL 描述示例

描述一个 4×4 concentrated mesh + control ring + reduction tree 的 AI 加速器互连：

```yaml
# ============================================================
# L1: Physical Topology
# ============================================================
accelerator:
  name: example_npu_16tile
  tile_count: 16
  cluster_size: 4        # 每 4 tile 一个 cluster
  cluster_count: 4

clusters:
  - id: C0
    tiles: [T0, T1, T2, T3]
    local_interconnect:
      type: crossbar
      ports: 4
      arbiter: round_robin
      latency: 1

  - id: C1
    tiles: [T4, T5, T6, T7]
    local_interconnect:
      type: crossbar
      ports: 4
      arbiter: round_robin
      latency: 1

  # C2, C3 类似...

networks:
  # --- Data NoC: concentrated 2×2 mesh ---
  - name: data_noc
    type: concentrated_mesh
    rows: 2
    cols: 2
    concentration: 4      # 每 router 接 4 tile（= 1 cluster）
    link:
      width: 256           # bit
      latency: 1           # cycle
      pipeline_stages: 0
    router:
      radix: 8             # 4 mesh + 4 local
      vc_count: 4
      buffer_depth: 8
      arbiter: round_robin
      flow_control: credit
      pipeline: [RC, VA, SA, ST, LT]

  # --- Control NoC: ring ---
  - name: control_noc
    type: ring
    direction: bidirectional
    nodes: 4               # 每 cluster 一个节点
    link:
      width: 64
      latency: 1
    router:
      vc_count: 2
      buffer_depth: 4
      arbiter: fixed_priority

  # --- Reduction overlay: binary tree ---
  - name: reduce_tree
    type: binary_tree
    leaves: 4              # 每 cluster 一个 leaf
    in_network_op: fp16_add
    link:
      width: 256
      latency: 1

# ============================================================
# L2: Network Resources (已嵌入 network 定义中)
# ============================================================

# ============================================================
# L3: Routing Rules
# ============================================================
routing:
  data_noc:
    algorithm: xy
    deadlock_freedom: dimension_order
  control_noc:
    algorithm: shortest_path
  reduce_tree:
    algorithm: up_down     # leaf → root (reduce), root → leaf (broadcast)

# ============================================================
# L4: Traffic Specification
# ============================================================
traffic_classes:
  - name: weight_data
    network: data_noc
    vc: 2
    priority: medium
  - name: activation_data
    network: data_noc
    vc: 2
    priority: medium
  - name: control
    network: control_noc
    vc: 0
    priority: high
  - name: partial_sum
    network: reduce_tree
    priority: medium
  - name: barrier
    network: control_noc
    vc: 1
    priority: highest

# ============================================================
# L5: Scheduled Communication (workload-specific)
# ============================================================
schedule:
  - cycle: 0
    event:
      kind: dma_transfer
      src: HBM_port_0
      dst: [T0, T1, T2, T3]
      size: 128KB
      class: weight_data
      network: data_noc
      multicast: tree

  - cycle: 100
    event:
      kind: multicast
      src: HBM_port_0
      dst_group: [T0, T4, T8, T12]   # column 0
      size: 32KB
      class: activation_data
      network: data_noc

  - cycle: 500
    event:
      kind: reduce
      src_group: [T0, T4, T8, T12]
      dst: T0
      size: 32KB
      op: fp16_add
      class: partial_sum
      network: reduce_tree
      strategy: in_network

  - cycle: 600
    event:
      kind: barrier
      group: [C0, C1, C2, C3]
      class: barrier
      network: control_noc
```

### 这个示例展示了什么

| 特性 | 体现在哪里 |
|---|---|
| 多网络 | data_noc + control_noc + reduce_tree 三张独立网络 |
| 层次化 | cluster 内 crossbar + cluster 间 mesh |
| 多种通信原语 | unicast (dma)、multicast、reduce、barrier |
| Traffic class 隔离 | 不同 class 走不同网络/VC/priority |
| 编译器调度 | schedule 中的 cycle-level 事件 |
| 声明式 | 描述"是什么"而不是"怎么仿真" |

## 从 DSL 到评估的完整流程

```text
DSL 描述 (YAML)
     │
     ▼
Parser → 构建内部数据结构
     │
     ├──→ Analytical Evaluator → 快速估算指标
     │
     ├──→ Cycle-Approximate Simulator → 中等精度仿真
     │
     └──→ Cycle-Accurate Simulator → 精确仿真
              │
              ▼
         Performance Report
         - per-link utilization
         - per-flow latency
         - stall breakdown
         - bottleneck identification
```

## 设计 DSL 时最容易犯的错误

| 错误 | 后果 | 正确做法 |
|---|---|---|
| 只描述 topology，不描述 traffic | 无法做 workload-driven 评估 | L1-L5 都要覆盖 |
| 把所有流量塞进一张网络 | 低估 control 延迟和 traffic 干扰 | 支持多网络 |
| 只支持 unicast | 无法描述 AI workload 的 broadcast/reduce | 加入 collective 原语 |
| DSL 绑定特定 simulator | 无法切换评估精度 | DSL 只描述硬件和 workload，评估器独立 |
| 不支持 cluster / hierarchy | 无法描述真实 AI 加速器的层次化设计 | cluster 是一等公民 |

## 本页结论

DSL 设计的核心是将 NoC 知识分层组织成 5 个正交的描述层次（topology → resources → routing → traffic → schedule），使得同一硬件描述可以在不同 workload 和不同评估精度下复用。与 BookSim/Garnet 相比，面向 AI 加速器的 DSL 最关键的差异是：支持多网络、支持 collective 通信原语、支持层次化 cluster 描述、支持与编译器的调度接口。
