# NoC 高频问题：怎样避免常见误判？

<span id="high-frequency-questions"></span>

上级：[10 查阅与练习](../SUMMARY.md#09-reference)；原章节：[09 Reference](./README.md)

相关：[NoC 术语表](./glossary.md)、[设计决策路径](./noc-design-decision-tree.md)、[练习与参考解答](./exercises-and-worked-solutions.md)

<span id="这页在回答什么问题"></span>每个问题先给短答，再链接到机制或案例。短答用于定位问题，不能替代具体系统的约束和证据。

## 高频问答

### 1. NoC 是不是“更高级的总线”？

不是简单的升级关系。总线可以指共享连接结构，也可以指一组接口与事务规则；NoC 描述网络式互连及其资源组织。两者可以组合，例如通过 NoC 承载 AXI 事务，仍要处理接口协议与完成语义。[总线、Crossbar 与 NoC](../01-overview/bus-vs-noc-vs-crossbar.md)

### 2. credit 能不能解决 deadlock？

不能。正确执行的 slot credit 契约限制发送端预留的下游槽位，但不自动消除资源循环等待。信用为零也不表示下游此刻的物理 FIFO 一定已满：返还信用可能仍在途。[Credit 与反压](../02-router-microarchitecture/credit-based-flow-control.md)

### 3. VC 的价值是不是只是提高吞吐？

不是。适当的 VC、路由和资源映射可以缓解部分队头阻塞，也可用于流量隔离或某些无死锁设计。VC 仍共享物理带宽；只增加 VC 数量不自动保证吞吐、隔离或前进。[VC 基础](../02-router-microarchitecture/virtual-channel-fundamentals.md)

### 4. XY routing 为什么这么常见？

固定的维度顺序便于实现和分析。在无故障、非环绕二维 Mesh 等明确条件下，它可以消除所建模的一类路由通道依赖环。Torus 环回、协议依赖、端点停顿和不公平服务需要另行检查。[维序路由](../04-routing-and-flow-control/dimension-order-routing.md)

### 5. source routing 是不是就不用仲裁了？

Source routing 决定路径。在共享 packet-switched 网络中，交汇流量通常仍需仲裁；预先验证的无冲突 TDM 或电路式方案可以不做动态仲裁，但要保证时隙、容量和时钟条件。[源路由](../04-routing-and-flow-control/source-routing-for-deterministic-systems.md)

### 6. adaptive routing 一定更好吗？

不一定。它可能让流量利用其他合法路径；静态偏斜和动态拥塞都值得比较，但效果取决于流量、路由选择及共享资源。替代路径可能增加跳数、硬件和验证成本。[自适应路由](../04-routing-and-flow-control/adaptive-routing-tradeoffs.md)

### 7. 为什么 link 利用率不高，系统还是慢？

平均值可能掩盖某条热点链路或某段突发；也可能是 NI、ejection、memory 或依赖限制了发送与消费。先固定观测窗口、链路方向和完成边界，再结合各资源的等待及服务事件判断。[性能界与瓶颈](../07-evaluation-methodology/performance-bounds-and-bottlenecks.md)

### <span id="8-decode-和-prefill-为什么必须分开讨论"></span>8. Decode 与 prefill 应分别说明什么？

它们的任务依赖和可并行程度可能不同。Prefill 不一定只受吞吐限制；decode 也可能受到 KV 数据带宽或端点服务限制。应给出序列长度、batch、映射及测量边界。[Prefill](../06-ai-noc-specifics/workload-attention-prefill.md) · [Decode](../06-ai-noc-specifics/workload-attention-decode-kv-cache.md)

### <span id="9-moe-为什么比-gemm-更折磨-noc"></span>9. MoE 一定比 GEMM 更难传输吗？

不一定。MoE 的 token 分配可能形成不均匀 dispatch/gather；GEMM 的广播、归约或映射也可能形成热点。需要比较实际通信矩阵、端点放置和资源，不能从算子名字推出结果。[MoE 案例](../06-ai-noc-specifics/workload-moe-routing.md) · [GEMM 案例](../06-ai-noc-specifics/workload-gemm-on-noc.md)

### <span id="10-ai-芯片为什么经常既要-bus-又要-noc"></span>10. BUS 与 NoC 只能分别负责控制和数据吗？

不能这样限定。控制、状态、请求、响应和大块数据都可能通过不同互连承载；接口协议和 NoC 也可组合。应按事务语义、目标服务和具体资源判断。[总线、Crossbar 与 NoC](../01-overview/bus-vs-noc-vs-crossbar.md)

### 11. NoC 模型是不是一上来就该做 cycle-accurate？

不一定。先看问题需要哪些资源和时间细节。事件驱动是推进方式，不自动等于粗粒度；它也可以按指定契约模拟逐拍 flit、credit 和仲裁。[模型粒度](../07-evaluation-methodology/modeling-layers-analytical-event-cycle.md) · [事件推进](../08-simulator-construction/event-driven-vs-cycle-accurate.md)

### 12. 第一版 simulator 最该先验证什么？

先固定输入、状态和时间口径，再按已实现能力验证单包顺序、slot 守恒、反馈可见点与端点完成。加入多包 VC 分配或仲裁后，再增加对应竞争与释放场景。[验证场景](../08-simulator-construction/verification-and-calibration.md)

### 13. QoS 是不是 fixed priority 就够了？

Fixed priority 可以满足某些已约束流量的目标，但策略名字本身不证明低优流前进或端到端延迟有界。要检查输入突发、非抢占时间、每段服务和接收端条件。[端到端服务保证](../04-routing-and-flow-control/service-guarantees-and-latency-bounds.md)

### 14. 为什么地址映射也会成为 NoC 问题？

地址映射影响请求到达哪个目标，路由和 placement 再决定它使用哪些资源。改变交织或数据位置可能改变流量分布；是否形成热点需要结合并发访问和端点能力分析。[地址映射与路由](../05-system-integration/address-map-and-routing-table.md)

### <span id="15-为什么很多-ai-noc-倾向-deterministic-static-scheduling"></span>15. 静态调度什么时候值得考虑？

当流量、资源和时间约束可预测时，可以比较静态调度与动态仲裁。静态方案仍需验证运行时偏差、冲突、时钟和端点服务；流量不规则时，也可以采用部分静态、部分动态的混合方式。[确定性与静态调度](../06-ai-noc-specifics/deterministic-noc-and-static-scheduling.md)

<span id="一句话理解"></span><span id="建模启示"></span>先将问题还原为对象、资源和事件，再到对应正文检查结论成立的条件。
