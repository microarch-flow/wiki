# PCIe 与以太网：共用什么，又在哪里不同？

上级：[系统应用](./README.md)

PCIe 和以太网都可能使用高速串行电链路，但它们解决的系统问题、协议状态和可选介质不同。SerDes 是物理实现的一部分，不能仅凭收发器工作，就推断整套协议已实现。

| 比较项 | PCIe 示例 | 以太网示例 |
| --- | --- | --- |
| 主要用途 | 主机、设备与交换组件之间的互连和事务 | 不同设备之间的网络帧通信；速率与介质有多种组合 |
| 物理路径 | 具体系统可能使用板卡走线、连接器、线缆和 retimer | 可能使用背板、铜缆、双绞线或光模块；依 PHY 类型而异 |
| 建链机制 | 指定版本的 LTSSM、速率与宽度协商 / 恢复 | 依 PHY 与配置使用相应的自动协商、训练和其他机制 |
| 可共用的物理问题 | 时钟恢复、损耗、反射、串扰、均衡和误码测量 | 同样需要关注，但不意味着参数和测试条件相同 |
| 系统观察 | 速率、宽度、状态、事务与错误等 | 指定 PHY 的链路状态、错误 / FEC、帧和吞吐等 |

例如，[TI TLK10031 手册](https://www.ti.com/lit/ds/symlink/tlk10031.pdf)描述了该器件 10GBASE-KR 模式的协商和训练；[PCI-SIG PCIe 5.0 问答](https://pcisig.com/blog/pcie%C2%AE-50-protocol-and-electrical-compliance-testing-deep-dive-webinar-qa)说明了 PCIe 的建链与测试。两份资料分别约束各自的模式，不能把 KR 的系数请求直接当作 PCIe 状态机。

速率相同也不代表两者可以直接相连。双方还要满足同一协议的编码、时序、电气、状态与软件要求；是否支持 FEC、训练和具体通道，必须按协议版本与配置检查。

可继续读现有 [PCIe 分层架构](../../../PCIE/wiki/02-link-transaction-basics/layered-architecture-transaction-data-link-physical.md)，或回看本专题的 [PCIe 链路训练案例](../06-link-operation/pcie-training-case.md)。

## 接下来怎么读

读[增加 lane 还是提高单 lane 速率？](./lane-count-vs-rate.md)，比较两种达到目标线路容量的方法。
