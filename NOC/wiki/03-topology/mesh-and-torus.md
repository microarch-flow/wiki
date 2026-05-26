# Mesh And Torus

上级：[03 Topology](./README.md)
相关：[Topology Design Metrics](./topology-design-metrics.md), [../04-routing-and-flow-control/dimension-order-routing.md](../04-routing-and-flow-control/dimension-order-routing.md)

## 这页在回答什么问题

为什么 mesh 在 NPU 上几乎总是 baseline，torus 又为什么常常在图论上更漂亮、在芯片上却没那么常见。

这两者的关系很典型：torus 看起来像“给 mesh 打补丁”，但补丁补掉的是边界效应，换来的是更长的物理线和更麻烦的资源依赖处理。

## Mesh：规则性比“理论最优”更值钱

mesh 的核心吸引力不是某个单一指标最强，而是它在很多维度上都不极端：

- 链路长度规则
- router radix 低而稳定
- 与二维 tile array 和 floorplan 自然对齐
- deterministic routing 很自然
- hotspot 位置可预测

这几个特点组合在一起，解释了为什么 mesh 特别适合作为第一版 simulator 的 baseline，也特别适合 deterministic NPU。你需要的是一个能被编译器、架构师和版图工程同时接受的结构；mesh 正好在这几个群体之间形成一个稳的交点。

## Mesh 的代价：中心区域会先累

mesh 的问题同样明确：

- 平均 hop 随规模上升
- 中心主干更容易形成热点
- 边缘 memory port 往往导致路径不均匀

以 4x4 mesh 为例，uniform random + 简单维序路由下，中心区域会承受更多穿越流量。这不是 routing 算法犯错，而是几何结构本身就让更多最短路径穿过中间。

所以 mesh 的核心 trade-off 可以概括成一句话：它用规整性和可落地性，换掉了更低的最短路径和更强的对分带宽。

## Torus：把边界接起来

torus 的直觉很简单：把 mesh 边界首尾相连，减少边角节点的天然吃亏，缩短最坏和平均路径。

图论上它通常带来：

- 更小的 diameter
- 更低的 average hop
- 更高的 bisection bandwidth

这些指标都是真优势，不是幻觉。但关键问题在于：torus 的新增边不是普通边，而是 wrap-around 长边。

## Torus 的真实代价在物理层

对片上系统，wrap-around link 很少只是“多几根线”。它经常意味着：

- 更长的 wire span
- 可能需要多级 pipeline
- credit round-trip 变长
- dateline 或额外 VC 的死锁处理

所以 torus 的逻辑 hop 优势，常常会被每一跳更重的物理代价侵蚀。

一个很典型的情况：

```text
4x4 mesh:
  normal hop = 1 tile pitch

4x4 torus:
  wrap-around hop = 3 tile pitches
```

如果全网时钟频率高、长线需要插 pipeline，那么 torus 的“少一两跳”并不自动等于端到端时间更短。

## 一个对比表

| 维度 | Mesh | Torus |
| --- | --- | --- |
| Average hop | 较高 | 更低 |
| Bisection BW | 较低 | 更高 |
| Router radix | 相近 | 相近 |
| Long wire cost | 低 | 高 |
| Deadlock handling | 简单 | 更麻烦 |
| Floorplan friendliness | 高 | 中到低 |

这个表恰好说明为什么 torus 在 HPC 和大系统文献里很吸引人，但在片上 NPU 上常常不是默认选项。它的优势更多体现在纯网络指标，mesh 的优势更多体现在“图指标和物理实现之间更一致”。

## Mesh 什么时候特别合适

mesh 常见的适用条件：

- workload 规整或局部性明显
- 编译器能把强依赖 tile 摆得较近
- memory port 数量适中，且可较均衡分布
- 更重视可建模和物理实现稳定性

这基本就是很多 AI accelerator 的现实画像。

## Torus 什么时候值得认真考虑

torus 值得认真考虑的场景通常更苛刻：

- 规模不算太大，wrap link 还没长到不可收敛
- 跨区高并发流量很强，bisection BW 很重要
- 你愿意为长线 pipeline 和额外 VC 付成本

也就是说，torus 更像“有明确指标压力时的针对性增强”，而不是 NPU 的自然起点。

## 为什么 NPU 上 mesh 几乎一统天下

不是因为 mesh 在所有指标上都最强，而是因为它最少把问题隐藏起来。它的长处和短处都很直观：

- 编译器容易理解路径结构
- 架构探索容易看热点
- 版图团队不会突然收到高风险 wrap link
- cycle-level 模型更容易和物理直觉对齐

对 deterministic NPU，这种“行为稳定、边界清晰”的价值，往往比图论上的少量 hop 改善更重要。

## 常见误解

常见误解：torus 一定是 mesh 的严格升级。  
实际上：它在图指标上通常更强，但在物理可实现性和死锁处理上更贵，所以不是严格支配关系。

常见误解：mesh 只是因为简单才被用。  
实际上：mesh 被大量采用，是因为它在规则性、可建模性、可收敛性和性能之间给出了极难替代的平衡点。

## 一句话理解

mesh 用规则几何换可落地和可分析，torus 用更短逻辑路径换更重的长线与依赖处理；NPU 通常更偏好前者的稳定边界。

## 建模启示

对 mesh，最小 analytical 模型通常只需要：

```text
per_hop_latency
average_hops
center_link_hotspot_factor
```

对 torus，除了这些，还应显式增加：

```text
wrap_link_extra_cycles
extra_vc_for_deadlock_avoidance
```

如果不把 wrap-around 的物理代价独立建模，torus 在模型里通常会被系统性高估。  
如果只做 routing 算法比较，mesh 可以先假设所有链路等价；torus 则不应这样做，因为“普通 hop”和“wrap hop”在片上很少同价。
