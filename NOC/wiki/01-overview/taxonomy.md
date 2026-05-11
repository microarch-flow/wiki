# NoC 分类框架

上级：[01 概览与问题定义](./README.md)

相关：[Topology 与物理布局](../03-topology-routing/topology-layout.md)、[Routing 与 Arbitration](../03-topology-routing/routing-arbitration.md)

## 为什么先做分类

学习 NoC 时，最容易把以下对象混为一谈：

- 拓扑
- 路由
- switching（交换方式）
- flow control（流控）
- protocol / message class
- workload traffic

更稳妥的方式是按正交维度拆开。

## 维度一：按服务对象分

- AI dataflow NoC
- CPU/cache coherent NoC（缓存一致性网络：当多个模块各自缓存同一地址的数据时，通过硬件协议保证所有副本始终一致，不会读到过期值。AI 加速器通常使用编译器管理的 scratchpad，不需要硬件一致性）
- memory-centric NoC
- control / management fabric

重点：

AI NoC 更像可编排的数据搬运网络；CPU coherent NoC 更像一致性事务网络。

## 维度二：按拓扑分

常见片上拓扑（覆盖绝大多数 AI 加速器实际设计）：

- mesh（网格）
- torus（环面，mesh 首尾相连）
- ring（环）
- tree / fat-tree（树 / 胖树）
- hierarchical mesh
- cluster-local crossbar + global NoC

其他在文献或特定场景中出现的拓扑：

- concentrated mesh（多个 tile 共享一个 router，减少 router 总数）
- flattened butterfly（更高 router radix 换更少 hop）
- 3D mesh / 3D torus（用于 3D 堆叠芯片）
- butterfly / Clos / Beneš（数据中心常用，片上偶尔出现）
- irregular / custom topology（根据特定 workload 定制连接）

重点：

拓扑决定平均 hop（跳数）、bisection bandwidth（对分带宽）、wire length、router radix（路由器端口数） 与 floorplan 兼容性。对 AI 加速器而言，mesh 是绝对主流 baseline，hierarchical mesh 是最常见的优化方向。

## 维度三：按路由方式分

- deterministic routing（确定性路由）
- dimension-order routing（维序路由，先 X 后 Y）
- source routing（源路由，路径由发送端指定）
- adaptive routing（自适应路由）

重点：

AI tile dataflow 往往更偏 deterministic 或 source routing，因为更容易被编译器利用和预测。

## 维度四：按 switching 方式分

- store-and-forward（存储转发，整包到齐再转发）
- virtual cut-through（虚拟直通，头到即可转发但需全包缓冲）
- wormhole（虫孔交换，按 flit 流水转发；注意：这是 1987 年由 William Dally 提出的经典网络交换概念，与 Tenstorrent 公司的同名芯片产品无关）

重点：

现代片上 NoC，尤其是面积敏感的 AI NoC，主流心智模型通常是 wormhole。

## 维度五：按 flow control 分

- ready/valid（就绪/有效握手）
- credit-based（基于信用的流控）

重点：

NoC 内长距离、多跳、多周期链路场景下，更常见的是 credit-based flow control。

## 维度六：按资源隔离方式分

- single queue / no VC（虚通道）
- VC-based separation
- virtual network / plane separation

重点：

VC 不只是”优化吞吐”，更承担协议隔离、避免 HOL blocking（队头阻塞） 与降低 deadlock（死锁） 风险的作用。

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
