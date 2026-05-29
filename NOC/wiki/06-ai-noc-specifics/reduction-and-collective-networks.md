# Reduction And Collective Networks

上级：[06 AI NOC Specifics](./README.md)

相关：[Broadcast Multicast Tree](./broadcast-multicast-tree.md)、[Workload GEMM On NOC](./workload-gemm-on-noc.md)、[Workload MOE Routing](./workload-moe-routing.md)

## 这页在回答什么问题

这页回答：当 AI NoC 里出现 gather、reduce、all-reduce、all-to-all 这类 collective 时，为什么不能再只用普通 point-to-point 直觉来思考网络，以及**怎样把每种 collective 的代价写成可计算的公式**——stage 数、带宽瓶颈、完成时间、热点位置。

## collective 的关键不是总量，而是形状

collective 最大的问题通常不是"字节总量特别大"，而是：

- one-to-many
- many-to-one
- many-to-many

这种空间结构会让热点更集中、同步更明显、端点压力更极端。

## gather 和 reduce 不是一回事

要先区分：

- `gather`：只是把数据收过来
- `reduce`：收过来的同时还要做结合运算

如果所有 partial sum 都直接冲向一个 sink，再在 sink 端算，这对网络和 endpoint 都很不友好。更好的方式通常是：

- endpoint aggregation
- tree reduction
- hierarchical reduction

它们的共同目标都是把压力从"一个最终 sink"往中间层分摊。

## 参数化前先约定符号

后面所有公式统一用这些符号：

| 符号 | 含义 |
|------|------|
| `N` | 参与 collective 的端点数 |
| `M` | 每个端点贡献的数据量（bytes） |
| `B` | 单端点单向 link 的带宽（bytes/cycle）|
| `α` | 单跳固定延迟（cycle），含 router + link |
| `D` | 集合通信路径上的最大 hop 数（topology-dependent） |
| `Treduce` | reduce 算子在端点上的处理时延（cycles/byte），通常 ≪ α |

注：单端点同时拥有的注入/弹出带宽通常各为 `B`，所以一个端点最多同时发 `B` 收 `B`。

## 朴素 sink-based reduce 的代价

所有人都向一个 sink 直接发：

```text
total_bytes_to_sink = (N - 1) · M
sink_ejection_time  = (N - 1) · M / B          # sink 注入端带宽瓶颈
T_naive             ≈ D · α + (N-1) · M / B
```

致命问题：sink 的 ejection bandwidth 成为唯一瓶颈，与 `N` 线性相关。`N` 翻倍，完成时间翻倍——这就是为什么大规模 collective 几乎不会走这条路径。

## ring AllReduce 的代价

把所有端点排成一个环，分两阶段：

1. **scatter-reduce**：每端点把数据切成 N 块，每块绕环 N-1 步累加，每步只发 `M/N`
2. **all-gather**：再绕环 N-1 步把最终结果广播回所有端点

公式：

```text
stages_per_phase = N - 1
bytes_per_step   = M / N
T_ring_step      ≈ α + (M/N) / B
T_ring_total     = 2 · (N - 1) · T_ring_step
                 = 2(N-1) · α  +  2(N-1)/N · M / B

# 当 N 较大时：
T_ring_total ≈ 2N · α + 2 · M / B
```

关键结论：
- **带宽项与 N 无关**（趋近 `2M/B`），因此 ring 在大 `N` 下带宽利用率最优
- **延迟项 ∝ N**（`2N·α`），所以小消息、大 N 下 ring 反而很差
- **每条 link 的瞬时带宽 = `M/(N·B)`**——所有 link 同时被用，热点完全消失

ring 是带宽友好、延迟敌人。

## tree AllReduce 的代价

二叉 reduce-tree 上行 + broadcast-tree 下行：

```text
stages_reduce    = ceil(log2(N))
stages_broadcast = ceil(log2(N))
T_tree_total     = 2 · log2(N) · (α + M / B)

# 根节点 ejection 带宽：M / B（与 N 无关）
# 但根节点同时被 log2(N) 个上行流冲击
```

关键结论：
- **延迟项 ∝ log N**，小消息下显著优于 ring
- **带宽项 ∝ log N · M**，大消息下劣于 ring（因为每一层都搬运全 M 字节）
- **根节点是热点**：上行最后一拍 root 端点同时收 `log2(N)` 路；硬件需要 multi-port endpoint 或更大 ejection queue

tree 是延迟友好、根节点压力大。

## halving-doubling / recursive halving AllReduce

把 ring 的"一次一块"和 tree 的"log N"结合，是大模型训练里最常用的：

```text
stages           = 2 · log2(N)                # halving + doubling
bytes_per_step   = M / 2^k  (k = step index)
T_hd_per_step    = α + (M / 2^k) / B

T_hd_total       = 2 · log2(N) · α  +  2 · M / B · (1 - 1/N)
                ≈ 2 · log2(N) · α  +  2 · M / B
```

关键结论：
- **同时具备 ring 的带宽最优（`2M/B`）和 tree 的延迟最优（`log N · α`）**
- 但要求**任意一对端点之间存在低 hop 路径**——只在 fat-tree / dragonfly / hypercube 之类拓扑上自然落地
- 在 mesh / torus 上做 halving-doubling 会跨长链，长拓扑直径反而吃掉收益

## 三种方案对比

固定 `α=10 cyc`、`B=64 B/cyc`、假设拓扑给出任意路径 `log₂(N)·α`（fat-tree 类）、对几组 `(N, M)` 算一遍。表格每格写成 `α项 + 带宽项 = 合计`：

| 场景 | `N` | `M` | T_naive | T_ring | T_tree | T_hd |
|------|-----|-----|---------|--------|--------|------|
| 小消息、小 N | 16 | 1 KB | 40 + 240 = 280 | 300 + 30 = 330 | 80 + 128 = 208 | 80 + 30 = **110** |
| 大消息、小 N | 16 | 1 MB | 40 + 246k ≈ **246k** | 300 + 31k ≈ 31k | 80 + 131k ≈ 131k | 80 + 31k ≈ **31k** |
| 小消息、大 N | 256 | 1 KB | 80 + 4080 ≈ 4.2k | 5100 + 32 ≈ 5132 | 160 + 256 = 416 | 160 + 32 = **192** |
| 大消息、大 N | 256 | 1 MB | 80 + 4.18M ≈ **4.18M** | 5100 + 33k ≈ 38k | 160 + 262k ≈ 262k | 160 + 33k ≈ **33k** |

每行加粗的是最优算法。读法：

- **小消息小 N**：α 项主导，hd 凭 `2·log N · α` 击败 ring 的 `2N · α`，是 ring 的 ~3 倍快
- **大消息小 N**：带宽项主导，hd 和 ring 并列最优（带宽项都 ≈ `2M/B`），均胜 tree 4 倍
- **小消息大 N**：α 项与带宽项都被 N 放大，hd 凭对数级 α 项一骑绝尘
- **大消息大 N**：naive 直接 4 M 拍——验证为什么大模型训练禁止 sink-based reduce；tree 的 `log N · M/B` 带宽项也吃掉收益；hd 与 ring 持平

总结主导项：
- α 项主导（消息小）→ tree / hd 远胜 ring
- 带宽项主导（消息大）→ ring / hd 远胜 tree
- 大 N + 大消息 → hd 是唯一全场景都不输的方案，但拓扑必须支持它

**α 项与带宽项的交叉点**可以解析求出（让 ring 的 `2N·α` ≈ tree 的 `2·log N · M/B`），是判断"该用哪种算法"的最早早期截止线。

## 多播 / 一对多 的展开方式

multicast 在 NoC 上有两种实现策略，开销差异显著：

| 实现 | 总 flit 数 | hot link | 何时合理 |
|------|-----------|----------|----------|
| **endpoint replication**（源端发 K 份 unicast）| `K · M / flit_size` | 源端注入链路 | K 小、目标分散 |
| **router-level tree replication**（沿路 fork）| `M · (sum of tree edges) / flit_size` | 树枝节点 | K 大、目标局部聚集 |

router-level 的总 flit 数下界 = `M · (N - 1) / flit_size`（树边数），比 endpoint replication 的 `M · K` 至少省一个数量级。代价是 router 必须支持 multicast fork 状态机。

## all-to-all 的代价

每个端点向所有其他端点各发 `M/N`：

```text
total_bytes_at_each_endpoint = (N-1) · M/N · 2  (in+out)
T_a2a_lower_bound (任何拓扑)  ≥ (N-1) · M / N / B
T_a2a_on_ring                ≈ N/2 · M / N / B  · 2 = M / B   (绕环平均距离 N/2)
T_a2a_on_fat_tree            ≈ M / B · log(N)
```

all-to-all 的下界由端点带宽决定，与拓扑形态关系不大。但**实际值**和拓扑高度相关：mesh/torus 上 all-to-all 容易把中央链路打到饱和。

## 热点位置速查

| Collective | 热点 | 缓解手段 |
|-----------|------|---------|
| sink-based gather/reduce | sink 端点 ejection link | 改 tree / ring |
| tree reduce | root 的最后一跳，以及二叉树合并节点 | 增加 root 端口数 / multi-rooted tree |
| ring reduce | 没有结构性热点 | （首选） |
| recursive halving-doubling | 中间步骤在 bisection 链路 | 拓扑选 fat-tree / dragonfly |
| all-to-all on mesh | 中央 row/column 链路 | concentration / 增加 channels |
| multicast endpoint replication | 源端注入 link | 改 router-level tree |

热点的诊断信号在 simulator 里就是**单链路利用率**：collective 期间某条链路 ≥ 90% 而其余 < 30%，几乎必然是上表中的某一行。

## 分层 collective

很常见的思路是：

- 先 cluster 内 gather / reduce
- 再 cluster 间交换更少的聚合结果

分两层时：

```text
T_2level = T_intra(N_in, M)  +  T_inter(N_out, M)
       where N_in · N_out = N
```

最优 `(N_in, N_out)` 切分点由 `α_intra / α_inter` 与 `B_intra / B_inter` 决定。一般规律：

- `α_inter ≫ α_intra`（die-to-die / 跨 cluster）时，应让 `N_out` 小、`N_in` 大
- `B_intra ≫ B_inter` 时，同样应该 cluster 内尽量聚合，减少跨层字节

因此分层不是设计风格，是**对参数比值的最优响应**。

## 什么时候值得上专用 collective network

通常在下面条件**多个**成立时值得考虑：

- 某类 collective 高频出现（例如训练每个 step 都做 AllReduce）
- multiple-unicast / flat gather 重复占用非常明显
- 端点或主干热点已经成为系统主瓶颈
- collective 完成时间占 step time > 20%
- 软件实现与普通 data network 混跑代价太高（QoS 隔离困难）

否则专用网络可能只是把少数流量问题硬件化，收益不够。判据是**实测**带宽项 / 延迟项哪个主导——若是带宽项，专用 reduce link 收益最大；若是延迟项，应该先优化 α 而不是上专网。

## 一句话理解

collective 网络关注的不是"能不能把数据送到"，而是**用 α 和 M/B 这两项的比值决定算法形状**：α 项主导用 tree，带宽项主导用 ring，两项都重就用 halving-doubling，且必须有支撑该算法的拓扑。

## 建模启示

第一版模型至少要能表达：

```text
CollectiveOp {
  pattern        := SINK | RING | TREE | HALVING_DOUBLING | ALL_TO_ALL | MULTICAST
  N              # 参与端点
  M              # per-endpoint bytes
  participants[] # NodeId
  topology_path  # 每 stage 的路径（用于热点定位）
}

CollectivePerformance {
  T_total = T_alpha + T_bw
  T_alpha = stages * (alpha + per_step_overhead)
  T_bw    = sum(per_step_bytes / B)
  hot_links[] := { link_id, utilization }
}
```

然后比较：

- `T_alpha` vs `T_bw` 各自占比（决定算法选择）
- `hot_links` 最大利用率（决定是否需要拓扑/分层调整）
- `total_flit_count`（决定能耗）
- `sink/root ejection pressure`（决定端点接口设计）
- `tail latency`（决定同步开销）

这比只比平均带宽更接近 collective 的真实代价。`from-workload-to-traffic-trace.md` 里 AllReduce 的 trace 生成需要这里的 `pattern` 和 `topology_path` 作为参数化输入。
