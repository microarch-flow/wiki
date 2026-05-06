# Collective Implementation 深化

上级：[AI Dataflow 系统视角](./README.md)

相关：[Collective Communication](./collective-communication.md)、[MoE Case Study](./workload-moe-case-study.md)

## 为什么要从“总览”进一步进入“实现深化”

你已经知道 broadcast、reduce、all-to-all 很重要。  
下一步真正会影响架构判断的问题是：

- 软件实现够不够
- 硬件支持值不值得
- 哪种 collective 应该分层做
- topology 会不会放大或缓和 collective 成本

## 一：Software Replication vs Hardware Multicast

### Software Replication / Multiple Unicast

做法：

- 源端复制多份 packet
- 每个目的地单独走一条 unicast 路径

优点：

- 实现最简单
- 第一版 simulator 最容易支持

缺点：

- 靠近源端的路径重复占用严重
- 网络总流量明显放大

### Hardware Multicast

做法：

- packet 在网络中的某些节点复制
- 多个目的共享上游路径段

优点：

- 减少重复链路占用
- 对高频 broadcast 尤其有利

缺点：

- router / NI 复杂度上升
- credit、buffer、复制点管理更复杂

### 架构上怎么判断值不值得

最关键的问题不是“multicast 好不好”，而是：

- 这类 broadcast 是否高频
- 重复占用是否已经是主瓶颈
- 软件复制是否已经足够接近理想效果

## 二：Flat Reduce vs Tree / Hierarchical Reduce

### Flat Reduce

做法：

- 多个源直接往同一个 sink 发

优点：

- 实现最简单

缺点：

- sink ejection 压力大
- 近 sink 链路拥塞重

### Tree / Hierarchical Reduce

做法：

- 中间节点先做局部聚合
- 再逐层向上汇聚

优点：

- 减少热点集中
- 更容易和 hierarchical NoC 对齐

缺点：

- 需要中间聚合语义或额外 staging
- 延迟模型更复杂

### 何时更值得做分层 reduce

通常在下面场景更有价值：

- fan-in 很大
- 局部 cluster 本来就有共享资源
- sink 端已经明显成为瓶颈

## 三：All-to-all 对 Topology 的敏感性

all-to-all 对 topology 特别敏感，因为它会同时考验：

- bisection bandwidth
- routing 灵活性
- 热点分散能力
- 端点注入 / 弹出能力

这类流量下，某些平时看起来“够用”的 topology 会迅速暴露问题。

## 四：Collective 与 Hierarchical NoC 的天然耦合

hierarchical NoC 往往更适合：

- cluster 内 broadcast
- 局部 reduce
- 再向上层网络传递已聚合结果

所以一旦 workload 中 collective 占比高，flat mesh 与 hierarchical NoC 的优劣判断就会明显变化。

## 五：建模建议

第一版可以按“上下界”思路建：

- software replication：近似实现上界成本
- ideal shared-path multicast：近似硬件 multicast 下界
- flat gather：近似最简单 reduce
- hierarchical gather：近似带中间聚合的 reduce

只要你能比较这几者的差距，就足以判断硬件 collective 是否有架构价值。

## 六：你应该重点看的指标

- 源端附近链路利用率
- sink / ejection 压力
- 全网总 flit 数
- tail latency
- workload completion time

如果只是平均带宽变化不大，但 tail latency 和热点显著改善，这仍可能是高价值优化。

## 七：常见误区

- 认为所有 broadcast 都值得做硬件 multicast
- 认为 reduce 只是算子问题，不是 NoC 问题
- 认为 all-to-all 只靠加宽链路就能解决

这些判断通常都过于粗糙。

## 本页结论

collective implementation 的核心，不是把网络做成“功能越多越好”，而是用对比建模判断：哪些 collective 已经成为结构性瓶颈，值得用硬件或分层网络去专门优化。
