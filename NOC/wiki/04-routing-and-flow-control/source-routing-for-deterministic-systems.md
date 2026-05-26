# Source Routing For Deterministic Systems

上级：[04 Routing And Flow Control](./README.md)

相关：[Routing Algorithm Classes](./routing-algorithm-classes.md)、[Tile Architecture And NOC](../06-ai-noc-specifics/tile-architecture-and-noc.md)、[Compiler NOC Co-Design](../06-ai-noc-specifics/compiler-noc-co-design.md)

## 这页在回答什么问题

这页回答：为什么 deterministic NPU 经常偏爱 `source routing`，以及它到底是在简化硬件，还是在把复杂度转移给编译器和系统软件。

## 定义

`source routing` 指的是：路径不是在每跳 router 内部临时算出来，而是在源端、NIC、编译器或 runtime 一侧预先决定，再通过 header、route id 或 route table 告诉网络“这包该怎么走”。

它和单纯 deterministic routing 的区别在于控制权位置：

- deterministic per-hop routing：路径规则在每个 router 本地实现
- source routing：路径由源端或软件先规划，再交给网络执行

## 为什么 deterministic NPU 喜欢它

AI 芯片的很多关键通信具有三个特点：

- `who talks to whom` 在编译期基本已知
- tile placement 与 memory placement 也大体已知
- 主流量会在同类算子上反复出现

这意味着系统往往有条件做下面这些事：

- 把 route planning 和 placement 一起优化
- 对主流量做静态冲突分析
- 让 router 尽量少做临场智能判断

source routing 的工程吸引力就在这里。

## 它带来的直接收益

### 路径行为更可控

对于特定 flow，编译器能明确知道：

- 会经过哪些 router
- 会竞争哪些链路
- 是否会跨 cluster 或 memory island

这对性能预测和问题归因很重要。

### 更容易和静态调度协同

如果系统本来就要做：

- DMA 计划
- collective 安排
- prefetch / refill 时序
- barrier / sync 排布

那么把 route 也纳入静态计划，会让“通信图”和“执行图”更一致。

### router 局部逻辑可以更轻

不一定意味着完全没有路由逻辑，但通常可以减少：

- 复杂地址译码后的候选选择
- 自适应拥塞探测
- 动态路径 tie-break

这对高频、低功耗 router 是有实际意义的。

## 它没有消失的复杂度

最常见误解是：source routing 让问题简单了。

更准确地说，它是把复杂度换了位置。

复杂度会转移到：

- 编译器 route generation
- route id / header encoding
- path conflict analysis
- deadlock-free path set 检查
- route 与 placement、memory map、workload schedule 的一致性维护

如果这些接口没有设计好，系统并不会更简单，只会更分散。

## 它仍然需要 VC 和仲裁

source routing 只决定路径，不消除共享资源竞争。

即使路径完全静态，仍然需要：

- VC 隔离不同 message class
- output arbitration 决定谁先过
- credit / buffer 机制限制发送速度

原因很简单：两条静态路径仍可能在某个链路或端口相交。

所以 source routing 绝不等于“不要仲裁”或“不要 flow control”。

## 它也不天然无死锁

如果静态路径集在 channel dependency 上形成环，source-routed 系统照样会 deadlock。

因此 deterministic 系统里常见的安全做法包括：

- 路径集本身遵守 DOR 或 turn restriction
- request / response / control 使用不同 VC
- 保留 escape VC
- 直接用多物理网络分离不同 traffic class

这说明 source routing 的正确问题不是“能不能预先写路径”，而是“预先写出的路径集是否安全且可执行”。

## 它最适合哪类流量

最适合 source routing 的通常是：

- 规则的 point-to-point tensor stream
- predictable gather/scatter
- 编译期可确定的 reduce tree
- DMA 与 local SRAM 之间的重复性搬运

不太适合完全依赖 source routing 的则包括：

- 强动态、运行时才出现的异常流量
- 不规则负载均衡或工作窃取
- 强依赖故障绕行的 fabric

这也是为什么很多系统会采用混合方案：主路径静态，边缘流量动态。

## 和 BUS 的差异

BUS 里的软件通常决定的是“什么时候发事务”，不是“事务在片上经过哪些中间资源”。NoC source routing 新增的能力在于：软件/编译器连中间路径都参与设计。

这使它更像“编译器和网络协同定义执行路径”，而不是单纯的软件调度。

## 一个现实判断

如果你的系统满足下面多数条件，source routing 往往值得优先考虑：

- 流量模式高度重复
- placement 由编译器掌控
- 主目标是稳定性和可验证性
- 你愿意在 compiler/runtime 侧投入工程

如果这些条件都不强，那么 source routing 的收益会下降，甚至可能变成维护负担。

## 一句话理解

source routing 不是“不做路由”，而是“把路径选择前移到源端或软件侧”，用更强的静态可控性换取更高的编译器接口责任。

## 建模启示

建模 source routing 时，最有效的抽象通常不是直接模拟 header bit，而是给每个 flow 一个 `route_id -> hop sequence` 映射。然后统计：

- route overlap
- per-link load
- per-class contention
- 与 placement 的耦合度

如果模型还要评估系统可行性，就必须再加两类检查：

- 静态路径集是否形成 channel dependency 环
- 不同 message class 是否被正确分到独立 VC 或物理网络

只有这样，模型才能回答“这套 source-routed 方案是否真的适合 deterministic 系统”，而不只是“路径写没写进去”。
