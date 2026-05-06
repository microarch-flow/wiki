# NoC 分类框架

上级：[01 概览与问题定义](./README.md)

相关：[Topology 与物理布局](../03-topology-routing/topology-layout.md)、[Routing 与 Arbitration](../03-topology-routing/routing-arbitration.md)

## 为什么先做分类

学习 NoC 时，最容易把以下对象混为一谈：

- 拓扑
- 路由
- switching
- flow control
- protocol / message class
- workload traffic

更稳妥的方式是按正交维度拆开。

## 维度一：按服务对象分

- AI dataflow NoC
- CPU/cache coherent NoC
- memory-centric NoC
- control / management fabric

重点：

AI NoC 更像可编排的数据搬运网络；CPU coherent NoC 更像一致性事务网络。

## 维度二：按拓扑分

- mesh
- torus
- ring
- tree / fat-tree
- hierarchical mesh
- cluster-local crossbar + global NoC

重点：

拓扑决定平均 hop、bisection bandwidth、wire length、router radix 与 floorplan 兼容性。

## 维度三：按路由方式分

- deterministic routing
- dimension-order routing
- source routing
- adaptive routing

重点：

AI tile dataflow 往往更偏 deterministic 或 source routing，因为更容易被编译器利用和预测。

## 维度四：按 switching 方式分

- store-and-forward
- virtual cut-through
- wormhole

重点：

现代片上 NoC，尤其是面积敏感的 AI NoC，主流心智模型通常是 wormhole。

## 维度五：按 flow control 分

- ready/valid
- credit-based

重点：

NoC 内长距离、多跳、多周期链路场景下，更常见的是 credit-based flow control。

## 维度六：按资源隔离方式分

- single queue / no VC
- VC-based separation
- virtual network / plane separation

重点：

VC 不只是“优化吞吐”，更承担协议隔离、避免 HOL blocking 与降低死锁风险的作用。

## 维度七：按流量类型分

- read request / read response
- write
- tile-to-tile stream
- multicast / broadcast
- reduce / gather
- control / barrier / descriptor

重点：

真正影响架构探索结果的，往往不是单个 router 的局部参数，而是不同 traffic class 是否互相阻塞。

## 一句话记忆法

先问“谁在通信”，再问“怎么连”，再问“怎么走”，再问“怎么控流”，最后问“在什么 workload 下会堵”。
