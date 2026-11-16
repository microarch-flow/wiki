# Flattened Butterfly 与 Dragonfly：高端口数网络怎样连接？

上级：[03 拓扑与物理组织](../SUMMARY.md#03-topology)；原章节：[03 拓扑与物理组织](./README.md)

相关：[拓扑设计指标](./topology-design-metrics.md)、[层次化与混合互连](./hierarchical-and-hybrid-topology.md)、[拓扑与物理实现](./topology-physical-realization.md)

<span id="flattened-butterfly-dragonfly"></span><span id="这页在回答什么问题"></span>Flattened Butterfly 利用同一维度内的直接连接减少部分路由器跳数；Dragonfly 把路由器组织成组，并设计组内与组间连接。它们的具体路径、端口数和物理代价必须由构造决定。

## 同一维度直连：Flattened Butterfly

<span id="它们共同的核心直觉用更高-radix-换更少-hop"></span><span id="flattened-butterfly-能借来的是什么"></span>以一个 3×2 的二维构造为例，路由器坐标为 (x,y)，x 为 0、1、2，y 为 0、1。同一行任意两个路由器直连，同一列任意两个路由器也直连。

<span id="可复现的连接例子"></span>因此，(0,0) 有三个网络邻居：(1,0)、(2,0) 和 (0,1)。若它另接一个端点，已连接双向端口数为 4。到 (2,1) 可以先到 (2,0)，再到 (2,1)，共两条路由器间边。该图有 6 个路由器、9 条双向连接，最短路径直径为 2。路径选择和实际延迟还取决于路由与链路实现。

[Flattened Butterfly 原始论文](https://people.eecs.berkeley.edu/~kubitron/courses/cs258-S08/handouts/papers/ISCA_FBFLY.pdf)给出了具体拓扑及其路由比较；[片上版本](https://icn.kaist.ac.kr/~jjk12/papers/2007CAL.pdf)进一步讨论集中端点和旁路连线。论文中的性能与能量结果来自其评估模型，不能直接推广到任意芯片。

## 分组连接：Dragonfly

<span id="dragonfly-能借来的是什么"></span>再构造一个小型例子：A、B、C 三组各有两个路由器，记为 A0、A1 等。每组内部两个路由器直连；组间连接为 A0—B0、A1—C0、B1—C1。每个路由器再接一个端点。

每个路由器有一个组内网络端口、一个组间网络端口和一个本地端口，共 3 个已连接双向端口。例如 A0 发往 C1，可以经过 A1、C0 再到 C1。组内和组间连接都直接连在路由器上，不要求全组只有一个独立 gateway。

在一种经典构造中，每组有 a 个组内全连接的路由器，每个路由器有 p 个本地端口和 h 个组间端口，则其端口数为 p + (a−1) + h。若每组与其余每组至少有一条直接组间连接，且每个组间端口只连向一个其他组，则组数 g 满足 g−1 ≤ a×h。具体连边仍决定距离、切面和流量分布。[Dragonfly 原始论文](https://www.cs.umd.edu/class/fall2019/cmsc714/readings/Kim-Dragonfly.pdf)

## 少跳数需要付出什么

<span id="片上系统里真正的问题高-radix-不是抽象参数"></span><span id="为什么芯片上不常直接落地"></span>更多路由器端口可能增加内部交换、仲裁和布线需求。较长的直接连接可能需要更强驱动或额外流水，但实际代价取决于布局、链路和电路设计。网络跳数减少，不保证端到端时延、面积或能耗同步减少。

<span id="最现实的使用方式把它们当参照系"></span>两种拓扑都可以是需要验证的候选，也可以作为结构对照。是否采用完整结构、局部增强，或其他方案，应由端点数量、流量、带宽目标和实现预算决定。路由对路径多样性的使用见[自适应路由](../04-routing-and-flow-control/adaptive-routing-tradeoffs.md)。

<span id="常见误解"></span><span id="一句话理解"></span>端口更多只说明连接选择发生变化，不能单独证明吞吐、延迟或物理成本更好。

<span id="建模启示"></span>先列出每个路由器的邻居及本地端点，再记录每条边的容量和物理代价。对 Dragonfly 同时记录组内、组间连接和路由；不要仅凭每组路由器数推导完整网络。
