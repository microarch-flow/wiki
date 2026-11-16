# Torus 与 Ring 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)、[Topology 量化对比](./topology-layout.md)、[Mesh 专题](./mesh-deep-dive.md)

## 为什么把 torus 和 ring 放一起

它们都可以看成“比 mesh 更强调闭环路径”的家族，但系统价值完全不同：

- torus（环面拓扑）更像对 mesh（网格拓扑）的增强
- ring（环形拓扑）更像极简互连

## Torus

### 核心直觉

torus 在 mesh 基础上增加环回边（wrap-around link），目标是：

- 降低边界效应
- 缩短逻辑最远距离
- 提高横截面带宽（bisection bandwidth，将网络平分为两半时横跨切面的总带宽）

### 优点

- 平均 hop（跳数）通常更好
- 边角节点不再天然弱势

### 关键问题

- 环回边往往是长链路
- 物理实现成本不再像 mesh 那样规整
- 长链路 pipeline（流水线）可能吃掉逻辑 hop 优势

### 适合什么

- 真正愿意把长链路代价纳入设计的系统

## Ring

### 核心直觉

ring 用最小结构换最简单实现。

### 优点

- 小规模时非常省
- 控制简单
- 验证也简单

### 关键问题

- 扩展性差
- 共享路径很强，热点敏感
- 大规模时延和带宽都容易掉队

### 适合什么

- 小 cluster（簇）内互连
- 控制面
- 较轻量子网络

## 什么时候 torus 胜过 mesh

通常在你确实需要更低逻辑 hop，而且愿意接受：

- 长链路
- 更复杂物理实现
- credit round-trip（信用往返延迟）可能变长

否则理论优势未必会兑现。

## 什么时候 ring 仍有价值

不是作为大规模全局主互连，而是作为：

- local ring
- side network
- 小规模 cluster fabric

## 你至少该做的实验

- mesh vs torus：同规模下加入长链路代价后是否还占优
- ring 作为 cluster-local fabric（本地互连结构）是否优于 local crossbar（交叉开关）

## Torus 量化分析

### 公式对比

对于 R×C 的 2D 网络（N = R×C）：

| 指标 | Mesh | Torus | Torus 改善 |
|---|---|---|---|
| Diameter | R+C-2 | ⌊R/2⌋+⌊C/2⌋ | ~2× 缩短 |
| Average Hop | (R+C)/3 | (R+C)/4 | ~25% 缩短 |
| Bisection BW | min(R,C) × W | 2×min(R,C) × W | 2× 提升 |
| Total Links | 2RC-R-C | 2RC | 多 R+C 条 |

### 具体数值（4×4，link_width=256b，1GHz）

| 指标 | 4×4 Mesh | 4×4 Torus | 差异 |
|---|---|---|---|
| Diameter | 6 | 4 | -33% |
| Avg Hop | 2.67 | 2.0 | -25% |
| Bisection BW | 128 GB/s | 256 GB/s | +100% |
| Total Links | 24 | 32 | +8 条 wrap link |
| 最长 link（物理） | 2mm | 6mm (wrap) | 3× |

### Wrap-Around Link 的物理代价

假设 tile pitch = 2mm，freq = 1GHz，wire delay ≈ 100ps/mm：

| Mesh 尺寸 | Wrap link 长度 | Wire delay | 需要 pipeline stages | 额外 credit round-trip |
|---|---|---|---|---|
| 4×4 | (4-1)×2mm = 6mm | 0.6ns | 0-1 | +0~2 cycle |
| 8×8 | (8-1)×2mm = 14mm | 1.4ns | 1-2 | +2~4 cycle |
| 16×16 | (16-1)×2mm = 30mm | 3.0ns | 3 | +6 cycle |

Pipeline link 的连锁代价：

- 每增加 1 个 pipeline stage → credit round-trip 增加 2 cycle
- credit round-trip 增加 → 需要更深的 input buffer 来避免 link 空转
- buffer depth 增加 → router 面积增加
- 所以 wrap-around link 的代价不只是”多几根线”，而是 **pipeline + buffer + 面积** 的连锁放大

### Dateline 死锁与额外 VC 需求

Torus 的环回结构会引入新的死锁风险：

```text
Mesh：所有路径单调递增/递减，不会成环 → XY routing 天然无死锁

Torus：路径可以绕环 → 可能形成环形依赖 → 死锁
```

解决方案——Dateline 机制：

- 在 torus 的环上选定一个位置作为 dateline（日期线）
- 跨越 dateline 的 packet 必须切换到另一个 VC
- 至少需要比 mesh 多 1 个 VC（每个 dateline 维度各 1 个）
- 4×4 torus（2 个环维度）至少多 2 个 VC

额外 VC 的代价：

- 每多 1 个 VC → input buffer 面积增加 ~1/vc_count（假设原来 4 VC，多 1 个则增 25%）
- 仲裁复杂度增加

### 什么规模下 Torus 值得

| 条件 | Torus 是否值得 | 原因 |
|---|---|---|
| N ≤ 4×4，wrap link ≤ 6mm | 可能值得 | wrap 代价可控，bisection BW 翻倍有吸引力 |
| N = 8×8，wrap link = 14mm | 通常不值得 | pipeline + buffer 代价吃掉 hop 改善 |
| N ≥ 16×16 | 几乎不值得 | wrap link 太长，应考虑 hierarchical 设计 |
| 流量以 all-to-all 为主 | 更值得 | bisection BW 翻倍的价值更大 |
| 流量有强局部性 | 不值得 | 局部流量不走 wrap link，优势无法发挥 |

## Ring 量化分析

### 公式

N 节点双向 ring：

| 指标 | 公式 | N=8 | N=16 | N=32 |
|---|---|---|---|---|
| Diameter | ⌊N/2⌋ | 4 | 8 | 16 |
| Avg Hop | N/4 | 2.0 | 4.0 | 8.0 |
| Bisection BW | 2 × link_width | 64 GB/s | 64 GB/s | 64 GB/s |
| Router Radix | 3 (left + right + local) | 3 | 3 | 3 |
| Total Links | N | 8 | 16 | 32 |

关键问题：**bisection BW 不随 N 增长**。

这意味着 ring 上 N 个节点共享固定的 2 × link_width 横截面带宽。N 越大，每节点可用带宽越低。

### Ring 在 AI 芯片中的适用场景量化

| 用途 | 典型 N | 带宽需求 | Ring 是否合适 |
|---|---|---|---|
| Cluster 内控制面 | 4-8 | 低（几 GB/s） | 合适，简单廉价 |
| Debug / profiling 网络 | 任意 | 极低 | 合适，面积最小 |
| 小 cluster 内数据面 | 4-6 | 中等 | 可能，但 crossbar 通常更好 |
| 全局数据面 | >8 | 高 | 不合适，bisection BW 不够 |
| Synchronization 网络 | 任意 | 极低 | 合适 |

### Ring vs Crossbar 作为 Cluster 内互连

| 指标 | Ring (N=4) | Crossbar (N=4) |
|---|---|---|
| Avg Hop | 1.0 | 1.0 |
| Max Hop | 2 | 1 |
| Bisection BW | 2W | 2W |
| Router Radix | 3 | 4 |
| 仲裁 | 分布式 | 集中式 |
| 面积 | 更小 | 稍大 |
| 适合 | 顺序流量（pipeline） | 随机流量 |

在 cluster 大小 ≤ 4 时，两者差别不大。Ring 在顺序 pipeline forwarding（如 systolic chain）时更自然；crossbar 在随机 all-to-all access（如共享 SRAM）时更好。

## 本页结论

torus 和 ring 都不是”更高级的 mesh 替代品”。torus 在小规模（≤4×4）且 bisection BW 需求强烈时可能值得，但 wrap-around link 的 pipeline + buffer + 死锁代价在大规模时会迅速侵蚀其逻辑优势。ring 几乎不适合作为全局数据网络，但在控制面、debug、同步等低带宽场景中是面积最优的选择。
