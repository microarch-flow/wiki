# 封装内芯粒互连：数据怎样跨越 die 边界？

把两颗芯粒放进同一封装，并不意味着它们已经能交换数据。封装需要提供连接通道；两端还需要兼容的物理接口、承载方式和上层协议。

Die-to-die（D2D）描述 die 之间的连接，不指定唯一标准或电路结构。本文关注封装内的 D2D：先区分一次通信所需的几类条件，再用 UCIe 承载 PCIe 读取作为例子。

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

[UCIe 联盟](https://www.uciexpress.org/specifications)将 UCIe 定义为封装级互连规范，覆盖 D2D 物理层、协议和软件等内容。它可以承载 PCIe 和 CXL 等上层协议。联盟说明 UCIe 1.1 向后兼容 1.0，但两颗具体芯粒仍要有可配合的物理接口、协议、格式和配置，才能完成所需通信。

下面是一个**构造案例**。假设芯粒 A 和 B 支持 UCIe 1.1 及兼容的 PCIe 承载模式，链路已就绪，B 的设备地址窗口也已配置：

1. A 发起 PCIe Memory Read；UCIe 接口将请求传到 B。
2. 假设 B 的 PCIe 端点通过桥转换为 AXI 读，再经片上网络访问目标寄存器。网关或网络拥塞时，请求可能等待。
3. 目标返回数据，B 形成带数据的 PCIe Completion。A 匹配返回、检查状态并收齐所需数据后，读取才成功完成。

在此例中，PCIe 定义读取请求和 Completion 的语义，UCIe 提供所选模式下的跨 die 承载。B 内部的 AXI 和 NoC 是案例假设。链路接收到请求，也不代表目标寄存器已经完成读取。

## 不同接口解决不同问题

UCIe 不是唯一的封装内 D2D 选择。例如，[BoW PHY 2.0](./bow-phy.md)描述一种物理接口；OCP 还提供独立的[事务与链路层规范](https://www.opencompute.org/chiplets/25/transaction-and-link-layer-specification-for-bunch-of-wires-bow-interfaces)。比较方案时，应先确认各规范覆盖哪些层，不能只比较名称。

计算 die 访问封装内 HBM 时也要跨越 die 边界，但使用什么接口取决于具体系统；不能仅凭“跨 die”就假设它使用 UCIe。[HBM 的堆叠与封装内互连](../../storage/06-system-integration/packaging/hbm-2.5d-3d-tsv.md)区分了堆栈内部连接与计算侧接口。

## 阅读顺序

1. [UCIe 1.1 读取案例](./ucie-pcie-read.md)：两端怎样准备链路，PCIe 请求怎样跨 die 并返回结果。
2. [BoW PHY 2.0](./bow-phy.md)：数据、时钟和 slice 怎样组成封装内连接。
3. [BoW.Flexi 读取案例](./bow-flexi.md)：AHB 读取怎样封包、跨芯粒并返回。

## 继续阅读

- [NoC：跨 die 网关与排队](../NOC/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：请求怎样进入网关，拥塞怎样影响片上网络。
- [SerDes：封装内接口的物理取舍](../SERDES/08-system-applications/chiplet-and-d2d.md)：宽度、速率、时钟和封装通道。
- [PCIe：事务与 Completion](../PCIE/02-link-transaction-basics/tlp-dllp-completion-basics.md)：读取请求和返回数据的系统语义。
