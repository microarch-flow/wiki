<<<<<<< HEAD
# Tree / Fat-Tree 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)、[Collective Implementation 深化](../04-ai-dataflow-system/collective-implementation-deep-dive.md)、[Topology 量化对比](./topology-layout.md)、[Broadcast / Multicast / Reduction 网络](../04-ai-dataflow-system/broadcast-multicast-reduction-network.md)

=======
# Tree / Fat-Tree 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)、[Collective Implementation 深化](../04-ai-dataflow-system/collective-implementation-deep-dive.md)

>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
## 为什么 tree 家族值得单独看

在 AI 芯片里，tree / fat-tree 更常见的角色通常是 reduce、broadcast 或其他 collective 子网络，而不是完整替代通用 packet-switched 主 NoC。

tree 和 fat-tree 的价值，不主要体现在规则 tile 邻近通信，而更体现在：
<<<<<<< HEAD

- gather（收集，多源汇聚到单一目的地）
- reduce（归约，多源数据边汇聚边计算）
- 上收型流量
- 层级带宽组织

## Tree

### 核心直觉

tree 把网络天然组织成“叶子到根”的层级路径。

### 优点

- 非常贴合 reduce / gather 直觉
- 层级结构清晰

### 缺点

- 上层节点容易形成瓶颈
- 根部压力大
- 对 all-to-all（全互连通信）很不友好

## Fat-Tree

### 核心直觉

fat-tree 试图用更强的上层带宽缓解 tree 的收敛瓶颈。

### 优点

- 比普通 tree 更能承受高并发流量
- 对复杂 traffic（流量）更稳

### 缺点

- 结构更贵
- on-chip 场景里未必划算
- router / link 成本更重

## 为什么它们在 AI NoC 里不是默认主流

因为很多 AI 芯片更强调：

- 规则二维布局
- 强局部通信
- floorplan（芯片版图布局）友好

这使 mesh / hierarchical 往往更自然。

## 它们在什么场景下有吸引力

- collective（集合通信）占比高
- reduce / gather 非常关键
- 层级通信远强于二维邻近通信

## 你至少要比较的实验

- flat gather vs tree-like reduce
- tree vs hierarchical mesh 在 collective-heavy workload（工作负载）下谁更稳
- fat-tree 增加带宽后，收益是否抵得上额外成本

## Tree 与 Fat-Tree 的结构区别

### 普通 Binary Tree（N=8 leaf）

```text
              R(root)           ← 1 条上行链路带宽 = W
             /       \
           R           R        ← 2 条链路，各 W
          / \         / \
        R     R     R     R     ← 4 条链路，各 W
       / \   / \   / \   / \
      T0 T1 T2 T3 T4 T5 T6 T7  ← 8 个叶子节点
```

每层链路带宽相同（都是 W）。越靠近 root，流量汇聚越严重，root 链路成为瓶颈。

Bisection BW = 1 × W（只有 root 的一条链路横跨两半）。

### Fat-Tree / Folded Clos（N=8 leaf）

```text
              R(root)           ← 上行带宽 = 4W（4 条并行链路）
             / \\ //\
           R           R        ← 每个 switch 上行 2W，下行 2W
          /|\ |\     /|\ |\
        R     R     R     R     ← 每个 switch 上行 W，下行 W
       / \   / \   / \   / \
      T0 T1 T2 T3 T4 T5 T6 T7
```

越靠近上层，链路数量（或宽度）越"胖"。Root 层的总带宽 = leaf 总注入带宽的一半。

Bisection BW = N/2 × W = 4W（full bisection bandwidth）。

### 关键区别

| 指标 | Binary Tree | Fat-Tree (k-ary) |
|---|---|---|
| Root 瓶颈 | 严重（1W） | 无（full BW） |
| Bisection BW | 1 × W | N/2 × W |
| Switch 总数 | N-1 | ~2N |
| 每 switch radix | 3 | 2k |
| 总链路数 | N-1 | ~2N |
| 面积 | O(N) | O(N log N) |

## 量化公式

### 通用 k-ary n-tree（k 叉 n 层树，N = kⁿ leaf）

| 指标 | 公式 | k=2, N=16 | k=4, N=16 |
|---|---|---|---|
| 层数 n | logₖN | 4 | 2 |
| Diameter | 2n = 2logₖN | 8 | 4 |
| Avg Hop | n = logₖN | 4 | 2 |
| Switch 总数 (tree) | N-1 | 15 | 15 |
| Switch 总数 (fat-tree) | ~2N | ~32 | ~32 |
| Bisection BW (tree) | 1 × W | 32 GB/s | 32 GB/s |
| Bisection BW (fat-tree) | N/2 × W | 256 GB/s | 256 GB/s |

### 与 Mesh 的延迟对比（做 Reduction）

N 个节点做 all-reduce 时：

| 拓扑 | Reduction 延迟 | 说明 |
|---|---|---|
| Tree (in-network reduce) | O(log₂ N) hop | 每级做一次 add，从 leaf 到 root |
| Fat-Tree (in-network reduce) | O(log₂ N) hop | 同上，但带宽不受限 |
| Mesh (endpoint reduce) | O(√N) hop | many-to-one unicast 到 sink |
| Mesh + tree overlay | O(log₂ N) hop | mesh 上叠加 reduction tree |

具体数值（N=16）：

| 拓扑 | Reduction Hop | 与 mesh 对比 |
|---|---|---|
| Tree | 4 hop | 和 mesh 差不多 |
| 4×4 Mesh (to corner) | 6 hop | — |

具体数值（N=64）：

| 拓扑 | Reduction Hop | 与 mesh 对比 |
|---|---|---|
| Tree | 6 hop | 明显更好 |
| 8×8 Mesh (to corner) | 14 hop | — |

结论：**N 越大，tree 在 reduction 上的延迟优势越明显**（log vs √N）。

## Fat-Tree 面积代价

以 N=16 leaf、k=2 fat-tree 为例：

| 组件 | 数量 | 说明 |
|---|---|---|
| Leaf switch | 8 | radix=4（2 上 2 下） |
| Mid switch | 4 | radix=4 |
| Root switch | 2 | radix=4 |
| 总 switch | 14 | 接近 N=16 的 mesh router 数量 |
| 总链路 | ~24 | 与 4×4 mesh (24 links) 相当 |

但 fat-tree 的布局困难：

- mesh 的 router 均匀分布在 2D 平面上，与 tile 一一对应
- fat-tree 的上层 switch 不对应具体 tile，布局需要额外面积
- 上层链路可能很长（连接远距离的子树）

这就是为什么 fat-tree 在片上不如数据中心常见——数据中心的 switch 可以独立放置，芯片上必须和 tile 共享 floorplan。

## AI 芯片中 Tree 的实际应用方式

Tree / fat-tree 在 AI 芯片中通常**不作为主网络**，而是作为**专用 overlay**：

### Reduction Tree Overlay

```text
Base NoC:  4×4 Mesh（搬运 weight、activation、control）

Overlay:   Binary Reduction Tree（专做 partial sum reduce）
           叶子节点 = 每行的 4 个 tile
           树高 = 2 级
           每级做 FP16/FP32 加法
```

典型配置：

| 参数 | 值 | 说明 |
|---|---|---|
| 树高 | 2-3 级 | 对应 4-8 个 leaf |
| 数据宽度 | 与 compute tile 输出一致 | 如 256b / 512b |
| 每级 ALU | FP16 / BF16 / INT32 adder | 支持 in-network reduction |
| 与 mesh 的关系 | 物理上与 mesh router co-located | 共享 floorplan 位置 |

### Broadcast Tree

类似结构，方向相反：root 到 leaf 分发数据。

适合 weight broadcast（1 → N 分发同一份权重到多个 compute tile）。

## 本页结论

tree / fat-tree 在 AI NoC 里不是通用默认答案，但在 collective-heavy、强聚合型流量下，它们提供了与二维 mesh 很不一样的结构化思路。实践中最常见的用法是 **mesh + tree overlay**：mesh 做通用数据搬运，tree 做专用 reduction / broadcast。fat-tree 的 full bisection bandwidth 在片上代价较高，更适合作为理论参考上界。
=======

- gather（收集，多源汇聚到单一目的地）
- reduce（归约，多源数据边汇聚边计算）
- 上收型流量
- 层级带宽组织

## Tree

### 核心直觉

tree 把网络天然组织成“叶子到根”的层级路径。

### 优点

- 非常贴合 reduce / gather 直觉
- 层级结构清晰

### 缺点

- 上层节点容易形成瓶颈
- 根部压力大
- 对 all-to-all（全对全通信）很不友好

## Fat-Tree

### 核心直觉

fat-tree 试图用更强的上层带宽缓解 tree 的收敛瓶颈。

### 优点

- 比普通 tree 更能承受高并发流量
- 对复杂 traffic（流量）更稳

### 缺点

- 结构更贵
- on-chip 场景里未必划算
- router / link 成本更重

## 为什么它们在 AI NoC 里不是默认主流

因为很多 AI 芯片更强调：

- 规则二维布局
- 强局部通信
- floorplan（芯片版图布局）友好

这使 mesh / hierarchical 往往更自然。

## 它们在什么场景下有吸引力

- collective（集合通信）占比高
- reduce / gather 非常关键
- 层级通信远强于二维邻近通信

## 你至少要比较的实验

- flat gather vs tree-like reduce
- tree vs hierarchical mesh 在 collective-heavy workload（工作负载）下谁更稳
- fat-tree 增加带宽后，收益是否抵得上额外成本

## 本页结论

tree / fat-tree 在 AI NoC 里不是通用默认答案，但在 collective-heavy、强聚合型流量下，它们提供了与二维 mesh 很不一样的结构化思路。
>>>>>>> fcf0028b7d9a83d6157907758db21ce2bd383528
