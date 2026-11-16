# Credit 如何控制逐跳发送与反压？

上级：[02 路由器与逐跳流控](../SUMMARY.md#02-router-microarchitecture)；原章节：[02 路由器与逐跳流控](./README.md)

相关：[输入缓冲组织](./input-buffer-organization.md)、[虚通道基础](./virtual-channel-fundamentals.md)

<span id="credit-based-flow-control"></span><span id="这页在回答什么问题"></span>下游缓冲有限，而发送和反馈需要时间。发送端怎样知道自己还能安全地发送多少 flit？这里先解释一种**逐跳、按下游 VC 槽位计数**的 credit 协议。

## 先定义一次授权

<span id="flow-control-要解决的是安全前进条件"></span><span id="credit-的核心思路把远端状态变成本地计数器"></span>假设 R0 向相邻的 R1 发送，每个 credit 授权 R0 向 R1 的指定 VC 发送一个 flit：

1. 初始化时，根据协议建立可用 credit 数；本例假设 R1 的该 VC 为空，深度为 B，R0 持有 B 个 credit。
2. R0 成功发送一个 flit 时，预留 R1 的一个 slot，并扣除一个 credit。
3. R1 实际移出这个 flit、释放该 slot 后，生成一个返还 credit。
4. 返还信用到达 R0，并在约定的采样点可用后，R0 才增加可用 credit。

发送还要满足 VC 许可、仲裁和链路可用等条件。credit 为零表示**发送端没有可用授权**；它不证明下游 FIFO 此刻一定物理满，因为释放出的 slot 可能仍在等待返还信用。

<span id="credit-不是-ack"></span>这个 credit 表示一个下游 slot 可以再次使用，不表示 packet 已到最终目的端，也不表示事务完成。下游 VC 能否分配给新包是另一项状态，见[虚通道的三种状态](./virtual-channel-fundamentals.md#一个包在-vc-上持有哪些状态)。

## 信用守恒

假设单条链路、一个固定深度的下游 VC，初始正反向管线为空；每次发送预留一个 slot，每次出队恰好产生一个返还 credit，且没有丢失、重复或其他预留。对同一个状态快照：

> **B = C + F + Q + K**

- B：下游 VC 的 slot 总数。
- C：发送端可用 credit 数。
- F：已预留 slot 的正向在途 flit 数。
- Q：下游 FIFO 中占用的 slot 数。
- K：尚未在发送端可用的返还 credit 数。

例如 B = 2、C = 0、F = 0、Q = 1、K = 1 时，下游 FIFO 有一个物理空槽，但该槽的授权还在返回途中，发送端仍不能使用它。这个等式只适用于上述契约；共享池、批量信用或其他预留需要相应扩展。

## 一个逐拍例子

<span id="credit-返回时机决定了-round-trip"></span><span id="典型数值例子"></span>假设 B = 2，发送方有足够长的包，下游每拍最多移出一个 flit。表中是每拍**开始时**的状态；动作在该拍结束时提交。

采用与[模拟器时序契约](../08-simulator-construction/router-pipeline-pseudocode.md#时间与快照契约)相同的边界：拍 0 发送的 flit 在拍 1 末到达下游，最早拍 2 出队；拍 2 出队产生的 credit 在拍 3 末到达，拍 4 才可用于发送。

| 拍初 | C / F / Q / K | 本拍动作 |
| --- | --- | --- |
| 0 | 2 / 0 / 0 / 0 | R0 发送 flit 0。 |
| 1 | 1 / 1 / 0 / 0 | R0 发送 flit 1；flit 0 拍末到达。 |
| 2 | 0 / 1 / 1 / 0 | R0 等 credit；R1 移出 flit 0；flit 1 拍末到达。 |
| 3 | 0 / 0 / 1 / 1 | R0 等 credit；R1 移出 flit 1；第一个 credit 拍末到达。 |
| 4 | 1 / 0 / 0 / 1 | R0 可发送 flit 2；第二个 credit 拍末到达。 |

每行四项之和都是 2。拍 3 时 R1 已有一个空槽，但 R0 仍须等待拍末返还。这里从拍 0 发送到拍 4 可用，credit 往返时间 R 为 4 拍。

## 窗口深度与发送速率

<span id="单-vc-持续满速时的-buffer-深度"></span><span id="推导单-vc-持续发送需要多少-slot"></span>假设单 VC 每拍都有 flit 待发，链路和下游每拍都能服务一个，且每次 credit 恰好在发送后固定 R 拍、仲裁前可用。要从头持续每拍发送，需要至少 R 个 slot。上例 R = 4、深度为 2，故拍 2 和 3 出现空拍。

多个 VC 可以共享链路。若两个 VC 都持续有数据、各有 2 个 slot，仲裁严格轮流，且各自的 credit 都在发送后第 4 拍可用，则拍 0–4 可依次发送 VC0、VC1、VC0、VC1、VC0。每个 VC 的深度都小于 4，链路仍可在此理想例子中保持每拍发送。

固定 R 且 V 个 VC 严格轮流时，每个 VC 的发送间隔为 V 拍，其窗口至少需要 ⌈R ÷ V⌉ 个 slot。这个容量条件不保证突发、不均匀仲裁、下游停顿或 credit 延迟波动下仍然满速。

<span id="r-的参数化分解"></span><span id="forward_link_latency"></span><span id="downstream_buffer_residency"></span><span id="credit_return_latency"></span><span id="合成"></span>R 包括正向传输、下游占用直到 slot 释放、返向传输以及信用何时可参与仲裁。各项只有在边界明确且不重叠时才能相加。拥塞和端点停顿可能增加下游占用时间；只用平均 R 不能证明最坏情况下无空拍。

## 反压怎样传播

<span id="backpressure-是怎样一级级传回去的"></span>如果目的端停止消费，邻近目的端的队列可能逐渐填满，上一跳随之用尽可用 credit。若上游继续提供足够多的数据，等待可以继续逐跳传播。传播时间取决于初始空槽、在途数据、链路时序和仲裁；流量不足时，阻塞可能不会到达源端。

credit 能帮助避免本协议下的缓冲溢出，但不能单独证明无死锁、无饥饿或有限完成时间。若下游可永久停顿，有限缓冲也不能给出有限等待上界。

## 与其他反馈方式比较

<span id="为什么长链路需要处理反馈延迟"></span><span id="和-bus-backpressure-的相同点与差别"></span>ready/valid 可以表达一次接口握手，也可以通过逐级寄存器和足够的缓冲处理反馈延迟。credit 以显式授权记录可发送的数量，也需要反向反馈、计数和正确的初始化。两者都是设计选择，不能按“总线”或“NoC”的名称排他划分。

<span id="credit-的主要代价"></span>例如 Arm AXI Issue L 描述了 valid/ready 和 AXI5 的 credited transport；不同协议的信用单位和规则应分别读取规范。[Arm AXI 规范，Issue L](https://documentation-service.arm.com/static/68b03beb01ae952d9559f9eb)

<span id="常见误解"></span>本页讨论的是相邻节点间的 slot credit。也存在跟踪远端接收缓冲的[端到端 credit 机制](https://cecs.uci.edu/~papers/esweek06/codes/p130.pdf)，不能直接套用本页的逐跳守恒范围。

<span id="建模启示"></span>按选定契约记录发送、下游入队与出队、credit 到达和首次可用时刻，并检查守恒。研究不同问题时可以采用逐拍或事件推进；关键是保留所需状态和时间边界，而不是强制选择某一种仿真引擎。

<span id="一句话理解"></span>逐跳 credit 用可追踪的授权管理下游缓冲；反压出现和消退的时间由整条反馈路径决定。
