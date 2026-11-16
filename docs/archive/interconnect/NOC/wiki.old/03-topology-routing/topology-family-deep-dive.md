# Topology Family 深化：Mesh / Torus / Ring / Tree / Fat-Tree

上级：[Topology 与 Routing](./README.md)

相关：[Topology 与物理布局](./topology-layout.md)、[Hierarchical NoC 深化](./hierarchical-noc-deep-dive.md)

## 为什么要把 topology family 单独拆开

在概览页里，拓扑只是“候选名字列表”。  
真正做架构探索时，你需要知道每一类 topology 的：

- 典型优点
- 典型死角
- 更适合什么 workload（工作负载）
- 物理实现上最可能踩什么坑

## Mesh

### 核心特点

- 规则
- 易布局布线
- 易扩展
- 每个节点局部连接简单

### 优点

- 非常适合 tile（计算单元）array
- routing（路由）和建模都简单
- floorplan（芯片版图布局）兼容性强

### 缺点

- 平均 hop（跳数）会随规模上升
- 中心或主干链路容易形成热点
- 边缘 memory port（存储端口）布局会拉长一部分关键路径

### 适合什么

- 规则 tile array
- compiler 可预测流量
- 想先做第一版 NoC 模型

## Torus

### 核心特点

- 在 mesh 基础上加环回边
- 减少边界效应
- 增大 bisection bandwidth（二分带宽，将网络平分为两半时横跨切面的总带宽）

### 优点

- 平均 hop 通常优于同规模 mesh
- 边角节点不再天然吃亏

### 缺点

- 环回边可能是长链路
- 物理实现复杂度明显上升
- 长链路 pipeline latency（流水线延迟）会改变理论优势
- 环形信道依赖会增加无死锁路由设计难度，常需 dateline 或 escape VC 等额外机制

### 适合什么

- 更在乎逻辑 hop 而且愿意为长链路付代价的系统

## Ring

### 核心特点

- 结构最简单
- router（路由器）开销低
- 单路径感强

### 优点

- 面积低
- 验证简单
- 小规模系统很好用

### 缺点

- 扩展性差
- 延迟和带宽都容易随规模恶化
- 单环共享路径容易被热点拖死

### 适合什么

- 小规模 cluster（簇）内局部互连
- 控制面或较轻量子网络

## Tree

### 核心特点

- 自底向上聚合
- 天然有层级结构

在 AI 芯片里，tree 更常见的角色往往是 reduce / broadcast / collective 子网络，而不是完整替代通用主 NoC。

### 优点

- 很适合 gather（收集）/ reduce（归约）直觉
- 层级清晰

### 缺点

- 根或上层节点容易形成瓶颈
- 容错和负载均衡弱
- 对 all-to-all（全对全通信）不友好

### 适合什么

- 明显上收式流量
- 结构化聚合

## Fat-Tree

### 核心特点

- 在 tree 上增强高层带宽
- 目的是缓解上层收敛处的瓶颈

在 AI 芯片里，fat-tree 更像是一种“为聚合流量加厚上层带宽”的专用结构思路，而不是默认的通用主互连答案。

### 优点

- 对高并发通信更稳
- 比普通 tree 更能支撑复杂 traffic（流量）

### 缺点

- 交换结构更贵
- 布线、面积和功耗更重
- 在 on-chip 环境里不一定像网络交换那样自然划算

### 适合什么

- 对 bisection bandwidth 很敏感
- 流量聚合明显但不想让根节点太弱

## 怎么在 AI NoC 里理解这些家族

一个实用的顺序是：

- 先看 workload 是否规则
- 再看局部性强不强
- 再看 memory / collective（集合通信）是否主导

通常：

- 规则 tile array：mesh 很自然
- 强局部性：hierarchical 比单纯更换全局拓扑更有价值
- 强聚合 / reduce：tree 直觉更强，但要防上层热点
- 强 all-to-all：更看重 bisection bandwidth 和热点分散能力

## 不要只看逻辑 hop

一个很容易犯的错是：

- 看到 torus / fat-tree 平均 hop 更低
- 就直接认为它一定更好

更稳的做法是同时问：

- 物理线长如何
- pipeline link 要不要加
- router radix（路由器端口数）是否变大
- 长链路是否改写 credit round-trip（信用往返延迟）

## 第一版实验建议

至少做 3 组对比：

1. mesh vs ring：看小规模和大规模差异
2. mesh vs torus：看逻辑 hop 优势是否被长链路抵消
3. flat mesh vs hierarchical：看局部性是否比换 topology 更重要

## 本页结论

topology family 的核心，不是记住每一类名字，而是知道它们分别在 `局部性、聚合性、全局带宽、物理代价` 上代表什么取舍。  
对 AI accelerator 来说，真正高价值的往往不是追求最“高级”的拓扑，而是让拓扑与 workload 局部性和 floorplan 共同对齐。
