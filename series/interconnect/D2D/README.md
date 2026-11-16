# 封装内芯粒互连：数据怎样跨越 die 边界？

两颗芯粒组合成一个封装后，仍需约定如何交换请求和数据。封装提供物理连接条件；两端还要具有兼容的接口、协议和工作配置。Die-to-die（D2D）描述 die 之间的连接，并不指定唯一标准或电路结构。

## 先区分四个问题

| 问题 | 需要确定的内容 |
| --- | --- |
| 交换什么 | 流数据、寄存器访问或内存事务；谁发起，何时完成。 |
| 怎样承载 | 两端采用的协议、数据格式、流控与错误处理。 |
| 怎样传信号 | 接口宽度、每线速率、时钟、训练和电气条件。 |
| 经过什么通道 | 凸点、重布线层、中介层或其他封装连接及其约束。 |

这些选择需要配合。例如，连接线足够多不代表两端的事务协议兼容。宽接口可能降低单线速率，但也会增加连接和布线资源；实际取舍要在相同带宽目标与封装条件下比较。

## 以 UCIe 为例

[UCIe 联盟](https://www.uciexpress.org/specifications)将 UCIe 定义为封装级互连规范，涉及 D2D 物理层、协议和软件等内容。UCIe 可以承载 PCIe 和 CXL 等上层协议；两端支持的协议、格式和特性仍需匹配。不同版本的能力不能直接混用。

下面是一个**构造案例**。假设两颗芯粒支持 UCIe 1.1 和兼容的 PCIe 承载模式，链路已就绪，设备地址窗口也已配置：

1. 芯粒 A 发起一次 PCIe Memory Read，UCIe 接口将请求传到芯粒 B。
2. 假设 B 的 PCIe 端点通过桥接到 AXI，片上网络再将请求送到目标寄存器。网关或网络拥塞时，请求可能等待。
3. 目标返回数据，B 形成带数据的 PCIe Completion；A 收齐所需数据并确认状态后，这次读取才成功完成。

UCIe 负责所选模式下的跨 die 承载，PCIe 定义此例的请求和完成语义。B 内部使用 AXI 和 NoC 是案例假设，不是 UCIe 的必选结构。UCIe 1.1 对 streaming 协议的承载和可靠性能力见[联盟说明](https://www.uciexpress.org/post/ucie-1-1-provides-streaming-protocol-solution-for-error-detection-and-replay)。

## 继续阅读

- [NoC：跨 die 网关与排队](../NOC/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：请求怎样进入网关，拥塞怎样影响片上网络。
- [SerDes：封装内接口的物理取舍](../SERDES/08-system-applications/chiplet-and-d2d.md)：宽度、速率、时钟和封装通道。
- [PCIe：事务与 Completion](../PCIE/02-link-transaction-basics/tlp-dllp-completion-basics.md)：读取请求和返回数据的系统语义。
