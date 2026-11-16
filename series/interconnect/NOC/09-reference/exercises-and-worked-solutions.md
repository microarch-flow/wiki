# NoC 练习与参考解答：怎样检查结论？

上级：[10 查阅与练习](../SUMMARY.md#09-reference)

相关：[NoC 术语表](./glossary.md)、[设计决策路径](./noc-design-decision-tree.md)、[检查清单](./checklists.md)

先按题设独立作答，再看后面的推导。以下数字都是教学构造，不是器件规格或硬件实测。改变传输格式、时间边界或资源约束后，需要重新计算。

## 练习

### 练习 1：一次传输有几个单位？ {#exercise-1}

一个 packet 的 payload 为 24 B，header 为 8 B，尾部信息已包含在 header 中。header 与 payload 可连续填入 16 B 的 flit，最后不足一个 flit 时补齐。物理链路每拍传输一个 64 bit phit，发送期间没有空拍，忽略编码和其他开销。

需要多少 flit、多少 phit 和多少个链路传输拍？这能否给出端到端延迟？

[查看解答](#answer-1) · [传输单位](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)

### 练习 2：空槽为什么不能立即发送？ {#exercise-2}

一个单跳、单 VC 连接的下游 FIFO 深度为 1。源端已取得**同一个 packet** 的 VC 许可，F0 和 F1 自拍 0 起都等待发送；最初只有一枚 slot credit。每拍最多发送和移出一个 flit，下游只要拍初 FIFO 非空就移出。

拍 t 发送的 flit 在 t+1 拍末进入 FIFO；拍 t 移出生成的 credit 在 t+2 拍末返回。所有决策读取拍初 S(t)，拍末到期的事件最早下一拍可用。没有其他流量或阻塞。

求 F0、F1 的发送拍和移出拍，以及两枚 flit 均移出、全部 slot credit 返回后的第一个拍初快照。拍 3 时 FIFO 已空，为什么源端仍不能发送？若只知道 credit 为零且 FIFO 为空，能否确定下一次发送拍？

[查看解答](#answer-2) · [时间与快照契约](../08-simulator-construction/router-pipeline-pseudocode.md#时间与快照契约)

### 练习 3：无路由死锁就能保证完成吗？ {#exercise-3}

在一个无故障、非环绕二维 Mesh 中，已证明所采用的 XY 路由通道依赖图无环。仲裁公平，但某个目的 consumer 可以永久停止接收。

仅凭上述条件，能否保证所有包最终交付给 consumer？如果不能，还缺什么条件？

[查看解答](#answer-3) · [三类不前进](../04-routing-and-flow-control/deadlock-livelock-starvation.md#三类不前进)

### 练习 4：加宽哪段资源？ {#exercise-4}

两个源在 t=0 各有一份不同数据，分别为 96 B 和 64 B。各自先经独立输入链路，再经同一条共享链路到同一个目的端。两条输入链路各为 16 B/cycle，共享链路为 16 B/cycle，目的端最多接收 20 B/cycle。所有数据都必须经过这些资源；初始没有在途数据，忽略包头及其他流量。

用每个资源必须服务的数据量给出完成时间下界。如果只将共享链路加宽到 32 B/cycle，新下界是多少？下界变化能否证明实际完成时间一定达到新下界？

[查看解答](#answer-4) · [性能界与瓶颈](../07-evaluation-methodology/performance-bounds-and-bottlenecks.md)

### 练习 5：有时隙就有端到端保证吗？ {#exercise-5}

单条链路的预留周期为 8 拍，拍号对 8 取余为 0 或 4 时，每个时隙恰好服务一个 flit。拍 1 初有一个 flit 到达，之前同类队列为空；链路及下游 credit 始终可用。一拍的服务从该拍开始到下一拍开始结束。

此 flit 开始服务前等待几拍，何时完成这次链路服务？预留容量是多少 flit/cycle？若扩展问题允许目的 consumer 永久停顿，能否只凭此时隙安排保证端到端完成？

[查看解答](#answer-5) · [端到端服务保证](../04-routing-and-flow-control/service-guarantees-and-latency-bounds.md)

### 练习 6：多目的 flow 何时完成？ {#exercise-6}

源节点 0 向目的集合 `{0,1,3}` 各交付相同的 24 B payload。本例选择本地目的 0 直接交付；目的 1、3 各展开为独立单播。远端 packet 的 payload 上限为 16 B，每 packet header 为 8 B，尾部信息包含在 header 中；header 和 payload 连续填入 16 B flit，不足补齐，忽略其他开销。

求远端 packet 总数、远端注入 payload、远端注入 wire 字节，以及三个 consumer 需要接收的 payload 总量。如果采用本专题 v1 的 all-consumer 完成规则，什么时候可以释放依赖该 flow 的后继？

[查看解答](#answer-6) · [注入、分包与完成](../08-simulator-construction/traffic-injection-and-tracing.md#多目的-flow-的完成)

### 练习 7：消费完成就是网络静止吗？ {#exercise-7}

使用[最小逐拍仿真实作](../08-simulator-construction/minimal-cycle-simulator.md)的默认条件：四个 router 的固定线形路径，一个三 flit packet，输入和 ejection 深度均为 4，正向延迟 1，consumer 每拍可接收。比较返回延迟分别为 1 和 3 的两次运行，其余条件不变。

两次的首 flit 注入拍、tail 进入 ejection 拍、consumer 接收 tail 拍分别是什么？全部 credit 和 tail free 首次返回的静止拍分别是什么？只观察到 consumer 已接收 tail，能否推出网络已静止？

[查看解答](#answer-7) · [验证场景](../08-simulator-construction/verification-and-calibration.md)

### 练习 8：共享树减少了多少传输？ {#exercise-8}

一个 2×2 Mesh 的源 S 位于 `(0,0)`，三个 consumer 位于 S、A=`(1,0)`、B=`(1,1)`。三个 consumer 需要相同数据；S 的本地交付不进入网络。发往远端的每份完整 packet 为 16 B wire，已包含全部线上开销。没有其他流量，路由按先 X 后 Y。

比较两种构造：分别向 A、B 单播一份；或者源只注入一份，在 A 所在节点交付并向 B 转发。后者假设网络支持所需复制和本地交付。分别求网络注入 wire 字节和有向链路上的 wire byte-hop；能否据此断定哪种方案完成得更快？

[查看解答](#answer-8) · [Mesh 与 Torus](../03-topology/mesh-and-torus.md) · [广播、多播与复制](../06-ai-noc-specifics/broadcast-multicast-tree.md)

## 参考解答

### 解答 1：传输粒度 {#answer-1}

线上内容为 24 + 8 = 32 B，恰好装入 **2 个 16 B flit**。链路每次传 64 bit，即 8 B，因此需要 **4 个 phit 和 4 个传输拍**。

这是指定单链路的传输工作量。路由、排队、链路传播和接收处理尚未给出，不能由此确定端到端延迟。

[返回题目](#exercise-1)

### 解答 2：slot credit 与物理空槽 {#answer-2}

记 C 为可用 credit、F 为正向在途 flit 数、Q 为 FIFO 占用、R 为返回在途 credit 数。表中数值是**拍末**快照，始终满足 1 = C + F + Q + R。

| 拍 | 主要事件 | C | F | Q | R |
|---:|---|---:|---:|---:|---:|
| 0 | 发送 F0 | 0 | 1 | 0 | 0 |
| 1 | F0 到达 FIFO | 0 | 0 | 1 | 0 |
| 2 | 移出 F0，生成 credit | 0 | 0 | 0 | 1 |
| 3 | credit 在途 | 0 | 0 | 0 | 1 |
| 4 | credit 返回 | 1 | 0 | 0 | 0 |
| 5 | 发送 F1 | 0 | 1 | 0 | 0 |
| 6 | F1 到达 FIFO | 0 | 0 | 1 | 0 |
| 7 | 移出 F1，生成 credit | 0 | 0 | 0 | 1 |
| 8 | credit 在途 | 0 | 0 | 0 | 1 |
| 9 | credit 返回 | 1 | 0 | 0 | 0 |

发送拍为 **0、5**，移出拍为 **2、7**；首个全部 credit 可用且两枚 flit 均已移出的拍初快照是 **S(10)**。拍 3 的物理 FIFO 虽空，授权尚在返回途中。只知道 credit 为零和 FIFO 为空，还缺在途事件及其可用时刻，无法确定下一次发送拍。本题不涉及下一 packet 的 VC 重分配。

[返回题目](#exercise-2)

### 解答 3：证明范围 {#answer-3}

不能保证。路由通道无环只覆盖所建模的路由资源依赖；consumer 永久停收会使目的端数据无法交付。还要约束端点最终接收、相关协议依赖、仲裁和其他资源的前进条件。

有限时间观察到阻塞，也不能单独证明永久死锁。要区分当前等待证据和对所有允许行为的证明。

[返回题目](#exercise-3)

### 解答 4：必要下界 {#answer-4}

| 必经资源 | 需服务数据量 | 原容量 | 时间下界 |
|---|---:|---:|---:|
| 源 0 输入 | 96 B | 16 B/cycle | 6 cycle |
| 源 1 输入 | 64 B | 16 B/cycle | 4 cycle |
| 共享链路 | 160 B | 16 B/cycle | 10 cycle |
| 目的端 | 160 B | 20 B/cycle | 8 cycle |

因此 T ≥ max(6, 4, 10, 8) = **10 cycle**。将共享链路加宽后，它的下界为 160/32 = 5 cycle，整体下界为 **8 cycle**。排队、流水、仲裁和交付规则仍可能使实际时间更长；下界变化不证明实际时间会达到它。

[返回题目](#exercise-4)

### 解答 5：局部服务和端到端 {#answer-5}

拍 1 初到达时，下一次预留服务在拍 4，等待 **3 拍**；这次链路服务在 **拍 5 初**结束。每 8 拍预留 2 个 flit 服务机会，预留容量为 **1/4 flit/cycle**；要用满还需有待服务流量。

这只约束题设中的单段服务。若目的 consumer 可以永久停顿，就不能单凭该时隙表保证端到端完成；还要约束下游与端点。

[返回题目](#exercise-5)

### 解答 6：分包与 all-of {#answer-6}

每个远端目的收到两个 packet，payload 分别为 16 B、8 B。加 header 并补齐后，分别占 **2、1 个 flit**，即每个目的 48 B wire。

两个远端合计 **4 个 packet、48 B payload、96 B wire**；三个 consumer 共需接收 **72 B payload**，其中本地 24 B 不经过网络。要保留 flow、目的和 packet 的身份，防止重复完成事件被重复计数。

按照本专题 v1，只有本地目的和两个远端目的的所需数据都被各自 consumer 接收，父 flow 才完成，依赖它的后继才可释放。这个 all-of 是 v1 的契约，不代表所有集体通信接口都采用同样的完成语义。

[返回题目](#exercise-6)

### 解答 7：完成与静止 {#answer-7}

| 返回延迟 | 首 flit 注入 | tail 进入 ejection | consumer 接收 tail | 首次协议静止 |
|---:|---:|---:|---:|---:|
| 1 cycle | 拍 0 末 | 拍 9 末 | 拍 10 末 | 拍 10 末 |
| 3 cycle | 拍 0 末 | 拍 9 末 | 拍 10 末 | 拍 12 末 |

两次 consumer 完成相同，但第二次最后的 credit／tail free 到拍 12 末才返回。仅观察 consumer 完成不能推出网络静止；还要检查待发队列、网络状态、在途消息及许可。这里没有其他工作负载事件；更一般的工作负载完成还需要另外检查。

这个程序只实现单 packet 固定路径。通过该例不能证明多包仲裁正确、任意网络无死锁或模型已与硬件校准。

[返回题目](#exercise-7)

### 解答 8：网络流量与完成时间 {#answer-8}

单播到 A 经过 1 跳，到 B 经过 2 跳；源各注入一份，所以网络注入为 **32 B wire**，链路工作量为 `16×(1+2) = 48 B·hop`。

共享树在 S→A 发送一份，并在 A 交付及向 B 转发一份。源注入 **16 B wire**，两条有向边各承载 16 B，共 **32 B·hop**。S 的本地交付不计入上述网络注入或链路流量。

共享树在本例中减少了注入和链路字节，但仍需检查复制、缓冲、仲裁及目的端服务。仅凭这两个流量数字不能确定完成时间。若 packet 大小、路径或复制位置变化，应重新计算。

[返回题目](#exercise-8) · [流量与性能界](../07-evaluation-methodology/performance-bounds-and-bottlenecks.md)
