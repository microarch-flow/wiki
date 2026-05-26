# Reduction And Collective Networks

上级：[06 AI NOC Specifics](./README.md)

相关：[Broadcast Multicast Tree](./broadcast-multicast-tree.md)、[Workload GEMM On NOC](./workload-gemm-on-noc.md)、[Workload MOE Routing](./workload-moe-routing.md)

## 这页在回答什么问题

这页回答：当 AI NoC 里出现 gather、reduce、all-reduce、all-to-all 这类 collective 时，为什么不能再只用普通 point-to-point 直觉来思考网络。

## collective 的关键不是总量，而是形状

collective 最大的问题通常不是“字节总量特别大”，而是：

- one-to-many
- many-to-one
- many-to-many

这种空间结构会让热点更集中、同步更明显、端点压力更极端。

## gather 和 reduce 不是一回事

要先区分：

- `gather`：只是把数据收过来
- `reduce`：收过来的同时还要做结合运算

如果所有 partial sum 都直接冲向一个 sink，再在 sink 端算，这对网络和 endpoint 都很不友好。更好的方式通常是：

- endpoint aggregation
- tree reduction
- hierarchical reduction

它们的共同目标都是把压力从“一个最终 sink”往中间层分摊。

## all-reduce 和 all-to-all 更敏感

`all-reduce` 本质上是：

- 先 reduce
- 再 broadcast 回所有参与者

`all-to-all` 则更接近：

- 每个参与者都和很多其他参与者交换数据

这两类模式会同时考验：

- bisection bandwidth
- endpoint injection/ejection
- QoS 隔离
- topology 的 global traffic handling

## 为什么很多 AI 设计会做分层 collective

很常见的思路是：

- 先 cluster 内 gather / reduce
- 再 cluster 间交换更少的聚合结果

这背后的动机非常直接：

- 减少长路径上传输的数据量
- 把热点尽量局部化
- 让 NoC 和 cluster memory 结构协同

因此 collective-heavy workload 往往会把 flat mesh 和 hierarchical fabric 的优劣迅速放大。

## 什么时候值得上专用 collective network

通常在下面条件更容易成立时值得考虑：

- 某类 collective 高频出现
- multiple-unicast / flat gather 重复占用非常明显
- 端点或主干热点已经成为系统主瓶颈
- 软件实现与普通 data network 混跑代价太高

否则专用网络可能只是把少数流量问题硬件化，收益不够。

## 一句话理解

collective 网络关注的不是“能不能把数据送到”，而是“能不能别用 point-to-point 的方式把本来可以共享或聚合的流量做得极其浪费”。

## 建模启示

第一版模型至少要能表达：

- one-to-many
- many-to-one
- many-to-many
- endpoint aggregation
- hierarchical aggregation

然后比较：

- total flit count
- hotspot concentration
- sink / ejection pressure
- tail latency

这比只比平均带宽更接近 collective 的真实代价。
