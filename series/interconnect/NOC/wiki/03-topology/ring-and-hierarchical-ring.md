# Ring And Hierarchical Ring

上级：[03 Topology](./README.md)
相关：[Crossbar And Concentrated Mesh](./crossbar-and-concentrated-mesh.md), [Topology Selection Framework](./topology-selection-framework.md)

## 这页在回答什么问题

ring 为什么在大规模全局数据面里常常掉队，却又会在控制面、小 cluster 和分层系统里反复出现；hierarchical ring 又是在救什么问题。

这类拓扑最大的特点不是“省”，而是“低 radix 和低结构复杂度非常诱人，但共享路径强得可怕”。

## Ring：最朴素的低-radix 闭环

一个双向 ring 的好处很干净：

- 每个节点只连左右两个邻居
- router radix 很低
- 控制简单
- 物理组织直观

在小规模系统里，这些优点非常有吸引力。尤其当流量本身更像链式传播、控制消息、或者低带宽同步时，ring 给出的“够用且便宜”的解很难忽视。

## Ring 的根本问题：横截面带宽不随规模长

ring 最大的结构短板是：bisection bandwidth 极弱，而且基本不随节点数增长。节点越多，更多端点在共享同一圈路径。

这带来的后果非常直接：

- average hop 很快变大
- 任何热点都容易沿整圈传播
- many-to-one 或 all-to-all 会迅速吃满主路径

所以 ring 不是不能扩，而是你每扩一次，都在让“共享一条大回路”这个本质变得更痛。

## 为什么它在很多 AI 芯片里又没有消失

因为很多实际系统并不要求它做全局数据面。ring 在下面几类场景里仍然很合理：

- 控制网络
- debug / telemetry 网络
- 小 cluster 内顺序流
- 分层互连中的局部子环

这些场景的共同点是：你更在乎实现成本和简单性，而不是全网高对分吞吐。

## Hierarchical ring 想解决什么

hierarchical ring 的出发点是承认单一大 ring 太脆弱，于是把它拆成几层：

- 局部 ring 处理局部通信
- 上层 ring 处理跨局部区域通信

这样做的好处是：

- 大部分局部流量不再占用全局一圈
- 全局路径长度被压住
- router 仍然可以保持较低复杂度

它的思想和 hierarchical NoC 很像，只是局部与全局都选用了 ring family。

## 它的代价也很明确

hierarchical ring 并不是“ring 的免费升级”。它会引入新的瓶颈位置：

- 局部 ring 与全局 ring 的 gateway
- 局部/全局切换时的流量汇聚
- 跨层流量的仲裁耦合

换句话说，你用分层减少了“大圈共享”的问题，但把压力重新集中到边界节点。

## Ring 和 crossbar 在小系统里的真实比较

4 个左右端点时，ring 和 crossbar 经常被放在同一候选池里。两者的关键差别不是“谁更现代”，而是流量形状：

- 若流量更像顺序传播、链式同步，ring 很自然
- 若流量更像任意端点随机访问共享 SRAM，crossbar 往往更好

所以 ring 常常不是被 mesh 打败，而是先在 cluster 内输给了 crossbar。

## Hierarchical ring 什么时候有现实吸引力

它常见的适用条件是：

- 端点很多，但局部通信明显更强
- 希望避免高-radix router
- 更重视规则和简单性，而不是最高 bisection BW

这使它在某些 control-heavy fabric、管理网络或带明显 locality 的分层系统里仍然有位置。

## 为什么它仍不是 NPU 全局主流

对于大规模 AI data plane，hierarchical ring 还是经常会输给 mesh / concentrated mesh，原因不是它不够巧，而是：

- 全局跨区带宽仍较弱
- gateway 热点难完全避免
- 对 bursty 或 all-to-all 流量不稳

这说明 ring family 更像“低复杂度工具箱”，不是大多数 NPU 通用数据面的默认骨架。

## 常见误解

常见误解：ring 不适合作为任何 AI 互连。  
实际上：它不适合作为大规模全局高吞吐数据面，但在控制面、同步面、小 cluster 内仍然很有价值。

常见误解：hierarchical ring 就是更简单的 mesh。  
实际上：它解决的是不同问题。mesh 更强调二维规则分布，hierarchical ring 更强调低复杂度分层闭环。

## 一句话理解

ring family 的价值在于低 radix 和简单性，代价是强共享路径；hierarchical ring 通过分层缓解共享，但会把压力重新集中到边界节点。

## 建模启示

对 ring，最小模型至少要保留：

```text
ring_size
average_hops
bisection_links = 2
```

对 hierarchical ring，还要额外保留：

```text
local_ring_size
num_rings
gateway_bandwidth
gateway_queue
```

如果忽略 gateway，hierarchical ring 会被高估，因为它最核心的风险正是跨层汇聚点。  
如果 workload 主要是控制和同步，可以把流量建模成低注入率小包；如果要放进数据面比较，就必须把 burst 和 hotspot 明确带进去，否则 ring 的短板不会在模型里显现。
