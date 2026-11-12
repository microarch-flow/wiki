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

## 维度二：按拓扑与网络组织分

拓扑是图结构（router/endpoint 怎么连），组织方式是分层策略（多张网络怎么叠、cluster 怎么分），两者正交——同一个芯片可以是 cluster 内 crossbar + cluster 间 mesh + 叠加一张 reduction tree overlay。

### 2a. 基础拓扑（Flat regular topologies）

描述 router 和 endpoint 的连接图结构，每个 router 地位对等。

- bus（共享总线，严格来说不算 NoC，但小规模 SoC 仍常见）
- ring（环，单向或双向）
- mesh（二维网格，AI 加速器绝对主流 baseline）
- torus（环面，mesh 首尾相连，直径更小但长绕线物理实现困难）
- tree（树，适合广播/规约/存储层级）
- fat-tree / Clos（胖树 / 折叠 Clos，高 bisection bandwidth；fat-tree 通过增加上层带宽缓解 root 瓶颈，本质是增强的 tree/Clos 网络）
- crossbar（交叉开关，小规模内单跳低延迟，面积随规模平方增长）

片上较少但文献中常见的拓扑：

- butterfly / omega / banyan（多级交换网络，介于 crossbar 和 NoC 之间）
- hypercube（n 维立方体，理论价值大但物理布局复杂）
- flattened butterfly（更高 router radix 换更少 hop）
- dragonfly（高 radix router 网络，系统级/机柜级更常见，片上较少但思想有参考价值）
- star / hub-and-spoke（特殊小系统或 hub-based design）
- 3D mesh / 3D torus（用于 3D 堆叠芯片）

深入阅读：[Topology Family 深化](../03-topology-routing/topology-family-deep-dive.md)、[Crossbar 与 Concentrated Mesh](../03-topology-routing/crossbar-concentrated-mesh.md)

### 2b. 层次化与集群化组织（Hierarchical & clustered organizations）

不是单一拓扑，而是多层互连的系统组织方式。AI 芯片因为 workload 有明显的通信局部性，几乎都采用某种层次化设计。

- hierarchical mesh（两级 mesh，如 cluster 内 2×2 mesh + cluster 间 4×4 mesh）
- concentrated mesh（多个 tile 共享一个 router，减少全局 router 数量）
- cluster-local crossbar + global mesh（cluster 内 crossbar 低延迟互连 + cluster 间 mesh 全局连通，最常见的 AI 加速器组织方式）
- cluster-local SRAM fabric + global NoC（cluster 内 SRAM 互连 + 全局 NoC）
- tree of meshes / mesh of trees（树和 mesh 的层次化组合）
- chiplet-local NoC + package-level interconnect（chiplet 内片上网络 + 封装级互连）

深入阅读：[Hierarchical NoC 深化](../03-topology-routing/hierarchical-noc-deep-dive.md)、[Crossbar 与 Concentrated Mesh](../03-topology-routing/crossbar-concentrated-mesh.md)

### 2c. 多网络组织（Multi-network organizations）

真实 AI 芯片通常不是只有一张 NoC，而是多张物理或逻辑独立的网络，分别服务不同 traffic class。

- data NoC（activation / weight 搬运，高带宽）
- control NoC（command / descriptor / barrier，低延迟低带宽）
- DMA / memory NoC（HBM ↔ SRAM 大块搬运）
- reduction / collective NoC（all-reduce、partial sum 汇聚）
- synchronization NoC（credit / semaphore / barrier）
- debug / profiling NoC（trace / performance counter 采集）

深入阅读：[多网络组织](../04-ai-dataflow-system/multi-network-organization.md)

### 2d. AI 专用通信 overlay（AI-specialized overlays）

叠加在 base NoC 之上的专用通信结构，服务 AI workload 中大量出现的非点对点通信模式。

- broadcast / multicast network（权重广播、activation 分发）
- reduction tree（partial sum 归约）
- systolic nearest-neighbor links（最近邻直连，不经过 NoC router）
- collective network（all-reduce / all-gather 专用）
- stream / dataflow channel（producer-consumer 专用通道）

深入阅读：[Broadcast / Multicast / Reduction 网络](../04-ai-dataflow-system/broadcast-multicast-reduction-network.md)、[Collective Communication](../04-ai-dataflow-system/collective-communication.md)

### 2e. 非规则与定制拓扑（Irregular & workload-specific）

真实芯片未必是完美规则拓扑，可能根据特定 workload 的流量特征定制连接。

- application-specific topology（根据特定 workload 定制连接图）
- heterogeneous-router NoC（不同位置的 router 有不同规格）
- asymmetric bandwidth NoC（不同方向/区域的链路带宽不对称）
- memory-centric NoC（以存储端口为中心组织的网络）

重点：

拓扑决定平均 hop（跳数）、bisection bandwidth（对分带宽）、wire length、router radix（路由器端口数） 与 floorplan 兼容性。对 AI 加速器而言，mesh 是绝对主流 baseline，hierarchical / concentrated mesh 是最常见的优化方向，多网络 + 专用 overlay 是区别于传统 SoC NoC 的关键特征。

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
