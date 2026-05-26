# Taxonomy

上级：[01 Overview](./README.md)
相关：[Problem Statement](./problem-statement.md), [../04-routing-and-flow-control/routing-algorithm-classes.md](../04-routing-and-flow-control/routing-algorithm-classes.md)

## 这页在回答什么问题

NoC 应该按哪些正交维度拆开理解，才能避免把拓扑、路由、交换方式、流控、QoS 和 workload 这些属于不同层级的东西混在一起。

这不是为了分类而分类，而是为了后面做判断时不偷换问题。比如“mesh 好不好”是 topology 问题，“XY routing 好不好”是 routing 问题，“credit 麻不麻烦”是 flow control 问题，它们不能互相代答。

## 为什么 NoC 特别容易学乱

BUS 世界里，对象边界相对稳定：地址、数据、响应、仲裁、协议、bridge。NoC 世界里，很多词都在描述“通信”，于是初学者很容易把它们混成一层：

- topology 看起来在讲路
- routing 也在讲路
- switching 也像在讲怎么走
- flow control 也会影响能不能走

结果就是一句话里同时出现 mesh、wormhole、XY、credit、QoS，却不知道哪个词在回答哪个问题。这一页的目标就是把这些维度分开。

## 第一维：按系统目标分

最先要分的不是结构，而是网络在服务谁。

AI dataflow NoC 的主问题是高并发数据搬运、局部性利用、静态调度和吞吐稳定。CPU coherent NoC 的主问题是一致性事务、严格 ordering 约束、消息类别隔离和协议无死锁。memory-centric NoC 则更像围绕 request/response 与 memory service rate 组织的网络。

这个区分的重要性在于，它决定你后面应该优先关注什么。对 deterministic NPU，source routing、traffic shaping 和 worst-case latency 更值得优先建模；对 CPU coherent NoC，adaptive routing 是否收益更高、VN/VC 如何支撑一致性消息隔离，才是主战场。

常见误解：NoC 先是通用技术，再在 AI/CPU 上“做应用”。  
实际上：系统目标会反过来决定 NoC 的主矛盾，很多设计并不存在“脱离场景的最佳形式”。

## 第二维：按 topology 分

topology 回答的是“谁和谁物理相连”，本质是图结构问题。它直接影响：

- 平均最短路径长度
- 对分带宽
- router radix
- 线长与 floorplan 兼容性
- 多路径冗余度

mesh、torus、ring、tree、fat-tree、crossbar、concentrated mesh 都属于这一维。它们的比较核心，不是“谁更高级”，而是“在给定规模、给定物理约束、给定 workload 局部性下，哪种结构更匹配”。

为什么必须把 topology 单独拿出来？因为同一个 mesh 可以跑 XY、source routing、adaptive routing；同一个 ring 也可以用不同 deadlock 避免手段。把 topology 和 routing 写在同一层，会让你误以为“选了 mesh 就等于选了某种路由哲学”。

## 第三维：按 routing 分

routing 回答的是“从源到目的地允许走哪些路径，以及具体怎么选路径”。它不改变物理连接图，只在既有图上定义路径策略。

常见子类包括：

- deterministic routing
- oblivious routing
- adaptive routing
- source routing
- dimension-order routing

这里最重要的判断是：routing 的收益，永远受 topology 提供的路径空间约束。一个 path diversity 很低的网络，adaptive routing 的潜力就小；一个物理长线极贵的网络，source routing 即使可行，也可能在 header 编码和静态调度上引入额外代价。

对你的目标而言，这一维尤其关键，因为 deterministic NPU 往往偏爱 `deterministic + source-routed + analyzable` 的组合，而不是 `adaptive + congestion-reactive` 的组合。

## 第四维：按 switching 分

switching 回答的是“一个 packet 在中间节点是整包存、部分存，还是按 flit 流水推进”。这一维描述的是转发方式，不是路径选择方式。

主流分法：

- store-and-forward
- virtual cut-through
- wormhole

为什么单独列这一维？因为很多性能与面积 trade-off 实际上是从这里长出来的。wormhole 之所以成为片上 NoC 主流，不是因为它“名字酷”，而是因为它用更小 buffer 支撑更细粒度流水。代价则是路径资源占用时间拉长、HoL blocking 更尖锐，于是 VC 和 allocator 复杂度被抬上来。

也就是说，switching 经常决定 router 微架构问题，而不是 topology 问题。

## 第五维：按 flow control 分

flow control 回答的是“发送方如何知道下游能不能继续接收”。它处理的是安全前进条件，而不是如何选路。

常见做法包括：

- on/off 或 stop-and-go
- ready/valid 式短距握手
- credit-based flow control

这一维和 BUS 最容易被误类比。BUS 里你熟悉的是 `VALID/READY`；NoC 里你更常见的是 credit。两者都是 backpressure 机制，但不在同一层。BUS 上的 ready/valid 常常在一个通道、一个局部接口内闭合；NoC 上的 credit 需要跨多跳、多周期链路处理 buffer 可用性，因此必须显式计数和回传。

## 第六维：按资源隔离与服务策略分

这一维回答的是“不同流量是否共享完全相同的资源，以及共享时如何避免互相压死”。它包括：

- 单队列 / 无 VC
- VC 分离
- virtual network / plane 分离
- 多物理网络
- 优先级与仲裁策略

很多人会把 QoS 只理解成“高优先级先过”，这是 BUS 视角残留。NoC 上的 QoS 往往是复合机制：traffic class 决定语义层次，VC 决定逻辑隔离，仲裁策略决定局部资源分配，多物理网络决定是否进行硬隔离。只有把这些对象分开，你后面才说得清 “这个流为什么被 bulk DMA 淹没了”。

## 第七维：按 traffic pattern 与 workload 分

这一维回答的是“网络实际上在承受什么流量形状”。uniform random、hotspot、transpose、neighbor traffic，是 synthetic pattern；GEMM、prefill、decode、MoE 则是 workload-derived pattern。

这一维看似最晚，实际很早就该进入心智模型，因为 NoC 设计的很多优劣只有放回流量分布里才成立。ring 对邻近通信可能很好，对 all-to-all 可能很差；adaptive routing 对 bursty hotspot 可能有收益，对静态规整数据流可能反而破坏可分析性。

这也是为什么后面 `05-system-integration` 和 `06-ai-noc-specifics` 必须单独成章。没有 workload 维度，前面的结构和策略会变成静态图鉴。

## 一个更实用的记忆顺序

比起死背“七大维度”，更实用的顺序是：

1. 先问系统目标：这张网在服务什么机器
2. 再问 topology：物理上怎么连
3. 再问 routing：允许怎么走
4. 再问 switching 和 flow control：怎么前进、怎么停
5. 最后问 isolation 和 workload：谁和谁会互相压

这个顺序的好处是，前一层决定后一层的问题空间。你不会再问出“哪种 QoS 最适合 crossbar 还是 mesh”这类混层问题，而会先确定结构，再谈其上的策略。

## 和 BUS / RAM 体系的衔接

和 BUS 体系最重要的衔接点有两个。

第一个是 backpressure。BUS 里你更多从 channel handshake 和 outstanding 语义理解 backpressure；NoC 里要把它升级成“资源耗尽如何跨 hop 传播”的问题。两者的相同点是都在协调发送方与接收方节奏；差异在于 NoC 需要显式建模网络中间状态。

第二个是 QoS。BUS 里的 QoS 常围绕 master priority、channel arbitration 和 response fairness；NoC 里的 QoS 则会深入到 VC、traffic class、multi-plane 和 path contention。这不是 BUS 错了，而是 NoC 的共享资源层次更多。

和 RAM 体系的关键衔接点则是：NoC 的 traffic class 和热点，经常是被 memory subsystem 反推出来的。比如 [RAM 分类框架](../../../RAM/wiki/01-overview/taxonomy.md) 里讨论的 bank 组织、以及 [把 register、cache、scratchpad、DRAM、HBM 看作一个系统](../../../RAM/wiki/07-system-architecture/memory-hierarchy-as-system.md) 里强调的层次角色，会直接决定 request/response 的压力分布。bank parallelism 不够、controller return path 偏置、HBM port placement 不均，这些问题都会在 NoC 上表现为特定拓扑区域或 response path 的拥塞，而不会体现在 topology 名词本身。

## 常见误解

常见误解：topology 和 routing 不需要强拆，反正最后都一起决定延迟。  
实际上：两者确实共同影响结果，但设计自由度不同；不拆开就无法说清“结构限制”与“策略限制”谁是主因。

常见误解：wormhole、credit、VC 都属于 router 细节，不必放进 taxonomy。  
实际上：它们虽然落在 router 内部，但分别属于 switching、flow control、resource isolation 三个不同维度，混在一起会直接污染建模边界。

## 一句话理解

NoC taxonomy 的目的不是列百科，而是把“谁在服务谁、怎么连、怎么走、怎么停、谁会互相压”拆成正交问题，从而让后续判断不混层。

## 建模启示

taxonomy 对建模最直接的价值，是把配置参数分组。一个最小配置草图可以写成：

```text
NoCConfig {
  system_goal
  topology
  routing_policy
  switching_policy
  flow_control_policy
  isolation_policy
  traffic_model
}
```

第一版 analytical 或 event-driven 模型，至少应让这几个字段是分开的，否则你后面做参数扫描时会出现“改了一项，实际上同时改了三项”的伪结论。

更具体一点，如果只关心 topology 对平均 latency 的影响，可以暂时把 `switching_policy` 固定为 `wormhole`、把 `flow_control_policy` 固定为 `credit`。如果要验证 deadlock-free 性质，就必须把 `routing_policy` 与 `isolation_policy` 联合展开，显式记录 `vc_class`, `allowed_turns`, `dependency_edge(src_vc, dst_vc)` 这类状态；否则你根本无法判断是结构无解，还是策略无解。
