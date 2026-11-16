# 05 端点与系统集成

上级：[NoC Wiki](../README.md)

相关：[04 路由、仲裁与服务保证](../04-routing-and-flow-control/README.md)、[DMA 与 NoC](../../../microarchitecture/DMA/wiki/05-system-integration/dma-and-noc.md)、[存储系统](../../../storage/README.md)

<span id="05-system-integration"></span><span id="这页在回答什么问题"></span>路由器和链路提供消息通路；端点还要产生请求、接收结果并遵守事务语义。本章沿任务、请求和返回路径，观察接口与系统资源怎样共同决定前进和性能。

## 本章入口

<span id="这一章的主线"></span><span id="本章其余正文"></span>

1. [BUS 与 NoC 的系统边界](./noc-vs-bus-revisited.md)：一次任务经过哪些控制、网络和完成边界。
2. [网络接口 NI](./ni-network-interface-design.md)：端点接口与网络消息怎样转换。
3. [地址映射与路由表](./address-map-and-routing-table.md)：地址怎样选择端点和路径。
4. [事务拆分、顺序与完成](./transaction-ordering-and-completion.md)：分片、匹配和响应怎样保持接口语义。
5. [Tile 与 NoC 的接口](../06-ai-noc-specifics/tile-architecture-and-noc.md)：计算与本地存储怎样影响注入和接收。
6. [DMA 与 NoC](./dma-engine-noc-interaction.md)：窗口、burst 和发起节奏怎样塑造流量。
7. [NoC 与存储系统](./noc-meets-memory-system.md)：bank、controller 与接收资源怎样限制一条路径。
8. [Memory-centric NoC](../06-ai-noc-specifics/memory-centric-noc.md)：多条流如何共享存储端口和返回路径。
9. [多网络与资源隔离](./multiple-physical-networks.md)：共享、预留与物理隔离怎样比较。
10. [芯粒与跨 Die 互连](../06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：片上网络如何衔接跨 die 接口。

<span id="为什么这章对-deterministic-npu-特别关键"></span><span id="读完这章后应该得到什么"></span>静态计划可以提前确定部分数据放置、目标和注入顺序；是否能按计划完成，还取决于缓冲、仲裁、端点服务和异常处理。阅读时分别标记数据到达、端点接纳、事务响应和软件可见的时刻。

<span id="和前后章节的关系"></span>第四章讨论选路、仲裁与前进条件；本章解释网络两端及跨接口的契约。多目标通信和具体工作负载见[知识地图](../SUMMARY.md)。流量如何表征和生成 trace 属于[性能评估与架构探索](../SUMMARY.md#07-evaluation-methodology)，可从[流量模式与表征](./traffic-patterns-and-characterization.md)继续阅读。

<span id="建模启示"></span>先按研究问题选定边界，再记录目标映射、注入/接收资源、请求及响应状态、目的端服务和完成事件。需要比较时序时，再加入共享资源、反馈延迟和输入约束。

<span id="一句话理解"></span>一次网络传输是系统事务的一部分；端点和跨接口的契约决定数据能否被正确使用。
