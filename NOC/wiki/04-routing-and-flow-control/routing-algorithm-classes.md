# Routing Algorithm Classes

上级：[04 Routing And Flow Control](./README.md)

相关：[Topology Selection Framework](../03-topology/topology-selection-framework.md)、[Dimension-Order Routing](./dimension-order-routing.md)、[Adaptive Routing Tradeoffs](./adaptive-routing-tradeoffs.md)、[Source Routing For Deterministic Systems](./source-routing-for-deterministic-systems.md)

## 这页在回答什么问题

这页回答：NoC 里的 routing 到底有哪些大类，它们分别把“路径选择权”交给谁，又各自换来了什么代价。

很多初学者会把 routing 只理解成“从 A 到 B 怎么走”。在架构层面，routing 更重要的意义是：

- 热点会不会集中在少数链路上
- 同一个 flow 的延迟是否稳定
- 编译器能不能提前规划通路
- 死锁和验证成本会不会失控

## 先统一分类维度

一个 routing 算法最核心的差异，不是名字，而是下面三件事：

- 候选路径集合有多大
- 最终选择是在源端决定，还是在每一跳局部决定
- 路径选择会不会依赖实时拥塞信息

按这三个维度，可以把常见算法先粗分成四类。

## 1. Deterministic Routing

`deterministic routing` 的定义是：给定 `src` 和 `dst`，算法总会产生同一类固定路径。

典型例子：

- XY / YX 这类 dimension-order routing
- ring 上固定顺时针或逆时针策略
- tree 上固定上行再下行

它的优势很直接：

- 路径唯一，易验证
- 延迟分布稳定
- 路由器局部控制逻辑简单
- 更容易和性能模型、编译器静态分析对齐

它的代价也很明确：

- 遇到热点链路时没有绕行能力
- 某些 `src-dst` 对会永久绑定到同一批链路
- path diversity 无法转化成实际收益

对 deterministic NPU，这是最常见的基线，因为它把系统行为收敛到一个可解释的空间。

## 2. Source Routing

`source routing` 的关键不是“路径固定”，而是“路径由源端或软件预先指定”。

区别在于：

- deterministic routing 往往由每跳 router 根据地址和本地规则决定下一跳
- source routing 由编译器、runtime 或源端 NIC 提前把路径写进 header 或 route table id

它常见于：

- 流量模式高度规整的 AI dataflow
- placement 已知、通信图相对稳定的 tile array
- 想把复杂性上推给编译器而不是放在 router 里的系统

source routing 的真正价值不是“省几个门电路”，而是让软件能把路径规划和 placement、DMA 调度、collective 组织一起看。

它的风险是：

- 静态路径集同样可能形成资源依赖环
- traffic 变化时鲁棒性较弱
- 编译器接口定义不清时，系统复杂度只是转移了位置

## 3. Minimal Adaptive Routing

`minimal adaptive routing` 仍然只允许最短路径，但在多条最短路径之间根据局部状态选择。

典型例子是在 2D mesh 上，从 `(0,0)` 到 `(3,2)` 时，不再强制只能先走 `X` 再走 `Y`，而是允许在“还保持最短 hop”的前提下动态挑选 `E` 或 `S`。

它的收益通常来自：

- 多条最短路径分担热点
- 对不规则 burst 更有弹性
- 不增加 hop 数，因此平均延迟成本相对可控

它的限制是：

- 如果 topology 本身 path diversity 很低，收益有限
- 如果 traffic 主要是静态规则流，热点往往来自全局映射而不是局部拥塞
- 仍然要处理 deadlock、乱序和公平性问题

所以它不是“比 XY 更高级”，而是“在存在多条短路径且 traffic 足够动态时，值得付更高控制复杂度”。

## 4. Non-Minimal / Fully Adaptive Routing

这类 routing 允许 packet 为了绕开拥塞而走非最短路径，甚至在局部做较激进的路径选择。

理论优势：

- 最大化 path diversity 利用率
- 对热点和故障绕行最灵活
- 在大规模高基数网络里潜在吞吐更高

现实代价：

- router 状态和决策逻辑更复杂
- 延迟可预测性更差
- 更容易引入 livelock、乱序和验证困难
- 如果物理布线已经很长，额外 hop 的能耗和尾延迟成本会很显著

对于片上 deterministic NPU，这类策略通常不会成为主干数据网络的默认选择，更常见于：

- 研究型仿真
- 极大规模或更通用的 manycore
- 容错/故障绕行需求强的系统

## 一个更实用的分类视角

工程上，与其问“我要不要 adaptive”，不如先问：

1. 我的 topology 是否真的提供了可用的多路径？
2. 我的流量模式是静态编排还是动态爆发？
3. 我的目标是平均吞吐，还是 tail latency 上界？
4. 我的验证预算能不能承受更复杂的局部决策？

如果这四个问题的答案分别是：

- 路径选择很少
- 流量高度规则
- tail latency 更重要
- 验证预算有限

那么 deterministic 或 source routing 往往更对路。

## 和 BUS 的类比边界

BUS 世界里常见的是“共享资源仲裁”，而不是“路径选择”。NoC 新增的核心维度就在这里：

- BUS 通常只是在一条固定共享通路上决定谁先用
- NoC 既要决定谁先用资源，也要决定 packet 究竟经过哪组资源

因此 NoC 的 routing 类比不了 BUS 的仲裁策略。仲裁是每个冲突点的局部决策，routing 是整个路径空间的全局约束。

## 常见误区

- 认为 source routing 天然比 deterministic routing 更灵活
- 认为 adaptive routing 一定吞吐更高
- 认为最短路径一定最优
- 认为 routing 只影响性能，不影响验证和系统接口

更准确的说法是：

- source routing 只是把路径控制权移到源端或软件侧
- adaptive 只有在 path diversity 和 traffic unpredictability 足够大时才有明显收益
- 非最短路径可能减少热点，但会增加 hop、能耗和尾延迟
- routing 直接影响 deadlock 处理、message class 隔离和编译器接口

## 一句话理解

routing algorithm 的本质差异，不是名字，而是“谁决定路径、可选路径有多少、是否依赖实时状态”。

## 建模启示

建模 routing 时，不要只给每个 `src-dst` 对一个固定 hop 数。模型至少要保留：

- 合法候选路径集合
- 路径选择的决策位置：source、per-hop、本地表驱动
- 选择依据：固定规则、route id、局部拥塞、全局状态
- 是否允许非最短路径

对 deterministic/source routing，第一版模型可以把路径直接编译成静态 route table。对 adaptive routing，至少要再引入：

- 每个输出方向的拥塞观测
- 选择 tie-break 规则
- escape VC 或死锁规避约束

否则模型会高估 adaptive 的收益、低估它的实现成本。
