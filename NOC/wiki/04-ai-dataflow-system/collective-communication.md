# Collective Communication

上级：[AI Dataflow 系统视角](./README.md)

相关：[流量模式](./traffic-patterns.md)、[QoS、公平性与 Stall Taxonomy](../05-modeling-evaluation/qos-fairness-stall-taxonomy.md)

## 读这页前先统一几个词

- `unicast`：单源到单目的的普通点到点通信
- `broadcast`：一个源把同一份数据发给所有参与者
- `multicast`：一个源把同一份数据发给一部分参与者
- `fan-in`：很多源往少数目的汇聚
- `fan-out`：一个源向很多目的扩散

读 collective 时，最容易漏掉的一点是：问题不只是“总数据量大”，而是“同一时间很多流量会压到同一段路径”。

## 为什么 collective communication 需要单独讨论

很多 AI NoC 不是只处理点到点通信。  
一旦进入：

- 权重广播
- partial sum（部分和）reduce（归约）
- expert（专家模块）dispatch / gather（分发/收集）
- 多 tile（计算单元）同步

流量形态就会从 point-to-point 变成 one-to-many、many-to-one 或 many-to-many。

这类流量通常比普通 unicast（单播）更容易制造热点。

## 三类你必须重点掌握的 collective

### Broadcast（广播）/ Multicast（组播）

典型场景：

- 权重分发
- activation（激活值）分发
- 控制面同步消息

问题本质：

- 如果完全用 multiple unicast 实现，链路会被重复占用
- 靠近源端的路径段很容易成为热点

你需要比较两种方式：

- 软件复制 / multiple unicast
- 硬件 multicast 支持

第一版建模建议：

- 先用 multiple unicast 建上界
- 再用理想化的树形复制近似硬件 multicast 下界
- 对比两者差值，判断硬件 multicast 是否值得

### Gather（收集）与 Reduce（归约）

典型场景：

- 多 tile 结果收集
- partial sum accumulation 前的汇聚
- 某些 attention 或归约算子

问题本质：

- 多个源同时压向一个目的地
- sink 端口、ejection FIFO（弹出缓冲队列）、local SRAM（本地静态存储）写入口容易变成瓶颈

要先分清三件事：

- `gather`：只负责把多份数据收拢到一个目的地，不在网络里做合并
- `reduce`：在收拢过程中或收拢后，还要执行求和、最大值等结合运算
- `all-reduce`：先做 reduce，再把结果分发回所有参与者

关键要看：

- fan-in 大小
- 到达时序是否对齐
- 目的端是否能边收边消费

第一版建模建议：

- gather 先按 many-to-one unicast 建模
- 显式统计 sink ejection stall
- 如果要近似 reduce，可先用 `gather + endpoint aggregation（端点聚合）`
- 再评估是否值得加入 tree reduction 或分层 reduce

### All-to-all（全对全通信）

典型场景：

- MoE（混合专家模型）dispatch / gather
- 某些 tensor parallel（张量并行）交换
- 不规则 data redistribution

问题本质：

- 多个源与多个目的同时活跃
- routing（路由）、QoS（服务质量）、buffer（缓冲区）和端点都可能成为瓶颈

这是最接近“网络本体压力测试”的 collective 之一。

## 为什么 collective 对 AI NoC 特别敏感

普通 point-to-point 流量的问题，往往是局部链路竞争。  
collective 的问题则更容易演化成：

- 注入点热点
- 汇聚点热点
- 大范围同步阻塞
- 多 stream 相互等待

## 做架构探索时至少要问的 5 个问题

- 这种 collective 是高频还是偶发
- 是 latency-sensitive 还是 throughput-sensitive
- 是否可以通过 placement 减少通信扇出/扇入
- 软件复制是否已经够用
- 硬件支持的节省量是否大于增加的复杂度

## 与 QoS / traffic class 的关系

collective 流量很容易挤占普通流量，因此通常要考虑：

- control 是否需要更高优先级
- reduce response 是否需要优先于 bulk stream
- all-to-all 是否应与 memory response 隔离

否则你会看到“不是 collective 本身太慢，而是它把整个系统拖慢”。

## 第一版 simulator 至少要支持什么

- one-to-many traffic 注入
- many-to-one traffic 注入
- many-to-many traffic 注入
- per-destination ejection 限制
- 与普通 stream / DMA（直接内存访问）混合运行

## 什么时候值得做硬件 collective 支持

更有价值的场景通常是：

- 该 collective 出现频率高
- 链路重复占用非常明显
- 软件实现导致的热点很集中
- 它已经成为系统吞吐主瓶颈

如果只是偶发控制消息，往往不值得引入复杂硬件机制。

## 本页结论

collective communication 是 AI NoC 区别于很多传统片上互连的重要特征。  
在架构探索里，不应把它当成“特殊 corner case”，而应把它视作决定是否需要 multicast、reduce 支持以及 QoS 分层的重要主流量形态。
