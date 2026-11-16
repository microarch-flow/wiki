# Topology Selection Framework

上级：[03 Topology](./README.md)
相关：[Topology Design Metrics](./topology-design-metrics.md), [../06-ai-noc-specifics/why-ai-noc-is-different.md](../06-ai-noc-specifics/why-ai-noc-is-different.md)

## 这页在回答什么问题

面对多种 topology，不应该按“谁更高级”选，而应该怎样从 workload、floorplan、memory placement 和 deterministic 需求反推。

这页的目标是把前面几页的知识压缩成一套决策顺序，而不是再做一轮家族总结。

## 第一步：先问流量长什么样

topology 从来不是脱离 workload 独立存在的。你至少要先分清：

- 主要是局部相邻流量，还是大量跨区流量
- 主要是 point-to-point，还是有明显 broadcast/reduce/all-to-all
- memory port 是否是全网主热点

如果这一步不做，后面的所有“好坏”都容易变成静态印象。

## 第二步：再问物理对象怎么摆

拓扑不是抽象图，它要服务真实对象的位置：

- tile array 是规则二维，还是有明显 cluster
- SRAM/HBM port 是均匀分布，还是集中在边缘
- 是否已有 chiplet / die 边界

这一层经常直接过滤掉一批“图上很强”的候选。因为一旦它和 floorplan 语义严重不对齐，后面只会一直为长线和不规则布局付补偿成本。

## 第三步：确定你在优化哪一类确定性

对 deterministic NPU，topology 选择通常不只是平均吞吐问题，还要问：

- 路径是否易于分析
- 热点是否可预测
- 静态调度是否容易约束

这会天然偏向：

- 规则结构
- 局部性清晰的分层结构
- 不太依赖复杂自适应路径选择的网络

所以 topology 选型会和 CPU coherent NoC 有明显不同。后者可能更愿意为 path diversity 和动态绕路买单；前者常更愿意为可分析性放弃部分自由度。

## 一套实用决策树

### 场景一：小规模、端点少、物理跨度小

优先问：crossbar 能不能在面积和频率上仍可接受。

如果可以，通常不必为了“网络感”强行上 mesh。  
如果不可以，再看是否需要 small ring 或 tiny mesh。

### 场景二：大规模二维 tile array，局部性明显

默认从 mesh 开始。  
如果 cluster 局部通信占比高，再看 concentrated mesh 或 cluster-local crossbar + global mesh。

这是大多数 NPU 最常见的分支。

### 场景三：全局跨区带宽压力很大

先问问题是不是：

- memory port placement 过于集中
- collective 子流量没有专用 overlay
- cluster 划分不合理

如果这些都排除了，再考虑是否需要更强的上层带宽结构，例如更分层的 topology，或者以 fat-tree / stronger gateway 为参照的增强设计。

也就是说，不要一看到 bisection 不够就立刻跳到 exotic topology，先检查是不是系统组织本身造成了假热点。

### 场景四：强 collective 子问题突出

优先考虑 mesh + overlay，而不是直接用 tree/fat-tree 替代主网络。

因为这通常更符合 AI 芯片的现实：通用流量和 collective 流量的最优结构不一样。

### 场景五：已有 chiplet / die 边界

优先考虑局部规则网络 + 明确 gateway / bridge，而不是试图维持一张全局统一 topology 的幻觉。

这时 topology 选型已经和 D2D 边界耦合，不应再只按单 die 的纯图指标决策。

## 一个简化的候选表

| 条件 | 更先考虑 | 谨慎考虑 |
| --- | --- | --- |
| 4-8 个局部端点 | Crossbar | Mesh |
| 规则二维大阵列 | Mesh | High-radix exotic topology |
| 强局部 cluster | Concentrated mesh | Flat everything |
| 强 reduce/broadcast | Mesh + tree overlay | Tree 直接做主网络 |
| 极强跨区 all-to-all | 上层带宽增强 / torus as reference | Ring |
| 控制/同步子网 | Ring | Full data mesh |

## 什么时候“理论更优”不该动你

如果某 topology 的优势主要来自：

- 更低 average hop
- 更高理论 bisection

但同时要求：

- 明显更长链路
- 更高 radix
- 更复杂布线

那么你应该先把它当参照上界，而不是默认候选。片上 NoC 很多时候输赢不在图指标，而在“能不能把图指标兑现出来”。

## 常见误解

常见误解：先挑一个最先进 topology，再让编译器去适配。  
实际上：对 deterministic NPU，通常是 workload、映射和物理对象先决定了 topology 的可行边界。

常见误解：mesh 是保守选项，应该尽量超越。  
实际上：mesh 之所以常是 baseline，不是因为保守，而是因为它在很多 NPU 的真实约束下本来就非常接近最优平衡点。

## 一句话理解

topology 选型的正确顺序是：先看流量，再看 floorplan，再看确定性需求，最后才比较家族名词。

## 建模启示

选型框架最适合落成一个候选评分器：

```text
TopologyCandidateScore {
  locality_fit
  floorplan_fit
  determinism_fit
  global_bandwidth_fit
  implementation_risk
}
```

在 architecture exploration 早期，不必精确到分值模型，但至少要让每个候选 topology 在这五个维度都被打标签。  
如果模型只记录 average hop 和 area proxy，你会系统性高估 exotic topology，低估 mesh / concentrated mesh 这类“图论没那么惊艳但非常贴实际”的方案。
