# Source Routing 与 Compiler-Driven NoC

上级：[Topology 与 Routing](./README.md)

相关：[Routing 与 Arbitration](./routing-arbitration.md)、[流量模式](../04-ai-dataflow-system/traffic-patterns.md)

## 读这页前先统一几个词

- `source routing`：路径由源端预先决定，packet header 里带着“该怎么走”
- `runtime`：介于编译器和硬件之间的执行时软件层，负责按当前任务状态发起或协调传输
- `placement`：把逻辑任务或数据块放到哪些 tile / cluster 上
- `segment`：一段路径编码，表示 packet 先按这段规则走，再进入下一段
- `plane`：相互隔离的一组链路或逻辑网络平面；常用于把不同流量分开跑，避免互相干扰

## 为什么这个主题对 AI NoC 特别重要

在 CPU coherent NoC（缓存一致性片上网络）里，很多流量是动态产生、动态分叉的。  
但在 AI tile dataflow（数据流）架构里，很多主流量其实来自：

- 已知的算子切分
- 已知的 tile（计算单元）placement（放置）
- 已知的 producer-consumer（生产者-消费者）关系
- 已知的 DMA（直接内存访问）搬运计划

这意味着路径并不一定要在每个 router 局部决定，完全可以在编译器或 runtime 侧预先规划。

## 什么是 source routing

source routing（源路由）的核心思想是：

- 路径在源端或软件侧预先计算
- packet（数据包）header（包头）携带路径信息
- 中间 router（路由器）只按 header 指示做转发

它和普通 deterministic routing（确定性路由）的主要区别，不是”简单或复杂”，而是谁掌握路径选择权。

## Source routing 的三种常见形式

### 1. 显式逐跳编码

header 直接带每一跳该走哪个方向。

优点：

- router 最简单
- 路径完全可控

缺点：

- header 开销较大
- 长路径编码成本更高

### 2. 分段路径编码

header 记录几个关键转向点或 segment。

优点：

- header 开销较低
- 仍保留较强路径控制能力

缺点：

- router 逻辑比显式逐跳稍复杂

### 3. 编译器约束下的半静态 routing

软件决定大路径，router 只在局部按简单规则完成剩余部分。

优点：

- 平衡软件可控性与硬件复杂度

缺点：

- 软件与硬件边界更难定义清楚

## 为什么它适合 AI tile dataflow

### 流量更规整

GEMM（通用矩阵乘法）、attention pipeline（注意力流水线）、固定 tile graph 往往具有可预测通信模式。

### 更容易和 placement 联动

编译器既然知道算子放在哪里，就能直接知道通信跨多少 hop（跳）、哪些链路是热点。

### 更容易做通路预留与隔离

对固定主数据流，可以提前规划：

- 哪些 packet 走哪条路径
- 哪些流量必须避开控制面
- 哪些流量应落在单独 plane / VC（虚拟通道）上

但要注意，`路径可预先规划` 不等于 `路径集合天然可落地`。  
如果静态路径集形成 channel dependency（信道依赖）环，source routing 一样会 deadlock（死锁）。

## 它不能自动解决什么

source routing 不是万能药，它不能自动解决：

- destination ejection（目的端弹出，数据包从网络到达目标节点的过程）堵塞
- credit（信用计数，用于流控的下游缓冲区空位计数）不足
- request / response 资源环
- 多流量动态叠加产生的新热点

也就是说，路径可控不等于系统无拥塞。

## Source routing 与 adaptive routing 的边界

对 AI NoC，一个很实用的思路是：

- 主数据流走 source routing 或强 deterministic routing
- 动态流量、异常流量或 background traffic（背景流量）再考虑局部 adaptive

这比“全网都做 adaptive”通常更可控。

## 编译器真正要做什么

如果你想让 source routing 真正有价值，编译器至少要提供：

- tile placement
- tensor / stream 到 tile graph 的映射
- DMA 计划
- 路径冲突感知
- deadlock-free path set（无死锁路径集）检查
- 通信与计算重叠计划

也就是说，source routing 落地前，必须检查静态路径集是否形成 channel dependency 环；若会成环，就要通过分离 VC、turn restriction 或 escape VC 保证无死锁。

换句话说，source routing 不是单独的 header 设计问题，而是编译器和 NoC 的接口设计问题。

## 架构探索里应该怎么建模

第一版可以先这样做：

- 为每个 flow 预先生成固定路径
- packet header 只记录 dst（目的地址）和 route id
- simulator（仿真器）用 route id 查表得到 hop 序列
- 统计不同 flow 在同一路径段上的重叠情况
<<<<<<< HEAD

这样不必一开始就实现复杂 header bit-encoding，也能评估 source routing 的架构价值。

## 你至少应该比较的三件事

- source routing vs XY routing（先X轴再Y轴的维序路由）的热点分布差异
- 固定 placement 下，静态路径是否会放大某些链路压力
- 当流量模式变化时，source routing 的鲁棒性是否下降

## 常见误区

- 认为 source routing 等于不需要仲裁
- 认为 source routing 等于不需要 VC
- 认为只要路径静态就不会 deadlock（死锁）

实际情况是：

- 同一路径上的共享链路仍然要竞争
- traffic class（流量类别）隔离仍然需要
- 静态路径一样可能形成资源依赖环（导致 deadlock）

## Header 编码格式详解

### 形式一：Per-hop Direction Encoding

每一跳用 3 bit 编码方向：

```text
Direction Code:
  000 = North
  001 = South
  010 = East
  011 = West
  100 = Local (eject)

Header layout (4×4 mesh, 最长路径 6 hop):
┌──────────┬──────┬──────┬──────┬──────┬──────┬──────┬─────────┐
│ dst_addr │ hop0 │ hop1 │ hop2 │ hop3 │ hop4 │ hop5 │ payload │
│  4 bit   │ 3b   │ 3b   │ 3b   │ 3b   │ 3b   │ 3b   │  ...    │
└──────────┴──────┴──────┴──────┴──────┴──────┴──────┴─────────┘
路由字段总开销: 6 × 3 = 18 bit

示例: (0,0) → (3,2), XY routing
  hop0=East, hop1=East, hop2=East, hop3=South, hop4=South, hop5=Local
  编码: 010 010 010 001 001 100
```

Router 行为：读取当前 hop 字段 → 输出到对应端口 → 移位或递增 hop pointer。

优点：router 逻辑最简单（3-bit mux），路径完全可控。

缺点：header 长度随 hop 数线性增长。对于 8×8 mesh（最长 14 hop），需要 14 × 3 = 42 bit 路由字段。

### 形式二：Segment-Based Encoding

连续同方向跳压缩为 (direction, count) pair：

```text
Segment:
  direction: 3 bit
  count:     3 bit (最多 7 hop)

Header layout:
┌──────────┬──────────┬──────────┬──────────┬─────────┐
│ dst_addr │  seg0    │  seg1    │  seg2    │ payload │
│  4 bit   │ 3b+3b   │ 3b+3b   │ 3b+3b   │  ...    │
└──────────┴──────────┴──────────┴──────────┴─────────┘

示例: (0,0) → (3,2), XY routing
  seg0 = (East, 3)    → 向东走 3 hop
  seg1 = (South, 2)   → 向南走 2 hop
  seg2 = (Local, 1)   → 弹出
  编码: 010.011  001.010  100.001
  路由字段总开销: 3 × 6 = 18 bit（和 per-hop 一样，但这是最坏情况）
```

对于 8×8 mesh 的长路径（先走 7 hop X，再走 7 hop Y）：只需 2 个 segment = 12 bit，远少于 per-hop 的 42 bit。

Router 行为：读取当前 segment → 输出到 direction → count 减 1 → 如果 count=0 则移到下一 segment。

### 形式三：Route Table Index

Header 只携带一个 route_id，每个 router 用 route_id 查本地路由表得到输出端口。

```text
Header layout:
┌──────────┬──────────┬─────────┐
│ dst_addr │ route_id │ payload │
│  4 bit   │  8 bit   │  ...    │
└──────────┴──────────┴─────────┘
路由字段总开销: 固定 8 bit（无论路径多长）

Router 行为:
  output_port = route_table[route_id]
  // route_table 由编译器/runtime 在运行前配置
```

优点：header 开销固定且最小；支持路径复用（多个 flow 可共用同一 route_id）。

缺点：每个 router 需要存储路由表（256 entry × 3 bit = 96 byte，很小）；路由表需要在 workload 切换时重新配置。

### 三种方式的 Header Overhead 对比

以 4×4 mesh（最长 6 hop）和 8×8 mesh（最长 14 hop）为例：

| 编码方式 | 4×4 最大开销 | 8×8 最大开销 | 实现复杂度 | 灵活性 |
|---|---|---|---|---|
| Per-hop (3b/hop) | 18 bit | 42 bit | 最低 | 最高 |
| Segment (6b/seg) | 18 bit | 12 bit | 中等 | 高 |
| Route table (8b) | 8 bit | 8 bit | 稍高（需要表） | 中等 |

对 AI 加速器的建议：

- 小规模（≤4×4）：per-hop 足够简单
- 中等规模（4×4 到 8×8）：segment-based 是好平衡
- 大规模或路径复用多：route table index

## 编译器路由生成流程

从 workload mapping 到 header 编码的完整流程：

```text
Step 1: Placement（放置）
  输入: 算子图（op graph）
  输出: 每个算子的 tile 坐标
  方法: 贪心、模拟退火、ILP 等

Step 2: Communication Graph（通信图）
  输入: placement + 数据依赖
  输出: (src_tile, dst_tile, data_size, traffic_class) 列表

Step 3: Path Computation（路径计算）
  输入: communication graph + topology
  输出: 每条 flow 的 hop 序列
  方法:
    - 最短路径（XY routing 等价）
    - 负载均衡路径（避开已知热点链路）
    - 约束路径（避免死锁依赖环）

Step 4: Deadlock Check（死锁检查）
  输入: 所有 flow 的路径 + VC 分配
  方法: 构建 channel dependency graph (CDG)
        检查是否有环
        如果有环 → 调整路径或 VC 分配

Step 5: Header Encoding（编码）
  输入: hop 序列 + 编码格式
  输出: 每个 packet 的 header 路由字段

Step 6: Injection Schedule（注入调度）
  输入: 编码后的 packet + 计算 schedule
  输出: 每个 cycle 每个 tile 注入哪些 packet
```

伪代码示例（Step 3 + Step 4）：

```python
def compile_routes(placement, comm_graph, topology):
    routes = {}
    link_load = defaultdict(int)

    for flow in comm_graph:
        # 最短路径，带负载感知
        path = shortest_path(
            topology,
            src=placement[flow.src_op],
            dst=placement[flow.dst_op],
            weight=lambda link: 1 + link_load[link]
        )
        routes[flow.id] = path
        for link in path:
            link_load[link] += flow.data_size

    # 死锁检查
    cdg = build_channel_dependency_graph(routes, vc_assignment)
    if has_cycle(cdg):
        # 重新分配 VC 或调整路径
        routes, vc_assignment = break_deadlock(routes, cdg)

    return routes
```

## Source Routing 与 VC 的交互

### 方式一：Header 中指定 VC（完全静态）

```text
Header:
┌──────────┬──────────┬────────┬─────────┐
│ dst_addr │ route    │ vc_id  │ payload │
│  4 bit   │ var      │ 2 bit  │  ...    │
└──────────┴──────────┴────────┴─────────┘

编译器在 Step 3 时同时决定路径和 VC。
每个 router 按 header 中的 vc_id 分配 buffer。
```

优点：
- 完全可预测，编译器有最大控制权
- 死锁分析在编译期完成

缺点：
- VC 利用率可能低（某些 VC 分配了但 flow 不活跃时空转）
- 编译器负担重（要同时优化路径 + VC）

### 方式二：Router 本地根据 Traffic Class 分配 VC（半静态）

```text
Header:
┌──────────┬──────────┬───────────────┬─────────┐
│ dst_addr │ route    │ traffic_class │ payload │
│  4 bit   │ var      │ 2 bit         │  ...    │
└──────────┴──────────┴───────────────┴─────────┘

Router 有固定映射: traffic_class → vc_id
例如: control→VC0, response→VC1, data→VC2, bulk→VC3
```

优点：
- 编译器只需标注 traffic class，不需要管 VC
- VC 在同一 class 内共享，利用率更高
- 死锁通过 traffic class 之间的 VC 隔离保证

缺点：
- 同一 traffic class 内的 flow 共享 VC，可能 HOL blocking
- 编译器对 VC 的控制力降低

### 推荐

对 AI 加速器，方式二（半静态）通常是更好的起点：

- 编译器负责路径，硬件负责 VC → 关注点分离
- traffic class 数量有限（通常 3-4 种），映射简单
- 如果特定 flow 需要严格隔离，再升级到方式一

## 对 DSL 的映射

DSL 应该描述**逻辑路径意图**，而不是物理编码：

```yaml
# DSL 层面（逻辑意图）
flow:
  id: weight_broadcast_0
  src: tile_0
  dst: [tile_1, tile_2, tile_3]
  traffic_class: data
  route_hint: shortest_path    # 或 explicit: [R0, R1, R2]
  multicast: tree

# 编译器翻译为具体编码（不在 DSL 中暴露）
# per-hop:  010 010 100
# segment:  (East,2)(Local,1)
# table_id: 0x07
```

原因：

- DSL 的用户关心”从哪到哪、走什么类型的路径”
- 具体的 bit 编码是编译器后端的工作
- DSL 应该能支持”从最短路径到显式指定路径”的灵活性

如果需要精确控制，DSL 可以提供 explicit route 模式：

```yaml
flow:
  id: critical_path_0
  route: explicit
  hops: [R(0,0).E, R(1,0).E, R(2,0).S, R(2,1).Local]
  vc: 2
```

## 本页结论

source routing 对 AI tile dataflow 很重要，因为它把 NoC 设计从”纯硬件局部决策”推进到”编译器与硬件协同的路径规划”。三种 header 编码格式各有适用场景，segment-based 是大多数 AI 加速器的好平衡点。编译器需要完成 placement → path → deadlock check → encoding 的完整流程。DSL 应该描述逻辑路径意图，把物理编码留给编译器后端。
=======
- 额外做一次 path-set legality check（路径集合法性检查）

这样不必一开始就实现复杂 header bit-encoding，也能评估 source routing 的架构价值。

## 你至少应该比较的三件事

- source routing vs XY routing（先X轴再Y轴的维序路由）的热点分布差异
- 固定 placement 下，静态路径是否会放大某些链路压力
- 当流量模式变化时，source routing 的鲁棒性是否下降

## 常见误区

- 认为 source routing 等于不需要仲裁
- 认为 source routing 等于不需要 VC
- 认为只要路径静态就不会 deadlock（死锁）

实际情况是：

- 同一路径上的共享链路仍然要竞争
- traffic class（流量类别）隔离仍然需要
- 静态路径一样可能形成资源依赖环（导致 deadlock）

## 本页结论

source routing 对 AI tile dataflow 很重要，因为它把 NoC 设计从“纯硬件局部决策”推进到“编译器与硬件协同的路径规划”。  
它最适合承担主数据流的可预测传输，但必须和 VC、credit、ejection、QoS（服务质量）一起考虑，才会变成真正有用的系统能力。
>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
