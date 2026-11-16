# Adaptive Routing Tradeoffs

上级：[04 Routing And Flow Control](./README.md)

相关：[Routing Algorithm Classes](./routing-algorithm-classes.md)、[Deadlock Avoidance Turn Model](./deadlock-avoidance-turn-model.md)、[Topology Design Metrics](../03-topology/topology-design-metrics.md)

## 这页在回答什么问题

这页回答：`adaptive routing` 什么时候真的有价值，什么时候只是把系统复杂度推高，却拿不到成比例收益。

## 它承诺的是什么

adaptive routing 的卖点很直观：

- 拥塞时不走那条正堵的路
- 把流量分散到更多链路
- 提升吞吐，降低热点

这在论文图上通常表现得很好，因为实验往往故意选了：

- path diversity 较高的 topology
- 高负载或不规则 traffic
- 能体现局部绕行收益的场景

这些前提如果不成立，收益就会明显缩水。

## 收益成立的前提

### 1. 必须真的有多条可用路径

没有 path diversity，adaptive 就无路可选。

在小 ring、严格树形、或局部布线很受限的网络里，router 即便知道前方拥塞，也可能没有可替代出口。

### 2. 拥塞必须是动态且局部的

如果热点来自长期静态映射，例如：

- 所有流都要过同一 memory port
- reduce 根节点固定在一个 cluster
- 某个 SRAM bank 永远偏热

那么 adaptive 只能在热点周围“重新排队”，很难根治根因。

### 3. 额外路径不能引入过高绕路成本

非最短路径意味着：

- 更多 hop
- 更高链路能耗
- 更长尾延迟
- 更多中间资源占用

如果绕路节省的等待时间还不如多出来的 hop 成本，adaptive 反而会亏。

## 它带来的真实代价

### 决策逻辑更复杂

router 不再只是按地址查固定规则，而要观察：

- 哪些输出可达
- 哪些满足 deadlock 约束
- 哪些 credit 充足
- 哪些拥塞更低

这会增加关键路径和状态量。

### 延迟更难预测

在 deterministic routing 下，同一个 flow 的路径稳定，延迟波动主要来自资源竞争。

在 adaptive routing 下，路径本身也变成变量，所以：

- 同一 flow 的 hop 分布可能变化
- hotspot 位置更难提前解释
- 99th percentile latency 更难设上界

### 验证和 debug 成本更高

更灵活的局部决策意味着：

- trace 更难复现
- 死锁/饥饿/livelock 边界更复杂
- QoS 是否真正生效更难判断

对于想做 deterministic NPU 的团队，这通常是很现实的工程成本。

## 为什么 AI NoC 往往更保守

AI 工作负载并不总是“随机 manycore 程序”。

很多关键流量其实是：

- 编译期已知
- placement 已知
- producer-consumer 图已知
- 在相同算子上会重复出现

这意味着很多优化空间更适合放在：

- placement
- source routing
- traffic class 分离
- 多物理网络分离
- collective 组织方式

而不是完全依赖 router 在运行时局部修补。

## 哪些场景更适合考虑它

adaptive routing 更像是这些场景的候选项：

- MoE、稀疏激活、动态工作窃取这类通信模式更不规则的系统
- 大规模 manycore 或 chiplet fabric
- 容错需求强，需要绕过故障链路或节点
- 背景流量和主流量叠加后呈现明显动态热点

此时静态路径规划的收益下降，adaptive 的灵活性才更可能兑现。

## 它和 QoS 的冲突

adaptive 不只是和 routing 有关，还会影响 QoS。

原因是：

- 低延迟类流量可能被导向不同路径
- 不同 class 之间的相对隔离边界变得更难静态推断
- 某些局部链路可能因 adaptive 汇聚而出现新的高优争用点

所以如果系统要求很强的 latency bound，仅靠 adaptive 往往不够，通常还要搭配：

- class-specific VC
- reserved network / plane
- escape path

## 一个更务实的比较对象

工程上，更有价值的比较通常不是：

- `XY` vs `fully adaptive`

而是：

- `better placement + XY`
- `source-routed static plan`
- `limited adaptive with escape VC`
- `separate control network + simple data network`

这些方案往往更接近真实设计空间。

## 一句话理解

adaptive routing 的价值取决于“有没有真实可用多路径”和“拥塞是不是动态到值得临场绕路”；否则它很容易只是增加复杂度。

## 建模启示

评估 adaptive routing 时，模型至少要输出四类结果，而不只是平均 latency：

- path diversity 的实际利用率
- 平均 hop 与尾 hop 分布
- 热点链路利用率变化
- 99th percentile latency 和 starvation 风险

如果这些结果里只看到平均吞吐略升，却伴随：

- hop 明显增长
- tail latency 恶化
- class isolation 变差

那 adaptive 在该系统里就未必是好交易。

更进一步，模型应把 adaptive 的收益和以下基线对照：

- 更优 placement
- 更深/更浅 buffer
- 不同 VC 划分
- 多网络分离

否则你不知道收益究竟来自 routing 本身，还是只是弥补了别处的设计不足。
