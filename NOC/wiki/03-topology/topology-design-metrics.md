# Topology Design Metrics

上级：[03 Topology](./README.md)
相关：[Mesh And Torus](./mesh-and-torus.md), [Topology Selection Framework](./topology-selection-framework.md)

## 这页在回答什么问题

判断一种 topology 时，真正应该先看哪些指标，以及这些指标分别在约束什么。

如果一上来就只比 average hop，很容易把“逻辑距离更短”误当成“系统一定更好”。实际设计里，diameter、bisection bandwidth、router radix、path diversity、最大线长往往同样关键。

## 为什么不能只看 hop 数

hop 数很容易被滥用，因为它最直观。一个 topology 的平均最短路径更短，看起来就像延迟更低。但这个推断只在两个前提同时成立时才近似有效：

- 每一跳代价相近
- 不会因为热点或长线代价把 hop 优势吃掉

现实里这两个前提都经常失效。torus 的逻辑 hop 可能比 mesh 少，但 wrap-around link 更长；fat-tree 的路径层数可能更低，但高层 switch 更大、布线更集中；crossbar 虽然单跳，但 radix 和布线开销可能让频率下降。

所以 topology 指标的作用，不是替你做结论，而是告诉你哪类代价可能主导。

## 指标一：Diameter

diameter 是任意两点之间最短路径长度的最大值。它回答的是：最坏情况下，网络要跨多远。

对 worst-case latency、tail latency 和编译器保守估计来说，diameter 比 average hop 更重要。因为很多 deterministic 系统关心的不是“平均多快”，而是“最坏要多慢”。

但它也不能单独用。一个 topology 的 diameter 小，不代表它在平均流量下就好，也不代表它物理上好实现。

## 指标二：Average Shortest Path

average shortest path 更贴近 uniform 或较分散流量下的平均通信距离。它常被拿来估计平均 hop latency 和平均链路占用。

这个指标对 baseline 筛选很有用，尤其在你还没建立 workload trace 时。但它的局限也明显：

- 它默认所有 src-dst pair 权重相近
- 它不看路径是否集中穿过同一区域
- 它不看每跳物理代价是否对称

所以 average hop 适合做 first-order 判断，不适合单独做最终选型。

## 指标三：Bisection Bandwidth

bisection bandwidth 回答的是：把网络切成两半后，横跨切面的总带宽有多大。

这个指标特别适合判断：

- all-to-all 或大量跨区域流量的上限
- memory port 集中放置时的主干压力
- collective-heavy workload 的结构瓶颈

ring 的一个典型问题，就是 bisection bandwidth 基本不随节点数增长；mesh 的 bisection bandwidth 会随一维长度增长；fat-tree 则是在设计上主动为上层汇聚区补带宽。

这就是为什么某些 topology 的 average hop 看起来还能接受，但一旦进入高并发跨区通信，吞吐会迅速掉队。

## 指标四：Router Radix

radix 是 router 的端口数。它回答的是：每个 router 要直接连接多少方向和端点。

radix 增加的好处：

- 平均 hop 可能下降
- 拓扑更“扁平”

radix 增加的代价：

- crossbar 更大
- allocator 更复杂
- 布线和时序压力更大

这就是 flattened butterfly、dragonfly 这类高-radix 家族在机柜级系统里很有吸引力，但在片上常常要谨慎借鉴的原因。高 radix 不是免费换 hop。

## 指标五：Path Diversity

path diversity 回答的是：从一个源到一个目的，是否存在多条质量相近的可选路径。

这个指标本身不等于吞吐，但它会决定后面的 routing 策略有没有施展空间。path diversity 高，adaptive routing 和负载均衡的潜力更大；path diversity 低，deterministic routing 的代价也更小。

所以它是 topology 和 routing 的接口指标。你现在在 topology 章节先看它，是为了后面不高估 routing 策略的自由度。

## 指标六：Maximum Wire Length

这是最容易在纯算法讨论里被忽略、但在芯片上最致命的指标之一。

最大线长决定：

- 是否需要额外 pipeline stage
- credit round-trip 是否会被拉长
- metal resource 和布线拥塞是否可接受

这也是为什么 mesh 经常在片上“看起来不惊艳但总能落地”：它的链路长度规则而可控。反过来，很多理论上 hop 更优的拓扑，往往在最大线长上突然变得很难。

## 一张实用对照表

| 指标 | 主要约束什么 | 典型误用 |
| --- | --- | --- |
| Diameter | 最坏路径长度 | 被当成平均性能指标 |
| Average shortest path | 平均通信距离 | 被当成拥塞预测指标 |
| Bisection bandwidth | 跨区吞吐上限 | 被忽略，只看 hop |
| Router radix | router 复杂度 | 被当成纯连接数，不看时序 |
| Path diversity | 路由自由度 | 被误当成吞吐本身 |
| Max wire length | 物理可实现性 | 在纯图论比较里被省略 |

## 各拓扑的闭式公式表

为了让 early-stage screening 可以直接查表，把常见拓扑的六个指标都写成 `N`（节点总数）的闭式表达。约定：

- `W` = 单条 link 带宽（bytes/cycle）
- `tile_pitch` = 物理单 tile 边长，作为线长单位
- mesh / torus 默认为 `k × k = N` 二维方阵（`k = √N`）
- fat-tree 默认 `k` 叉、`L = log_k(N)` 层
- dragonfly 默认 `a` 个 router 组成一 group、`g` 个 group、`p` 端点/router，`N = a · g · p`

### 1D ring（N 节点）

| 指标 | 公式 | N=16 取值 |
|------|------|----------|
| diameter | `⌊N/2⌋` | 8 |
| average hop | `N/4` | 4 |
| bisection BW | `2W` | 2W |
| max radix | `3`（2 个邻居 + 1 local）| 3 |
| path diversity | `2`（左右两路）| 2 |
| max wire span | `1 · tile_pitch`（含 wrap）| 1 |

bisection BW 不随 N 增长——这是 ring 在大规模下迅速饱和的根本原因。

### 2D mesh（k × k = N）

| 指标 | 公式 | k=4, N=16 | k=8, N=64 |
|------|------|-----------|-----------|
| diameter | `2(k - 1)` | 6 | 14 |
| average hop | `2k/3`（近似）| 2.67 | 5.33 |
| bisection BW | `k · W` | 4W | 8W |
| max radix | `5`（4 邻居 + local）| 5 | 5 |
| path diversity | `min(Δx, Δy) + 1`（XY 多路）| 1~3 | 1~5 |
| max wire span | `1 · tile_pitch` | 1 | 1 |

mesh 的招牌特性：radix 恒为 5、线长恒为 1 tile，物理可实现性最稳定。

### 2D torus（k × k = N）

| 指标 | 公式 | k=4, N=16 | k=8, N=64 |
|------|------|-----------|-----------|
| diameter | `⌊k/2⌋ + ⌊k/2⌋ = k`（偶数 k）| 4 | 8 |
| average hop | `k/2`（近似）| 2.0 | 4.0 |
| bisection BW | `2k · W` | 8W | 16W |
| max radix | `5` | 5 | 5 |
| path diversity | `≈ 2·(Δx路 × Δy路)` | 2~4 | 2~8 |
| max wire span | `(k-1)/2 · tile_pitch`（wrap 折叠后）| 1.5 | 3.5 |

torus 用更长 wrap link 换得 2× bisection 和更小 diameter，物理实现复杂度更高。

### Concentrated mesh（c 个 tile 共享一个 router，c·k² = N）

| 指标 | 公式 | c=4, k=4, N=64 |
|------|------|---------------|
| diameter | `2(k-1)` | 6 |
| average hop | `2k/3 + intra_concentration_cost` | 2.67 + ε |
| bisection BW | `k · W`（router 间）| 4W |
| max radix | `4 + c` | 8 |
| path diversity | 与 mesh 类似 | - |
| max wire span | `1 · tile_pitch` | 1 |

集中度 c 提升用 router radix 换 hop 数。c=4 时 router 数减为 1/4，节面积但 radix 更大。

### k-ary fat-tree（k 叉、L 层、N = k^L 叶子）

| 指标 | 公式 | k=4, L=3, N=64 |
|------|------|---------------|
| diameter | `2L` | 6 |
| average hop | `≈ 2L · (1 - 1/k)` | 4.5 |
| bisection BW | `N/2 · W`（满胖度）| 32W |
| max radix | `2k`（向上向下各 k）| 8 |
| path diversity | `k^(L-1)`（核心层路径数）| 16 |
| max wire span | `O(L · spacing)`（核心层最长）| ≫ 1 |

fat-tree 的招牌：bisection BW 随 N 线性增长，是数据中心首选。代价是核心层长线和高 radix switch。

### Dragonfly（a · g · p = N）

| 指标 | 公式 | a=4, g=8, p=4, N=128 |
|------|------|---------------------|
| diameter | `3`（local + global + local）| 3 |
| average hop | `≈ 2 + g/(2·a·(a-1))` | ≈ 2.27 |
| bisection BW | `N · W / 2`（满 group-to-group）| 64W |
| max radix | `a - 1 + g - 1 + p` = local + global + endpoint | 14 |
| path diversity | `g`（global link 多路）| 8 |
| max wire span | global link `≫ tile_pitch` | large |

dragonfly 的招牌：constant diameter，端点数翻倍 diameter 不变。代价是 global link 物理上极长，且 max radix 随 N 增长。

### 总表（汇总查阅）

按"主要约束"列重新排一遍（数值都按相同 N=64 折算）：

| 拓扑 | diameter | avg hop | bisection | radix | path div | max wire | 主导优势 |
|------|----------|---------|-----------|-------|----------|----------|----------|
| Ring (N=64) | 32 | 16 | 2W | 3 | 2 | 1 | 实现极简 |
| 2D mesh (8×8) | 14 | 5.33 | 8W | 5 | 1~5 | 1 | 物理稳定 |
| 2D torus (8×8) | 8 | 4 | 16W | 5 | 2~8 | 3.5 | 平衡 hop/BW |
| Cmesh (c=4) | 6 | 2.67 | 4W | 8 | 1~3 | 1 | 省 router 数 |
| Fat-tree (k=4,L=3) | 6 | 4.5 | 32W | 8 | 16 | large | 跨区 BW |
| Dragonfly | 3 | 2.27 | 32W | 14 | 8 | very large | constant diameter |

从这张表可以一眼看出三类设计哲学：

- **mesh/torus** 把 radix 锁死换可实现性
- **fat-tree** 加 layer 加 radix 换 bisection
- **dragonfly** 用长 global link 换 constant diameter

没有一种拓扑同时拿满"radix 小 + diameter 小 + bisection 大 + wire 短"——必须在四个维度上做选择。

## 把这些指标接到 NoC 性能公式

闭式公式不是为了好看，是为了**直接代入 collective / GEMM 性能估计**。例如：

```text
# 一个 N=64 AllReduce 的下界估计（ring algorithm）
T_lower_bound = 2(N-1) · α_per_hop + 2 · M / B_bisection
```

代入不同拓扑得到不同的 `α_per_hop` 和 `B_bisection`，可立即排出预期排名而不必跑 simulator。如果实测排名与这里不同，就要回查是 placement、routing 还是 traffic class 偷走了名义带宽。

## 一个具体例子：4x4 mesh vs 4x4 torus

两者在图论上很接近，但看指标就知道它们在芯片上不是同一种东西。

| 指标 | 4x4 Mesh | 4x4 Torus |
| --- | --- | --- |
| Diameter | 6 | 4 |
| Average hop | 2.67 | 2.0 |
| Bisection BW | 4W | 8W |
| Max wire length | 1 tile pitch | 3 tile pitches wrap-around |

如果你只看前三项，torus 像明显更优；一旦把最大线长补回来，就知道它的优势不是白来的，而是拿长链路和更复杂死锁处理换的。

## 常见误解

常见误解：平均 hop 最低的 topology 就是最优 topology。  
实际上：平均 hop 只描述图上的平均距离，不描述高-radix、长链路、热点和时序代价。

常见误解：bisection bandwidth 只对 HPC 重要，对片上系统不重要。  
实际上：AI NoC 里只要存在大规模跨区域流量、memory port 汇聚或 collective，bisection bandwidth 就会立刻变成一阶指标。

## 一句话理解

topology 指标的作用，不是替你选答案，而是把“距离、吞吐、router 复杂度和物理代价”拆成互不偷换的几张表。

## 建模启示

做 early-stage topology screening 时，至少把这些字段放进配置：

```text
TopologyMetrics {
  diameter            # 闭式公式见上文
  average_hops
  bisection_links     # bisection BW 的 link 数
  max_radix
  path_diversity
  max_wire_span       # 单位：tile_pitch
}

TopologyClosedForm(topology_type, N, ...) -> TopologyMetrics
```

`TopologyClosedForm` 是上面公式表的直接实现。给一个 `(type, N)` 返回六元组，screening 阶段不需要建图也不需要跑 BFS。

如果只做 analytical baseline，可以先用 `average_hops * per_hop_latency` 估平均延迟，用 `bisection_links * link_bw` 估跨区吞吐上限。

如果要进一步接近真实芯片，`max_wire_span` 不能再忽略，因为它会反过来改变 `per_hop_latency` 和 `credit_round_trip`——具体地：

```text
per_hop_latency(topology) = base_router_delay + ceil(max_wire_span / signal_um_per_cycle)
R(topology, allocator) = per_hop_latency · 2 + router_internal_residency(allocator, K)
buffer_depth_min(topology, allocator) = R
```

这条链条把 topology metric → router 流水 → buffer 需求一路打通：拓扑变了，buffer 自动跟着改，不必工程经验拍数。完整 R 公式见 [credit-based-flow-control](../02-router-microarchitecture/credit-based-flow-control.md#r-的参数化分解)。
