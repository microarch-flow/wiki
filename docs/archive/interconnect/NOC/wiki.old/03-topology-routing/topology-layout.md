# Topology 量化对比与物理布局

上级：[Topology 与 Routing](./README.md)

相关：[架构探索方法](../05-modeling-evaluation/architecture-exploration.md)、[Mesh 专题](./mesh-deep-dive.md)、[Torus 与 Ring 专题](./torus-ring-deep-dive.md)、[Tree / Fat-Tree 专题](./tree-fat-tree-deep-dive.md)、[Crossbar 与 Concentrated Mesh](./crossbar-concentrated-mesh.md)

## 为什么拓扑不是"画图问题"

拓扑同时影响：

- 平均 hop count（跳数，数据包经过的路由器数量）
- 最远路径长度
- bisection bandwidth（二分带宽，将网络平分为两半时横跨切面的总带宽）
- wire length（线长）
- router radix（路由器端口数）
- floorplan（芯片版图布局）兼容性
- 编译器 placement（放置，决定算子或 tile 在芯片上的物理位置）自由度

所以它既是通信问题，也是面积、功耗和实现问题。

## 拓扑量化公式总表

以下用 N 表示 endpoint 总数。对于 2D 结构，假设 N = R×C（R 行 C 列），正方形时 R = C = √N。

| 拓扑 | Diameter | Avg Hop (uniform) | Bisection BW | Router Radix | Total Links | Area Scaling |
|---|---|---|---|---|---|---|
| **Ring** (bidirectional) | ⌊N/2⌋ | N/4 | 2 × link_width | 2 + 1 | N | O(N) |
| **2D Mesh** (R×C) | R+C-2 | (R+C)/3 | min(R,C) × link_width | 4 + 1 | 2RC - R - C | O(N) |
| **2D Torus** (R×C) | ⌊R/2⌋+⌊C/2⌋ | (R+C)/4 | 2×min(R,C) × link_width | 4 + 1 | 2RC | O(N) |
| **Binary Tree** | 2×log₂N | log₂N | 1 × link_width | 3 | N-1 | O(N) |
| **Fat-Tree** (k-ary) | 2×logₖN | logₖN | N/2 × link_width (full) | 2k | ~2N | O(N log N) |
| **Crossbar** | 1 | 1 | N/2 × link_width | N | N×(N-1)/2 | O(N²) |
| **Concentrated Mesh** (k:1) | same as mesh of N/k routers | slightly less than mesh | same as mesh of N/k routers | 4 + k | mesh links + k×N/k local | O(N) |
| **Hypercube** | log₂N | log₂N / 2 | N/2 × link_width | log₂N + 1 | N×log₂N / 2 | O(N log N) |

注：
- Router radix 中 "+1" 表示 local port（连接本地 tile）
- Bisection BW 以链路数 × 单链路带宽表示
- Avg Hop 指 uniform random traffic 下所有 src-dst pair 的平均最短路径长度

## 具体数值对比

### N=16 endpoint

假设 link_width = 256 bit，freq = 1 GHz，单链路带宽 = 32 GB/s。

| 拓扑 | Diameter | Avg Hop | Bisection BW | Router 数 | Router Radix | Total Links |
|---|---|---|---|---|---|---|
| Ring (16) | 8 | 4.0 | 64 GB/s | 16 | 3 | 16 |
| 4×4 Mesh | 6 | 2.67 | 128 GB/s | 16 | 5 | 24 |
| 4×4 Torus | 4 | 2.0 | 256 GB/s | 16 | 5 | 32 |
| Binary Tree | 8 | 4.0 | 32 GB/s | 15 | 3 | 14 |
| 2-ary Fat-Tree | 8 | 4.0 | 256 GB/s | ~32 | 4 | ~32 |
| Crossbar | 1 | 1.0 | 256 GB/s | 1 | 16 | 120 |
| Concentrated Mesh (4:1, 2×2) | 2 | 1.0 | 64 GB/s | 4 | 8 | 4+16 |

### N=64 endpoint

| 拓扑 | Diameter | Avg Hop | Bisection BW | Router 数 | Router Radix |
|---|---|---|---|---|---|
| Ring (64) | 32 | 16.0 | 64 GB/s | 64 | 3 |
| 8×8 Mesh | 14 | 5.33 | 256 GB/s | 64 | 5 |
| 8×8 Torus | 8 | 4.0 | 512 GB/s | 64 | 5 |
| Concentrated Mesh (4:1, 4×4) | 6 | 2.67 | 128 GB/s | 16 | 8 |

关键观察：

- **Ring** 在 N=64 时 diameter 已经到 32，avg hop 到 16，几乎不可用于高带宽数据流
- **Mesh** 是最均衡的选择：radix 不高、bisection BW 够用、diameter 可接受
- **Torus** bisection BW 是 mesh 的 2 倍，diameter 减半，但多出 8 条 wrap-around link
- **Concentrated Mesh (4:1)** 把 64 tile 的问题简化为 16 router 的 mesh，router radix 从 5 升到 8
- **Crossbar** 在 N=64 时 radix=64，面积不可接受

## 物理代价对比

假设 tile pitch = 2mm（相邻 tile 中心距），芯片频率 1 GHz，wire delay ≈ 100 ps/mm。

| 拓扑 | 最短 link | 最长 link | 最长 link pipeline stages | 布线复杂度 |
|---|---|---|---|---|
| 4×4 Mesh | 2mm (1 hop) | 2mm (1 hop) | 0 (单周期) | 低，规则布线 |
| 4×4 Torus | 2mm (1 hop) | 6mm (wrap) | 1 | 中，需要绕线 |
| 8×8 Mesh | 2mm | 2mm | 0 | 低 |
| 8×8 Torus | 2mm | 14mm (wrap) | 1-2 | 高，长绕线 |
| Binary Tree (16 leaf) | 2mm | ~8mm (root) | 1 | 中，上层集中 |
| Concentrated Mesh (4:1) | 4mm (cluster间) | 4mm | 0-1 | 低，router 少 |

关键观察：

- Mesh 的所有 link 等长，物理实现最友好
- Torus 的 wrap-around link 随规模线性增长，8×8 时 wrap link 长达 14mm，需要 pipeline register
- Pipeline link 意味着更大的 credit round-trip → 需要更深的 buffer → 更多面积
- Concentrated mesh 的 cluster 间 link 比普通 mesh 长（跨 cluster），但 link 数量少

## 拓扑选型决策流程

```text
开始
  │
  ▼
endpoint 数量 ≤ 8？
  ├─ 是 → Crossbar（面积可控，单跳延迟）
  │
  ▼
需要 cluster 化设计？（workload 有明显局部性）
  ├─ 是 → cluster 内 crossbar + cluster 间 mesh（concentrated mesh）
  │        cluster 大小 = 2-8 tile
  │
  ▼
对 bisection BW 有极高要求？（如大量 all-to-all）
  ├─ 是 → 考虑 fat-tree / torus
  │        但评估 wrap-around / 上层 switch 的面积代价
  │
  ▼
需要专用 reduction / broadcast 路径？
  ├─ 是 → base mesh + reduction tree overlay
  │
  ▼
默认选择 → 2D Mesh
  适用于大多数 AI accelerator 的第一版设计
  规则、易建模、floorplan 友好
```

## 必须跟踪的拓扑指标

| 指标 | 为什么重要 | 怎么算 |
|---|---|---|
| average hop count | 决定平均延迟和平均线材占用 | 所有 src-dst pair 的最短路径平均值 |
| diameter | 决定最坏延迟 | 所有 src-dst pair 的最短路径最大值 |
| bisection bandwidth | 决定理论最大吞吐上界 | 将网络等分为两半，横跨切面的总带宽 |
| router radix | 决定 router 面积和仲裁复杂度 | router 的端口数（含 local port） |
| link count | 决定总布线面积 | 网络中双向链路的总数 |
| max wire length | 决定是否需要 pipeline register | 最长链路的物理长度 |
| placement compatibility | 决定编译器 mapping 自由度 | 拓扑结构与 tile/SRAM/HBM 物理布局的匹配程度 |

## 对 AI 芯片特别关键的两个问题

### Flat mesh 还是 cluster-hierarchical

这通常不是纯 NoC 决策，而是与 tile 面积、local SRAM 大小、编译器切分粒度、workload 的空间局部性共同决定。

经验规则：

- cluster 内流量占比 > 60% 时，hierarchical 设计通常优于 flat mesh
- cluster 大小 4-8 tile 是最常见的甜区
- flat mesh 在 tile 数 ≤ 16 时通常足够

### HBM / DMA / SRAM bank 放在哪里

端点位置会决定热点分布。同一套 router 参数，在不同 memory placement 下可能出现完全不同的拥塞图。

常见方案：

- **边缘放置**：HBM/DMA port 放在 mesh 边缘，边缘 router 承受更大压力
- **分布式放置**：memory port 均匀散布，平衡负载但增加布线复杂度
- **集中放置**：memory port 集中在一侧，简单但容易形成单侧热点

## 一个实用判断

对 AI tile 架构来说，最重要的往往不是"理论最优拓扑"，而是：

在真实 floorplan、真实 memory placement、真实 workload 下，哪种拓扑能以最低复杂度获得更好的稳定吞吐。

量化公式帮你快速筛选候选方案，但最终判断必须回到 workload-driven simulation。
