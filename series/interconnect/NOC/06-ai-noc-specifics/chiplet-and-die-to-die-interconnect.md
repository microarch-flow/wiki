# NoC 网关与跨 Die 互连：请求怎样跨越边界？

上级：[05 端点与系统集成](../SUMMARY.md#05-system-integration)；原章节：[06 AI NOC Specifics](./README.md)

相关：[层次化与混合互连](../03-topology/hierarchical-and-hybrid-topology.md)、[事务拆分、顺序与完成](../05-system-integration/transaction-ordering-and-completion.md)、[封装内芯粒互连](../../D2D/README.md)

<span id="chiplet-and-die-to-die-interconnect"></span><span id="这页在回答什么问题"></span>跨 die 通信需要两端接口、协议和封装连接共同工作。对 NoC 分析来说，关键是找出片上网络与跨 die 接口之间有哪些队列、转换和服务边界。

## 网关怎样接住片上请求

<span id="跨-die-不再是多几-hop"></span>构造一个双 compute die 系统：A 和 B 各有片上网络，两者通过兼容的 D2D 接口通信。一次从 A 到 B 的读取可以经过：

1. A 的 NI 将请求送至本地 NoC，路由到 A 的网关。
2. 网关按所选接口接纳请求；根据实现，可能进行格式、位宽或时钟转换。
3. D2D 接口传输请求，B 侧接收并将其交给目的资源；数据和状态再按系统规定返回 A。
4. A 侧匹配返回并交付发起端。网关队列或远端资源受阻时，有限缓冲及相应流控可能使本地网络等待。

这只是可行构造。两侧不一定都有 NoC，也不一定使用同样的格式。CRC、replay、跨时钟和序列化是否存在，以及它们的粒度，都由所选协议和实现决定。D2D 接口也可以使用多条并行数据线；例如 [OCP BoW PHY 规范](https://www.opencompute.org/documents/bunch-of-wires-phy-specification-pdf)描述了其线和 slice 组织。

## HBM 路径与芯粒网关

<span id="为什么-ai-系统很容易碰到它"></span>另一种路径是 compute die 上的 NoC 接到 HBM controller 和 PHY，再访问封装中的 HBM。它同样跨越 die 和封装边界，但不能因此假设使用 UCIe，或假设 HBM 侧还有一个通用片上 NoC。

[封装内芯粒互连](../../D2D/README.md)说明协议与物理连接的区别；[HBM 封装](../../../storage/06-system-integration/packaging/hbm-2.5d-3d-tsv.md)讨论存储封装。不同技术的延迟、带宽和能量需要按具体实现和测量边界比较。

## 放置和调度要知道哪些资源

<span id="编译器和-placement-必须感知层次"></span><span id="为什么-deterministic-npu-更要谨慎"></span>跨 die 流可能集中经过少数网关或封装连接。改变计算和数据放置，可以改变这些资源的需求；但把通信留在本地也可能增加复制、容量或其他链路开销。

若静态调度依赖固定的完成时间，还需约束网关队列、各段服务、时钟关系、端点响应及异常处理。固定路径不自动消除排队或重传带来的波动。

<span id="工程上的直接结论"></span>比较候选方案时，分别列出片上路径、网关、跨 die 连接和目的端。只增加若干抽象 hop 可能足以做粗筛，但无法解释格式转换、共享网关、反馈或错误恢复。

<span id="建模启示"></span>按问题保留网关容量、队列、两侧流控、映射、时钟、可选可靠性机制和完成边界。逐项确认哪些延迟可以重叠；只有非重叠区间才能直接相加。

<span id="一句话理解"></span>跨 die 不只是改变距离；接口和网关引入的资源与语义，也会影响片上事务的前进。
