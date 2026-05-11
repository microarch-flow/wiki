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
