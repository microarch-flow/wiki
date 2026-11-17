# 封装内芯粒互连：数据怎样跨越 die 边界？

芯粒是为与其他裸片共同组成系统而设计的功能裸片。例如，一个封装中可以有计算芯粒和 I/O 芯粒。封装为裸片提供支撑、连接和保护等功能。

把两颗芯粒放进同一封装，并不意味着它们已经能交换数据。封装需要提供连接通道；两端还需要兼容的物理接口、承载方式和上层协议。Die-to-die（D2D）描述裸片之间的连接，不指定唯一标准或电路结构。本文关注封装内的 D2D。

## 芯粒怎样在封装内连接

以电互连为例，发送端的物理接口（PHY）产生信号；信号经过焊盘、凸点和封装内布线等结构，到达另一颗芯粒的接收端 PHY。布线可以经过封装基板、中介层或局部硅桥；上下堆叠的裸片也可以经过连接界面通信。具体路径取决于封装结构。

封装通道负责连接，不会自动定义消息的含义。两端还要按共同支持的规则组织和接收数据，系统才能完成所需的读取、写入或其他操作。

如果刚接触这些概念，可从[芯粒是什么](./01-foundations/what-is-a-chiplet.md)开始，再看[封装内连接](./01-foundations/in-package-connections.md)和[一次跨芯粒通信](./01-foundations/cross-die-communication.md)。

## 先区分四个问题

| 问题 | 需要确定的内容 |
| --- | --- |
| 交换什么 | 是流数据、寄存器访问还是内存事务？谁发起，什么事件表示完成？ |
| 怎样承载 | 两端使用什么协议和数据格式？怎样流控、检测和处理错误？ |
| 怎样传信号 | 数据线数、每线速率、时钟、电气条件与训练要求是什么？ |
| 经过什么通道 | 信号经过哪些凸点、重布线层、中介层或其他封装连接？ |

四个问题需要配合。例如，两颗 die 的连接线已经接通，仍可能因为上层协议或数据格式不兼容而无法交换预期事务。反过来，两端都支持相同的事务协议，也不代表它们的物理接口和封装连接可以直接配合。

在给定的数据率目标下，较宽的数据接口可能降低每线所需速率，但也需要更多连接和布线资源。比较时还要区分线路速率与有效载荷速率；详见 [SerDes：封装内接口的物理取舍](../SERDES/08-system-applications/chiplet-and-d2d.md)和[怎样计算带宽和每比特能耗？](../SERDES/05-signaling-and-metrics/bandwidth-power-efficiency.md)。

## 以 UCIe 为例

[UCIe 联盟](https://www.uciexpress.org/specifications)将 UCIe 定义为封装级互连规范，覆盖 D2D 物理层、协议和软件等内容。假设两颗芯粒支持相容的 UCIe 1.1 和 PCIe 承载配置，一次 PCIe 读取可以经 UCIe 到达对端，再由对端返回 Completion。链路收到请求不代表读取已经成功；完整过程见 [UCIe 1.1 读取案例](./ucie-pcie-read.md)。

UCIe 继续演进。[UCIe.mem 存储访问](./02-interfaces/ucie-memory.md)说明 4.0 介绍的计算芯粒与内存逻辑 die 连接；[UCIe 2.0 测试访问与管理](./03-system-design/ucie-dfx-test-access.md)说明可选管理架构中的测试入口。现有读取文章仍以 1.1 为例，不能把新版本的功能直接套入该案例。

## 不同接口解决不同问题

下面的入口覆盖不同层次，不能仅凭名称判断它们是否可以替换或配合。具体组合还要核对两端实现、接口配置和封装条件。

| 入口 | 本专题关注的职责 |
| --- | --- |
| [UCIe 1.1 读取案例](./ucie-pcie-read.md) | 在选定配置下，用 UCIe 承载 PCIe 请求和 Completion。 |
| [UCIe-3D 垂直连接](./02-interfaces/ucie-3d.md) | 通过堆叠界面的物理接口传递数据；上层仍需配合。 |
| [UCIe.mem 存储访问](./02-interfaces/ucie-memory.md) | 在 UCIe 4.0 中组织计算芯粒与内存逻辑 die 之间的内存请求和响应。 |
| [BoW PHY 2.0](./bow-phy.md) | 定义数据线、随路时钟等物理接口；上层事务规则需要另行确定。 |
| [BoW.Flexi 读取案例](./bow-flexi.md) | 使用 BoW.Flexi 自身的事务层、链路层和物理层，展示一次 AHB 读取。 |
| [AIB 2.0](./02-interfaces/aib-2.md) | 提供并行物理接口；上层协议和封装连接仍需配合。 |
| [OIF 112G XSR+](./02-interfaces/oif-cei-112g-xsr-plus.md) | 定义高速串行电接口；事务语义和其他上层职责需要另行确定。 |
| [AMBA CHI C2C](./02-interfaces/chi-c2c.md) | 组织跨芯片的 CHI 消息，与相容的承载接口配合。 |

例如，OCP 还提供独立的[事务与链路层规范](https://www.opencompute.org/chiplets/25/transaction-and-link-layer-specification-for-bunch-of-wires-bow-interfaces)。BoW.Flexi 有自己的分层定义，不能仅凭名称假定它与 BoW PHY 2.0 直接互通。配合前还应检查[芯粒互操作与启动](./03-system-design/interoperability-and-bring-up.md)涉及的条件。

计算 die 访问封装内 HBM 时也要跨越 die 边界，但使用什么接口取决于具体系统；不能仅凭“跨 die”就假设它使用 UCIe。[HBM 的堆叠与封装内互连](../../storage/06-system-integration/packaging/hbm-2.5d-3d-tsv.md)区分了堆栈内部连接与计算侧接口。

## 按问题选读

- **初识芯粒互连**：从[芯粒是什么](./01-foundations/what-is-a-chiplet.md)开始，依次看[芯粒怎样在封装内连接](./01-foundations/in-package-connections.md)和[一次跨芯粒通信](./01-foundations/cross-die-communication.md)，再选择 [UCIe 1.1 读取案例](./ucie-pcie-read.md)或 [BoW.Flexi 读取案例](./bow-flexi.md)。
- **启动和故障定位**：先看[芯粒互操作与启动](./03-system-design/interoperability-and-bring-up.md)，再用 [UCIe 1.1 链路启动与训练](./02-interfaces/ucie-1-1-link-bring-up.md)了解具体流程。需要排查时，继续阅读[链路测试与故障定位](./03-system-design/link-testing-and-diagnosis.md)；如需了解管理测试入口，可选读 [UCIe 2.0 测试访问与管理](./03-system-design/ucie-dfx-test-access.md)。
- **性能和系统设计**：依次阅读[跨芯粒流控与前进条件](./03-system-design/flow-control-and-forward-progress.md)、[跨芯粒读取的有效性能](./03-system-design/effective-bandwidth-and-latency.md)和[多芯粒拓扑与数据放置](./03-system-design/multi-chiplet-topology.md)，再用 [AMD MI300A 产品案例](./04-product-cases/amd-mi300a.md)了解一个公开的系统实例。

## 阅读顺序

1. [芯粒是什么](./01-foundations/what-is-a-chiplet.md)：区分裸片、芯粒和封装。
2. [芯粒怎样在封装内连接](./01-foundations/in-package-connections.md)：认识中介层、硅桥和堆叠连接。
3. [一次跨芯粒通信](./01-foundations/cross-die-communication.md)：沿请求和返回路径区分接口与通道。
4. [UCIe 1.1 读取案例](./ucie-pcie-read.md)：PCIe 请求怎样跨 die 并返回结果。
5. [UCIe 1.1 链路启动与训练](./02-interfaces/ucie-1-1-link-bring-up.md)：边带、主带和 Adapter 怎样逐步就绪。
6. [UCIe-3D 垂直连接](./02-interfaces/ucie-3d.md)：堆叠芯粒怎样通过垂直接口交换数据。
7. [UCIe.mem 存储访问](./02-interfaces/ucie-memory.md)：计算芯粒怎样经内存逻辑 die 访问内存。
8. [BoW PHY 2.0](./bow-phy.md)：数据、时钟和 slice 怎样组成封装内连接。
9. [BoW PHY 2.0 坏线重映射](./02-interfaces/bow-phy-redundancy.md)：支持冗余的 slice 怎样用备用线绕过缺陷。
10. [BoW 存储接口](./02-interfaces/bow-memory.md)：控制器芯粒和存储芯粒怎样使用 BoW 连接。
11. [BoW.Flexi 读取案例](./bow-flexi.md)：AHB 读取怎样封包、跨芯粒并返回。
12. [AIB 2.0](./02-interfaces/aib-2.md)：另一种并行物理接口怎样传递数据。
13. [OIF 112G XSR+](./02-interfaces/oif-cei-112g-xsr-plus.md)：高速串行电接口怎样经过封装内通道。
14. [AMBA CHI C2C](./02-interfaces/chi-c2c.md)：一致性消息怎样组织并跨芯粒传输。
15. [芯粒互操作与启动](./03-system-design/interoperability-and-bring-up.md)：从设计匹配到链路和系统就绪。
16. [跨芯粒流控与前进条件](./03-system-design/flow-control-and-forward-progress.md)：请求、snoop 和数据怎样取得发送授权。
17. [跨芯粒链路错误检测与重放](./03-system-design/link-reliability.md)：数据传输出错后怎样检测和尝试恢复。
18. [跨芯粒读取的有效性能](./03-system-design/effective-bandwidth-and-latency.md)：线路速率、在途窗口和目标服务怎样限制吞吐。
19. [多芯粒拓扑与数据放置](./03-system-design/multi-chiplet-topology.md)：多个芯粒之间的连接与数据位置怎样改变链路流量。
20. [链路测试与故障定位](./03-system-design/link-testing-and-diagnosis.md)：按测试路径判断覆盖范围和故障线索。
21. [UCIe 2.0 测试访问与管理](./03-system-design/ucie-dfx-test-access.md)：管理端怎样访问封装内芯粒的测试逻辑。
22. [Stratix 10 TX 产品案例](./04-product-cases/stratix-10-tx.md)：FPGA 核心怎样与收发器 tile 配合。
23. [AMD EPYC 9004 产品案例](./04-product-cases/amd-epyc-9004-gmi.md)：计算芯粒怎样经 I/O die 访问系统。
24. [AMD MI300A 产品案例](./04-product-cases/amd-mi300a.md)：CPU、GPU 和 HBM 怎样在同一封装协作。

也可以按问题查看[知识地图](./SUMMARY.md)。

## 继续阅读

- [NoC：跨 die 网关与排队](../NOC/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：请求怎样进入网关，拥塞怎样影响片上网络。
- [SerDes：封装内接口的物理取舍](../SERDES/08-system-applications/chiplet-and-d2d.md)：宽度、速率、时钟和封装通道。
- [PCIe：事务与 Completion](../PCIE/02-link-transaction-basics/tlp-dllp-completion-basics.md)：读取请求和返回数据的系统语义。
