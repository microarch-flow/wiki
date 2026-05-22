# 仲裁、顺序性与 Backpressure

上级：[02 基础对象与事务语义](./README.md)

相关：[地址、数据、响应与事务语义](./transaction-address-data-response.md)、[AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[AXI 五通道与 VALID/READY](../03-on-chip-protocol-families/axi-five-channels-handshake.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)、[争用、QoS 与可观测性](../05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

为什么 transaction 被拆成地址、数据和响应之后，系统还必须定义“谁先用资源、哪些完成顺序可见、下游不能接收时阻塞如何传播”。

## 三者解决的是同一个共享系统问题

上一页把 transaction 拆成地址、控制属性、数据和响应，是为了表达一次访问的生命周期。只要系统里同时存在多笔 transaction，这个生命周期就不再由单个 master 独占：地址要抢 decode 和目标端口，写数据要抢 data path，读数据和写响应要抢 return path，slave 和 bridge 还会因为有限 buffer 把压力传回上游。

仲裁、顺序性和 backpressure 分别回答三个问题：

- 仲裁：多个候选同时想用同一个资源时，谁获得下一次服务机会。
- 顺序性：多笔请求可以怎样重排，哪些完成顺序必须对 master 或软件可见。
- Backpressure：下游暂时不能接收时，上游应该在哪里停住，以及停住会传到多远。

这三者不是独立开关。仲裁决定排队位置，顺序性决定排队能不能绕过，backpressure 决定某个队列满了之后会不会把更远处的资源也停住。看似“带宽够但延迟异常”的问题，排查时要沿着这三类规则的组合展开。

## 仲裁不是选赢家，而是给稀缺资源定价

仲裁对象不是抽象的“整条总线”，而是某个具体稀缺资源：address accept slot、shared slave port、write data path、read return path、bridge 内部 FIFO 写口、memory controller command queue。不同资源可以有不同仲裁器，同一笔 transaction 也可能在生命周期里经历多次仲裁。

仲裁策略是在交换公平性、尾延迟和服务保证。fixed priority 可以让高优先级 master 获得更低等待时间，但低优先级流量可能长期拿不到 grant。round-robin 降低 starvation 风险，但无法表达 display、audio、real-time DMA 这类带服务期限的流量。weighted round-robin 或 QoS-aware arbitration 可以给不同流量分配份额，但需要权重、credit、aging 或 priority boost 等状态，验证成本也随之上升。

仲裁粒度同样关键。按 beat 或服务窗口仲裁更细，可以让短访问在资源窗口层面插入长 burst 的占用序列，降低短请求尾延迟；按 burst 仲裁实现更简单，也能减少切换开销，但一个 16-beat burst 会连续占用目标 data path 的 16 个 beat 窗口。对只需要 1 beat 的 MMIO read 或 interrupt controller read 来说，这 16 个窗口就是明确的排队成本。这里比较的是资源调度粒度，不是在声明所有协议都允许已接受的 burst data phase 被任意打断；协议边界会限制仲裁器能在哪些窗口重新选择服务对象。

下面是一个构造场景：DMA 正在写一个长 burst，CPU 同时发出一个短读请求，两者共享同一个下游端口。表里不是在规定某个协议的实现，只是展示“仲裁粒度”如何改变可见延迟。

| Cycle | DMA 写 burst | CPU 读请求 | 按 burst 仲裁结果 | 按 beat/窗口仲裁结果 |
|---:|---|---|---|---|
| 0 | 申请 16 beat | 申请 1 beat | grant DMA | grant DMA |
| 1 | beat0 使用端口 | 等待 | CPU 等待 | CPU 等待 |
| 2 | beat1 使用端口 | 等待 | CPU 等待 | grant CPU |
| 3 | beat2 使用端口 | 读数据准备返回 | CPU 等待 | DMA 继续 |
| 4-15 | DMA 继续 | 已完成或等待返回路径 | CPU 继续等待 | DMA 继续 |
| 16 | DMA burst 结束 | 才获得机会 | grant CPU | DMA 结束 |

这张表说明：平均带宽没有变，短请求的尾延迟却完全不同。建模时如果只记录“端口总带宽”，会看不到这种排队结构；至少要记录仲裁粒度、grant 状态、候选队列和每类请求占用资源的长度。

常见误解：仲裁只影响性能。实际上，仲裁也影响 forward progress；一个没有 aging 或公平性约束的优先级策略，可能让低优先级事务无法完成，进而卡住等待 completion 的软件或上游状态机。

## 顺序性决定可以释放多少并行度

顺序性定义的是“哪些重排合法”。它不等于“所有请求都按发出顺序完成”。在单一共享总线和阻塞式访问里，系统天然接近强保序；当协议演进到 pipeline、outstanding 和多返回路径后，可重排边界就必须显式写出来。更强的顺序规则让软件和外设更容易推理完成时机，但会压缩并行度；更弱的顺序规则可以隐藏慢 slave、长 memory latency 和不同路径延迟，但需要 ID、tag、barrier、fence、lock 或软件同步协议来约束可见行为。

一个最小例子：同一 master 发出两个读请求，`R0` 去慢速外设，`R1` 去低延迟 SRAM。如果系统要求这个 master 的读响应严格按发出顺序返回，`R1` 即使已经完成，也要等 `R0` 返回后才能对 master 可见。如果系统允许不同 ID 或不同 stream 乱序返回，`R1` 可以先完成，但 master 必须能把 response 匹配回原请求，软件也必须知道这种完成顺序是允许的。

| 请求 | 目标 | 服务时间 | 强保序下的可见完成 | 允许重排下的可见完成 |
|---|---|---:|---:|---:|
| `R0` | 慢速外设 | 20 cycle | cycle 20 | cycle 20 |
| `R1` | SRAM | 3 cycle | cycle 21 或更晚 | cycle 3 |

这个差异不是协议字段的小事，而是体系结构契约。CPU load/store、DMA descriptor、doorbell、interrupt status、cacheable 与 non-cacheable 访问，对顺序性的期望并不相同。硬件如果重排了软件以为强顺序的访问，会出现数据可见性错误；硬件如果把所有访问都强行保序，又会把慢路径延迟传播给本来能独立完成的快路径。

`barrier / fence / lock` 可以先理解为“给重排能力加边界”的机制。它们告诉系统：某些访问不能越过某个点，某些访问必须以独占或原子语义观察，某些 completion 必须在软件继续前已经可见。具体语义属于 ISA、协议和系统内存模型的共同约定，这里只需要记住一件事：顺序性不是附加说明，而是 transaction 能否被并行化的边界。

常见误解：保序只影响 correctness，不影响性能。实际上，保序会把本可独立完成的请求串起来；在有慢 slave、长 burst 或拥塞返回路径时，它直接决定尾延迟。

## Backpressure 是有限 buffer 的语言

Backpressure 不是异常状态，而是有限资源系统的正常流控语言。slave 忙、bridge FIFO 满、clock domain crossing 弹性缓冲耗尽、return path 没有被 master 消费，都需要把“现在不能继续接收”传给上游。协议可以用 `READY=0`、credit 耗尽、retry、wait state 或 request 队列满来表达这个事实。

关键点在于 backpressure 会传播。一个 response FIFO 满，可能让 slave 无法再生成新的 response；slave 无法生成 response，又可能不能释放内部 request slot；request slot 不释放，address channel 就不能继续接收；address channel 不接收，上游 master 的 outstanding slot 也不能释放。看波形时这只是几根 ready 信号拉低；看系统时它是一条资源依赖链。

下面的例子展示一个 4-entry bridge FIFO 如何把下游 stall 传回上游：

| Cycle | 下游接收 | 握手后 FIFO 占用 | 上游请求 | Bridge 对上游的反馈 | 结果 |
|---:|---|---:|---|---|---|
| 0 | 接收 | 1/4 | `VALID=1` | `READY=1` | 请求进入 FIFO |
| 1 | 停止 | 2/4 | `VALID=1` | `READY=1` | 继续吸收突发流量 |
| 2 | 停止 | 3/4 | `VALID=1` | `READY=1` | buffer 继续上涨 |
| 3 | 停止 | 4/4 | `VALID=1` | `READY=1` | FIFO 被填满 |
| 4 | 停止 | 4/4 | `VALID=1` | `READY=0` | backpressure 到达上游 |
| 5 | 接收 | 3/4 | `VALID=1` | `READY=1` | 压力解除一个窗口 |

这张表说明 buffer 可以吸收短暂抖动，但不能消除持续拥塞。FIFO 深度越大，backpressure 到达上游越晚，瞬时吞吐越平滑；代价是面积、功耗、可观测性和最坏排队延迟。把 FIFO 做深不等于解决拥塞，它只是把拥塞的可见位置推远。

常见误解：回压只是波形里的细节。实际上，backpressure 是资源不足的可传播信号；在存在环形依赖时，它还可能成为 deadlock 或 hang 的触发条件。

## 三者会互相放大

仲裁、顺序性和 backpressure 的危险之处在于组合效应。

如果仲裁器把 grant 长时间给了一个长 burst，短请求会排队；如果系统又要求同一 master 的响应强保序，短请求即使走的是快路径，也可能被前面的慢请求挡住；如果返回路径同时被另一个 master 的未消费 response 填满，下游 slave 可能停止接收新的 request，backpressure 再把地址侧也停住。

性能调优里看到的现象可能是“某个 master latency 抖动”，根因却可能在另一个路径的 response 未被及时消费；功能调试里看到的现象可能是“某笔写没有完成”，根因却可能是 ordering rule 让它等待一个更早的读 response。只看单个 channel 或单个 master，容易把系统级依赖误判成局部协议问题。

这也是为什么总线模型不能只建一个全局带宽数字。至少要保留三类结构：资源仲裁点、顺序约束边、backpressure 传播边。它们共同决定 transaction 从“请求被接收”到“completion 被消费”的时间距离。

## 一句话理解

仲裁决定共享资源先服务谁，顺序性决定哪些完成结果可以先被看见，backpressure 决定资源不足会沿着哪条路径传回去；三者共同决定 transaction 的尾延迟、forward progress 和可见行为。

## 建模启示

建模仲裁时，不要只给链路一个带宽参数。模型需要知道仲裁点在哪里、候选队列按 master 还是按目标划分、grant 是按 beat 还是按 burst 保持、优先级是否会 aging、QoS 或权重是否会改变服务顺序。对性能模型而言，请求大小、burst 长度、服务时间和 grant 历史比 payload 内容更重要。

建模顺序性时，需要把“可重排范围”显式写成规则：同 master 是否保序，同 ID 是否保序，读写之间是否能越过，不同目标是否能乱序完成，barrier/fence/lock 会阻断哪些请求。功能模型要检查这些规则是否被违反；性能模型要用这些规则判断快请求能不能绕过慢请求。

建模 backpressure 时，需要保留有限资源的占用状态：FIFO depth、outstanding slot、response queue、downstream ready、credit 计数、master 是否持续消费返回数据。持续的 `READY=0` 或 credit 归零不是孤立事件，而是依赖链上的一个节点；模型要能追踪它从下游传到上游的路径。

更抽象地说，一笔 transaction 在系统里不是沿着单线移动，而是在多个资源图之间切换：地址图决定路由和仲裁，数据图决定带宽占用，响应图决定 completion 和释放，顺序图决定哪些节点之间存在不可越过的边。模型只要丢掉其中任一类边，就会低估尾延迟，或解释不了 hang、starvation 和“平均带宽足够但业务超时”的现象。
