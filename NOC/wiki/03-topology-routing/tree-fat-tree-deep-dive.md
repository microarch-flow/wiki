# Tree / Fat-Tree 专题

上级：[Topology 与 Routing](./README.md)

相关：[Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree](./topology-family-deep-dive.md)、[Collective Implementation 深化](../04-ai-dataflow-system/collective-implementation-deep-dive.md)

## 为什么 tree 家族值得单独看

tree 和 fat-tree 的价值，不主要体现在规则 tile 邻近通信，而更体现在：

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

## 本页结论

tree / fat-tree 在 AI NoC 里不是通用默认答案，但在 collective-heavy、强聚合型流量下，它们提供了与二维 mesh 很不一样的结构化思路。
