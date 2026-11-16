# NoC 术语表：常见概念怎样区分？

<span id="glossary"></span>

上级：[10 查阅与练习](../SUMMARY.md#09-reference)；原章节：[09 Reference](./README.md)

相关：[传输单位](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)、[死锁、活锁与饥饿](../04-routing-and-flow-control/deadlock-livelock-starvation.md)、[高频问题](./high-frequency-questions.md)

<span id="这页在回答什么问题"></span>本页给出专题中常用词的简短口径。具体实现和推导以链接的正文为准；比较不同资料时，还要检查它们的统计边界和资源定义。

## 核心术语

### `packet / flit / phit`

- **Packet** 是网络承载的消息单位。一笔上层事务可以拆成多个 packet，请求和响应也可以分别传输。
- **Flit** 是 flow control unit。在 flit 级流控中，它是管理缓冲或推进传输的单位。
- **Phit** 是链路一次物理传输的单位。一个 flit 可以映射为一次或多次链路传输，取决于位宽、时钟和编码。

例如，16 B flit 经每拍传 8 B 的链路需要两次传输。这里忽略编码和空拍；具体格式见 [Packet、Flit 与 Phit](../02-router-microarchitecture/packet-flit-phit-hierarchy.md)。

### `wormhole`

Wormhole 允许 packet 的 flit 在不同节点间流水前进，不要求每跳先收齐整个 packet。资源不足时，包可能跨多个节点持有缓冲状态，反压随之传播。Wormhole 不要求每条物理链路都设置多个 VC。

采用 VC 的实现还要定义分配与释放策略。本专题的严格示例将 tail 离开本地 input 的上下文释放，与下游 tail free 返回后的 VC 许可释放分开。[转发与交换方式](../02-router-microarchitecture/wormhole-vs-vct-vs-store-forward.md)

### `credit`

Slot credit 是发送端已获得且尚未使用的下游槽位授权。发送时消耗授权；下游实际移出 flit 后生成返还，发送端要等 credit 到达并在约定时间可用。

Credit 不是下游此刻的物理空槽数：正向 flit 可能已预留槽位，返还 credit 也可能仍在途中。它与新包的 VC 分配许可是不同状态；正确执行 credit 契约可避免超出授权，但不自动排除死锁。[Credit 与反压](../02-router-microarchitecture/credit-based-flow-control.md)

### `VC`

Virtual channel 是共享物理通道的一组逻辑缓冲与控制状态。VC 可用于减少部分队头阻塞，或配合映射和路由规则隔离流量、避免某类死锁；它本身不保证带宽、无饥饿或隔离效果。

多个 VC 仍可能竞争同一链路、仲裁器或共享缓冲。Dally 的[虚通道流控论文](https://groups.csail.mit.edu/cag/PSRG/papers/dally-ieee92.pdf)区分了逻辑缓冲分配和共享物理带宽。

### VN、traffic class 与 HOL blocking

**VN**（virtual network）是按某种规则组织流量的逻辑网络。它与 VC 的映射由实现决定，不能直接假定一个 VN 等于一个 VC 或一张物理网络。**Traffic class** 是对流量语义或服务需求的分类；仅有标签不会自动改变资源分配。

**HOL blocking** 是队头阻塞：队首不能前进时，同一队列后面本可使用其他资源的项目也无法越过它。分开队列可能缓解这一现象，但共享的下游资源仍可能阻塞。[VC 基础](../02-router-microarchitecture/virtual-channel-fundamentals.md)

### `routing`

Routing 决定一个包允许使用的路径或下一跳候选。它受拓扑、目的、配置和实现规则约束。[路由算法分类](../04-routing-and-flow-control/routing-algorithm-classes.md)

### `arbitration`

Arbitration 在多个合格请求竞争有限资源时决定谁获得服务。例如，多个输入竞争一个输出端口；只要存在共享资源，就需要定义如何处理冲突。

### `QoS`

Quality of Service 描述所需的服务性质及其实现，例如带宽、延迟或公平性目标。优先级、VC 和预留时隙都是可能的机制。是否形成保证，取决于输入约束、整条路径和端点服务。[端到端服务保证](../04-routing-and-flow-control/service-guarantees-and-latency-bounds.md)

### `deterministic routing`

在给定配置和路由规则下，选路不随实时拥塞改变。路径固定不等于完成时间固定：仲裁、排队和接收服务仍可能变化。

### `source routing`

源端或上层预先选择路径，网络节点按携带的路径信息或约定表项执行。共享资源仍可能需要仲裁；经过验证的无冲突时隙表可以避免动态仲裁。[源路由](../04-routing-and-flow-control/source-routing-for-deterministic-systems.md)

### `adaptive routing`

选路使用运行时状态，例如可用 credit 或拥塞信息。它可能利用替代路径，也可能增加控制与验证成本；收益取决于路径、负载和约束。[自适应路由](../04-routing-and-flow-control/adaptive-routing-tradeoffs.md)

### `deadlock / livelock / starvation`

- **Deadlock**：某组参与者占有资源并相互等待，在所定义的后续行为中不能自行解除；其他部分仍可能前进。
- **Livelock**：相关组件持续活动，但目标操作始终不能完成。
- **Starvation**：某个持续等待服务的请求长期得不到所需机会，而其他请求可能继续获得服务。

有限时间未完成是需要调查的现象，本身不能证明永久不前进。[三类不前进](../04-routing-and-flow-control/deadlock-livelock-starvation.md#三类不前进)

### `injection / ejection`

**Injection** 是把数据从源端送入所定义的网络边界；**ejection** 是把数据从网络送到目的端边界。边界可以位于不同队列或接口，比较延迟时要写清楚。

网络到达不一定等于 consumer 接收，更不一定等于上层事务完成。[事务拆分、顺序与完成](../05-system-integration/transaction-ordering-and-completion.md)

### `memory-centric`

分析重点是存储请求、响应和端点服务的组织。它不意味着所有请求都在关键路径上，也不排除端点之间的其他流量。[NoC 与内存系统](../05-system-integration/noc-meets-memory-system.md)

### `collective`

Collective 描述一组参与者交换什么、谁得到什么结果，例如 Broadcast、Reduce、AllReduce 和 All-to-All。它可以用多个点对点消息、网络内复制或归约实现；通信语义不指定物理实现。[集体通信基础](../06-ai-noc-specifics/collective-communication-basics.md)

### Payload、wire 与 byte-hop

**Payload** 是所定义的有效数据量；**wire 字节**按所选链路格式计入头部和填充；**byte-hop** 将经过每条有向链路的数据量分别相加。三者的统计对象不同，不能直接互换。[流量 Trace 核算](../07-evaluation-methodology/trace-generation-worked-example.md)

### 完成事件与 stall

一次 flow 可以有释放、首次注入、网络到达、consumer 接收和上层完成等事件。它们各有时间戳；必须先指定哪个事件释放依赖。

**Stall** 是某对象在指定时间窗口内等待所需条件的记录。原因、统计对象和分母必须一起报告，不能只比较同名计数器。[Stall 分类与归因](../07-evaluation-methodology/stall-taxonomy-and-attribution.md)

## 最容易混淆的几组词

### routing vs arbitration

Routing 给出合法候选；arbitration 在竞争时决定获得资源的请求。路径相同的包仍可能等待不同时间。

### flow control vs deadlock avoidance

Flow control 管理发送与接收资源；deadlock avoidance 约束资源使用，防止进入所分析模型中的不可解除等待。后者不等于所有算法都必须消除静态依赖图中的每一个环。[逃逸资源](../04-routing-and-flow-control/deadlock-avoidance-turn-model.md#逃逸-vc-是什么)

### throughput vs utilization

Throughput 是在指定边界和时间内完成的数据量或任务数，单位例如 B/cycle、packet/s；utilization 是指定资源的已用服务能力占可用能力的比例。高利用率不一定带来高 payload throughput。[延迟与吞吐](../07-evaluation-methodology/metrics-latency-throughput-saturation.md)

### network bottleneck vs endpoint bottleneck

网络与端点都可能限制任务完成。链路、router、NI、ejection、存储端口和依赖可以相互耦合；定位时需要结合负载、等待与完成事件，而不是只看一个平均利用率。

<span id="一句话理解"></span><span id="建模启示"></span>术语只有和对象、资源及观察边界一起使用，才能在不同文章和实验之间保持同一口径。
