# From Workload To Traffic Trace

上级：[07 Evaluation Methodology](./README.md)

相关：[Traffic Patterns And Characterization](../05-system-integration/traffic-patterns-and-characterization.md)、[Compiler NOC Co Design](../06-ai-noc-specifics/compiler-noc-co-design.md)、[Reduction And Collective Networks](../06-ai-noc-specifics/reduction-and-collective-networks.md)、[Core Data Structures](../08-simulator-construction/core-data-structures.md)

## 这页在回答什么问题

这页回答：真实 workload 怎样一步步变成 simulator 能消费的 traffic trace，以及中间哪些信息绝对不能丢；并对 GEMM、Attention、AllReduce 三个最常见的 AI workload 各给一个**完整、可执行**的转换案例与 trace schema 实例。

读完应能直接照案例为新 workload 写转换脚本，而不是只看到一个流程图。

## 核心原则

trace 的目标不是复刻完整软件栈，而是保住最影响 NoC 结论的结构信息。

最关键的通常是五件事：

- 谁和谁通信
- 什么时候通信
- 通信多大
- 属于什么 traffic class
- 它被放在硬件的什么位置

如果这五项保住了，第一版 trace 通常就已经进入有效区间。

## 推荐转换流程

一个稳定的流程通常是：

1. 定义 workload 计算图
2. 定义 mapping / placement
3. 定义 memory placement
4. 提取通信事件
5. 事件转 packet / flow
6. flow 转 trace

NoC 压力不是 workload 天生自带的，而是在 workload 遇到具体硬件布局之后才真正出现。所以前 3 步**不画完，后 3 步就无法开始**。

## Step 1: 先定计算骨架

先不要急着拆 packet。先把最小有意义的计算对象和依赖列出来，例如：

- operator sequence
- producer-consumer relation
- stage boundary
- synchronization point

这样后面才能判断哪些通信处在关键路径上。

## Step 2: 再定 placement

没有 placement，就没有真实的：

- hop
- hotspot
- cluster boundary
- cross-die path

同一个逻辑 workload，在不同 placement 下会变成完全不同的 NoC 问题。

## Step 3: memory placement 单独处理

至少要明确：

- weight 放哪里
- activation / scratchpad 放哪里
- KV cache 放哪里
- HBM channel / SRAM cluster 如何映射

很多 NoC 结论实际上首先由 memory placement 决定，而不是由 routing 决定。

## Step 4: 提取通信事件

这一步要把计算关系翻译成 NoC 语义对象。常见类型包括：

- read request
- read response
- write / writeback
- tile-to-tile stream
- multicast / broadcast
- gather / reduce
- barrier / control / completion

最重要的是尽早固定一套 canonical traffic class，否则后面 simulator 和实验模板会不断漂移。

## Step 5: 事件转 flow / packet

第一版最实用的抽象通常不是 bit-accurate packet，而是一个 flow 记录：

- `src`
- `dst`
- `traffic_class`
- `bytes`
- `release_time`
- `dependency`

如果是 collective，再转成：

- one-to-many
- many-to-one
- many-to-many

即可。

## Step 6: flow 转 trace

最终 trace 不一定一开始就要 cycle-perfect。可以先有两级：

- event trace
- packet / flit trace

event trace 适合更快的上层探索；packet / flit trace 适合更细粒度模拟。

## 最小 schema（v1）

为了后面三个案例能直接挂上去，先固定 v1 schema：

```json
// event-level flow record
{
  "flow_id":         "uint32",
  "src_node":        "NodeId",
  "dst_node":        "NodeId",          // 或 dst_set[] 用于 multicast
  "traffic_class":   "CONTROL|MEMORY_REQUEST|MEMORY_RESPONSE|STREAM|BULK_DMA",
  "bytes":           "uint32",
  "release_time":    "cycle",           // 依赖满足后最早可注入
  "depends_on":      ["flow_id", ...],  // workload DAG 上游
  "phase":           "string",          // 调试/聚合用，例如 "layer3.attn.qk"
  "placement_ctx":   { "stage": "...", "tile_role": "..." }
}
```

packetize 时附加：

```json
{
  "packet_id":   "uint64",
  "flow_id":     "uint32",
  "num_flits":   "uint16",
  "release_time":"cycle",
  "route_hint":  ["port_id", ...]    // 可选，source routing
}
```

字段对应 [Core Data Structures](../08-simulator-construction/core-data-structures.md) 里的 `Packet / Flit` 必填项，trace 生成器可以直接调 `build_packet(flow, seq)` 把 flow 拆 flit。

---

## 案例 A：GEMM 在 4×4 mesh 上的 trace 生成

**workload**：`C[M,N] = A[M,K] · B[K,N]`，`M=N=K=4096`，bf16（2 字节）。

### Step 1：计算骨架

按 `Tm × Tn × Tk` 分块，取 `Tm=Tn=Tk=1024`，每个 tile 计算 `[1024,1024] = [1024,1024]·[1024,1024]`。计算图：

```
for i in 0..M/Tm:   # 4 个外层
  for j in 0..N/Tn: # 4 个外层
    C_ij = 0
    for k in 0..K/Tk: # 4 个 reduce step
      C_ij += A_ik · B_kj
```

外层 `(i,j)` 完全独立。reduce 维度 `k` 串行（accumulate）。共 64 个 GEMM tile（4×4×4），每个有 4 步 reduce。

### Step 2：mapping / placement

4×4 mesh 共 16 个 tile。把 `(i,j)` 二维外层一一映射到 mesh 上的 tile`(i,j)`，每个物理 tile 负责一个输出 block `C_ij`，串行扫 4 个 reduce step。

### Step 3：memory placement

- `A` 切成 4 行带（`A_0*..A_3*`），分别放在 row buffer：`A_i*` 放在第 i 行的 leftmost HBM channel（`(i, 0)` tile 旁）
- `B` 切成 4 列带（`B_*j`），放在 column buffer：`B_*j` 放在第 j 列的 topmost HBM channel（`(0, j)` tile 旁）
- `C` 写回 row buffer，与 `A` 同侧

这是 GEMM 最经典的 row-broadcast + column-broadcast placement。

### Step 4：通信事件提取

对每个 tile `(i,j)`、每个 reduce step `k`：

| 事件 | 类型 | src | dst | bytes |
|------|------|-----|-----|-------|
| 读 `A_ik` | MEMORY_REQUEST | `(i,j)` | `(i,0)` HBM | 32（请求头）|
| `A_ik` 数据回传 | MEMORY_RESPONSE | `(i,0)` HBM | `(i,j)` | `Tm·Tk·2 = 2 MB` |
| 读 `B_kj` | MEMORY_REQUEST | `(i,j)` | `(0,j)` HBM | 32 |
| `B_kj` 数据回传 | MEMORY_RESPONSE | `(0,j)` HBM | `(i,j)` | `Tk·Tn·2 = 2 MB` |
| 写回 `C_ij`（最后一步）| BULK_DMA | `(i,j)` | `(i,0)` HBM | `Tm·Tn·2 = 2 MB` |

**关键优化**：`A_ik` 在行内 4 个 tile `(i, *)` **共用**——一次读、行广播给该行全部目的 tile，节 4 倍带宽。同理 `B_kj` 列广播。这是把"多 unicast"折成"multicast"的关键决策；trace 上体现为：

| 事件 | 类型 | src | dst_set | bytes |
|------|------|-----|---------|-------|
| `A_ik` 行广播 | STREAM (multicast) | `(i,0)` HBM | `[(i,0),(i,1),(i,2),(i,3)]` | 2 MB |
| `B_kj` 列广播 | STREAM (multicast) | `(0,j)` HBM | `[(0,j),(1,j),(2,j),(3,j)]` | 2 MB |

### Step 5：事件转 flow

每步 reduce 产生 8 个 flow（A 行广播 ×4 + B 列广播 ×4）。`depends_on` 串起 reduce 链：

```
flow_A[k] depends on compute_done[k-1]
flow_B[k] depends on compute_done[k-1]
compute[k] depends on flow_A[k] AND flow_B[k]
flow_C (writeback) depends on compute[K-1]
```

`release_time` 第一波 = 0，之后由 dependency 推导。

### Step 6：trace schema 实例

```json
[
  {
    "flow_id": 1, "src_node": 0, "dst_node": [0,1,2,3],
    "traffic_class": "STREAM", "bytes": 2097152,
    "release_time": 0, "depends_on": [],
    "phase": "gemm.k0.A_row0",
    "placement_ctx": {"tile_role": "row_broadcast_src", "row": 0}
  },
  {
    "flow_id": 2, "src_node": 0, "dst_node": [0,4,8,12],
    "traffic_class": "STREAM", "bytes": 2097152,
    "release_time": 0, "depends_on": [],
    "phase": "gemm.k0.B_col0",
    "placement_ctx": {"tile_role": "col_broadcast_src", "col": 0}
  },
  // ... 共 8 flows × 4 reduce steps × 16 tiles = 512 flows 第一波
  // 加 16 个 writeback flow
]
```

### Step 7：sanity check

写完应能立刻手算一组指标：

| 指标 | 估算 | 用途 |
|------|------|------|
| 总 NoC 字节 | `4 reduce × 2 multicast × 2 MB × (4 tile bcast 平均扩 ≈ 3)` ≈ 48 MB | 与 simulator 输出比 |
| 每 reduce step 关键路径 | 2 MB / `B_per_link` + multicast tree depth · α | 与 simulator 测出的 phase latency 比 |
| Hottest link | 行 broadcast 的第一跳（`(i,0)→(i,1)`），4 个 multicast 同时穿过 | sweep validation |

任一项偏离手算 > 30% 就要回查 placement 或 multicast 实现是否退化成 N 次 unicast。

---

## 案例 B：Attention prefill 在 2×4 array 上的 trace

**workload**：Transformer attention，`Q,K,V ∈ [seq=2048, head_dim=128]`，单 head，bf16。

### Step 1：计算骨架

prefill 阶段三个串行算子：

```
S = Q · K^T       # [seq, seq]
P = softmax(S)    # 行内归一化
O = P · V         # [seq, head_dim]
```

`Q·K^T` 和 `P·V` 都是 GEMM 形态，按 row blocking 切：行被切成 8 个块，每块 256 行。

### Step 2：mapping

2×4 = 8 个 tile，每个 tile 负责一行块（256×... 的输出）。

### Step 3：memory placement

- `K, V` 完整副本 staged 在共享 SRAM cluster（左侧两列 tile 旁）——所有 tile 都要读
- `Q` 按行切分别 staged 到对应 tile 本地 SRAM
- `O` 写回各 tile 本地 SRAM

### Step 4：通信事件提取

每个 tile `t`：

| 阶段 | 事件 | 类型 | src | dst | bytes |
|------|------|------|-----|-----|-------|
| QK | 读自己的 `Q_t` | MEMORY_REQUEST/RESP | 本 tile→本地 SRAM | -（本地）| 0 |
| QK | 读全 K | STREAM (broadcast) | K_SRAM | 全部 8 tile | `2048·128·2 = 512 KB` |
| softmax | row-local | -（无 NoC）| - | - | 0 |
| PV | 读全 V | STREAM (broadcast) | V_SRAM | 全部 8 tile | `512 KB` |
| writeback | 写 O_t | BULK_DMA | 本 tile | 本地 SRAM | 0 |

注意：`K` 和 `V` 都是**全员广播**——所有 8 tile 都需要全份。这是 prefill 的标志性 NoC 模式：少量大块广播 + 大量本地计算。

### Step 5：事件转 flow

只有两个广播 flow：

```json
[
  {
    "flow_id": 1, "src_node": "K_SRAM_node",
    "dst_node": [0,1,2,3,4,5,6,7],
    "traffic_class": "STREAM", "bytes": 524288,
    "release_time": 0, "depends_on": [],
    "phase": "attn.prefill.K_bcast",
    "placement_ctx": {"op": "QK"}
  },
  {
    "flow_id": 2, "src_node": "V_SRAM_node",
    "dst_node": [0,1,2,3,4,5,6,7],
    "traffic_class": "STREAM", "bytes": 524288,
    "release_time": "after_phase_QK_compute",
    "depends_on": [1, "compute_QK"],
    "phase": "attn.prefill.V_bcast",
    "placement_ctx": {"op": "PV"}
  }
]
```

### Step 7：sanity check

| 指标 | 估算 |
|------|------|
| 总 NoC 字节 | 2 × 512 KB = 1 MB |
| 关键路径 | 512 KB / `B_link` + multicast depth · α，重复两次 |
| Hottest link | K_SRAM / V_SRAM 第一跳（multicast tree 根边）|

prefill 是 broadcast 主导，与下面 decode（request/response 主导）形成强烈对比。

---

## 案例 C：AllReduce on 8 端点 ring

**workload**：DDP 训练每 step 末尾的 gradient AllReduce，参数量 `M = 100 MB`，`N=8` 端点。

### Step 1：计算骨架

每个端点 `i` 持有 `M_i = 100 MB` 的局部梯度，需所有端点最终各自得到 `Σ M_i / N`。

### Step 2：mapping + 算法选择

8 个端点排成物理 ring（mesh 上的边界一圈，或 dragonfly 的一组）。选 ring-based AllReduce（详见 [reduction-and-collective-networks.md](../06-ai-noc-specifics/reduction-and-collective-networks.md#ring-allreduce-的代价)），分两阶段：

- scatter-reduce：N-1=7 步，每步发 `M/N = 12.5 MB`
- all-gather：N-1=7 步，每步发 `M/N = 12.5 MB`

### Step 3：memory placement

每个端点本地 SRAM 存 100 MB（或分段流式）。

### Step 4：通信事件提取

每个端点 `i` 在每个 step `s` 发送一块给下游 `(i+1) mod N`：

| Step 类型 | flow 数 | 每 flow bytes | dst | dependency |
|-----------|---------|---------------|-----|------------|
| scatter-reduce s=0..6 | N=8 (每端点一条) | 12.5 MB | `(i+1) mod N` | `s-1` 的 receive 完成 |
| all-gather s=0..6 | N=8 | 12.5 MB | `(i+1) mod N` | scatter-reduce 全部完成 |

总 flow 数 = 8 × 14 = 112。

### Step 5：trace schema 实例（取前 3 个）

```json
[
  {
    "flow_id": 1, "src_node": 0, "dst_node": 1,
    "traffic_class": "BULK_DMA", "bytes": 13107200,
    "release_time": 0, "depends_on": [],
    "phase": "allreduce.sr.step0",
    "placement_ctx": {"phase_idx": 0, "kind": "scatter_reduce"}
  },
  {
    "flow_id": 2, "src_node": 1, "dst_node": 2,
    "traffic_class": "BULK_DMA", "bytes": 13107200,
    "release_time": 0, "depends_on": [],
    "phase": "allreduce.sr.step0",
    "placement_ctx": {"phase_idx": 0, "kind": "scatter_reduce"}
  },
  {
    "flow_id": 9, "src_node": 0, "dst_node": 1,
    "traffic_class": "BULK_DMA", "bytes": 13107200,
    "release_time": "after_flow_8_complete",
    "depends_on": [8],
    "phase": "allreduce.sr.step1",
    "placement_ctx": {"phase_idx": 1, "kind": "scatter_reduce"}
  }
  // ...
]
```

### Step 7：sanity check

代入公式（`α=10`, `B=64 GB/s = 64 B/cyc @ 1 GHz`）：

```
T_ring ≈ 2(N-1)·α + 2·M/B = 14·10 + 2·100MB/(64B/cyc)
       = 140 + 3.28M cycles ≈ 3.28 ms @ 1 GHz
```

simulator 输出的 makespan 与此偏离 > 15% 就要查：
- ring 是不是被某条 link 卡成了串行（拓扑实际不是干净 ring）
- 端点 ejection 是否成了瓶颈
- traffic class 是否被其他流量挤占

---

## 三个案例的对比

| workload | 主导模式 | trace 总字节 | flow 数 | 热点 |
|----------|---------|--------------|---------|------|
| GEMM | row/col multicast | ~48 MB | ~500 | broadcast 树根边 |
| Attention prefill | full broadcast | ~1 MB | 2 | broadcast 树根边 |
| AllReduce | ring point-to-point | ~1.4 GB | ~112 | 无（结构性均匀） |

可以看到：**同一个"AI workload"标签下，trace 形态差异极大**。trace 生成器必须按 workload 走对应路径，不能用一个 generic generator 套全部。

## workload-specific 提示

- **GEMM**：先提取 broadcast、forwarding、gather/reduce；reduce 维度成串行依赖
- **prefill**：先提取 bulk movement 和 HBM 注入热点；少量大 flow
- **decode**：务必保留 request/response 与 dependency chain；KV cache 读模式是 fan-in 热点
- **MoE**：务必保留 expert skew 与 many-to-many 结构；router→expert 是 all-to-all 退化
- **AllReduce / AllGather**：用 [collective 算法表](../06-ai-noc-specifics/reduction-and-collective-networks.md#三种方案对比) 先选算法，再展开为 flow 序列

## 第一版可以先忽略什么

通常可以先忽略：

- payload bit pattern
- 完整 runtime bookkeeping
- 非关键路径的细碎 metadata
- 过细地址编码

因为你的目标是架构洞察，不是协议复刻。

## trace 生成器的契约

trace 生成器和 simulator 之间最好有明确契约：

```text
TraceGeneratorContract {
  schema_version          := v1
  traffic_class_enum     := { CONTROL, MEMORY_REQUEST, MEMORY_RESPONSE, STREAM, BULK_DMA }
  placement_ctx_keys     := { stage, tile_role, row, col, op, phase_idx, kind, ... }
  multicast_representation := "single_flow_with_dst_set" | "fanout_to_unicasts"
  dependency_semantics   := "all_of" | "any_of"
  simplification_list    := ["no_coherence", "no_partial_credit", ...]
}
```

固定后即可作为可复现实验资产，而不是一次性脚本产物。换 workload、换 placement、换算法时**只改 generator 的输入参数**，simulator 与对照基线无需重新对齐。

## 一句话理解

从 workload 到 trace 的关键，不是"越细越真"，而是**把 placement、memory placement、依赖图、collective 算法**这四样真正决定 NoC 结论的结构信息显式留下来；trace 文件只是这四样的投影。

## 建模启示

每写完一份 trace，立刻做三件事：

1. **手算一个总字节数**，与 simulator stats 的 `Σ link_bytes` 对照（差 > 20% 多半是 multicast 退化或漏 dependency）
2. **手算关键路径长度**（最长依赖链 × 每步用时），与 makespan 对照
3. **预测热点链路**，与 simulator 的 `per_link_utilization` top-3 对照

这三步是最便宜的 trace 正确性检查，比把 simulator 跑通后再回头 debug 省 10 倍时间。trace 生成、simulator 实现、case card 三者之间的 schema 必须**一字不差**——否则任何一方改动都会让另一方的结果偷偷失效。
