# AIB 2.0：数据怎样通过芯粒间的物理接口？

上级：[02 接口与案例](../SUMMARY.md#interfaces)

两颗芯粒要通过封装交换数据，需要约定数据线、时钟和控制信号怎样配合。Advanced Interface Bus（AIB）提供一种并行的 die-to-die 接口。本文以 AIB 2.0 的一个具体实现为例，说明一组信号怎样传输数据，以及物理接口还需要上层提供什么。

[CHIPS Alliance 的 AIB 规范仓库](https://github.com/chipsalliance/AIB-specification)提供 AIB 2.0 规范；[AIB PHY 开源仓库](https://github.com/chipsalliance/aib-phy-hardware)提供对应的模型和 RTL。下面的线数、频率和电路细节采用研究者公开的 [Arvon 芯粒系统实现](https://web.eecs.umich.edu/~zhengya/papers/tang_jssc24.pdf)，不代表所有 AIB 实现都具有相同参数。

## 一个通道传送什么

Arvon 将 FPGA 芯粒和 DSP 芯粒放在同一封装中。其 DSP 芯粒的一侧使用 AIB 2.0，另一侧使用 AIB 1.0。本文只看其中一个 AIB 2.0 通道，并假设从芯粒 A 向芯粒 B 发送数据。

| 部分 | 本例中的职责 |
| --- | --- |
| A 的适配逻辑 | 从本地逻辑接收并行数据，按发送接口的节拍组织数据。 |
| A → B 的数据与时钟 | 40 条发送数据线并行传输；发送端同时送出差分时钟，供 B 确定采样时刻。 |
| B 的接收逻辑 | 使用收到的时钟采样数据，恢复并行数据并交给 B 的本地逻辑。 |
| B → A 的数据与时钟 | 另有 40 条反方向数据线及对应时钟，可以传送反方向数据。 |
| 控制及冗余连接 | 用于该实现的初始化、控制和冗余等功能，不计入上面的数据线数。 |

时钟由发送端随数据一起送出，称为**源同步**。收到时钟并不保证采样点已经合适：时钟和数据经过封装时可能产生不同延迟。Arvon 使用测试序列和接收时钟相位调整来寻找采样点；这说明一种实现方法，不表示所有 AIB 2.0 系统都采用相同训练电路。[Arvon 论文，第 III 节](https://web.eecs.umich.edu/~zhengya/papers/tang_jssc24.pdf)

## 40 条数据线能传多快

沿用 Arvon 中的一个工作条件：40 条发送数据线各以 **4 Gb/s** 工作，随路时钟为 **2 GHz**。数据在时钟的两个边沿传输，因此每条线在一个时钟周期传送 2 bit。

- 一个周期为 **0.5 ns**，40 条数据线共传送 **80 个线路 bit**。
- 单方向原始线路速率为 **40 × 4 Gb/s = 160 Gb/s = 20 GB/s**。

这里的 GB 按十进制计算。4 Gb/s 已经是每线数据率，计算时不再乘一次双沿系数。20 GB/s 只统计这个方向的数据线；它不包含反方向，也不是应用吞吐或一次访问的延迟。

论文还描述了可选的**数据总线反转**（DBI）：该实现把每 19 bit 数据与 1 bit 反转指示组合，再送上 20 个数据位置。启用这种编码时，部分线路 bit 用来表示反转状态，不能全部算作上层数据。包头、空闲、流控等其他开销还要按实际使用的上层机制计算。[Arvon 论文，第 III-A 节](https://web.eecs.umich.edu/~zhengya/papers/tang_jssc24.pdf)

## AIB 和封装、上层协议怎样配合

AIB 接口在两端产生和接收信号；封装提供这两端之间的连接。Arvon 使用 EMIB 硅桥连接芯粒。Intel 的 AIB 资料也展示了通过中介层布线或硅桥连接的方式。因此，**AIB 是接口，EMIB 是一种封装连接结构**。[Intel AIB 白皮书](https://www.intel.com/content/dam/www/public/us/en/documents/white-papers/accelerating-innovation-through-aib-whitepaper.pdf)

物理接口能够交付比特，不代表对端已经理解一次读取或写入。两端还需要相容的上层数据格式、事务规则和必要的流控。例如，两端各有 AIB 接口，仍要检查对数据的组织方式是否一致，才能将发送的数据交给正确的目标。

[UCIe 1.1 读取案例](../ucie-pcie-read.md)则同时涉及 UCIe 的跨芯粒承载和 PCIe 的事务语义。比较时，应先明确每个规范和实现覆盖的职责，不能把 AIB 的物理接口与整条 PCIe 读取路径当作同一层的方案。

[BoW PHY 2.0](../bow-phy.md)也使用并行数据和随路时钟，但它的普通单向 slice、信号组织和配置规则由自己的规范定义。不能只因为两者都是源同步接口，就把 AIB 通道和 BoW slice 直接相连。完整的互通判断还需要检查封装、电气、配置和上层协议。

## 接下来怎么读

- [芯粒互操作与启动](../03-system-design/interoperability-and-bring-up.md)：检查两端怎样从设计匹配走到系统可用。
- [BoW PHY 2.0](../bow-phy.md)：比较另一种并行物理接口的数据线和时钟。
- [AMBA CHI C2C](./chi-c2c.md)：看一致性消息如何组织后交给跨芯粒承载层。
- [Stratix 10 TX 产品案例](../04-product-cases/stratix-10-tx.md)：看 FPGA 与收发器 tile 的封装内连接及对外链路。
- [芯粒怎样在封装内连接](../01-foundations/in-package-connections.md)：回看 PHY 与硅桥、中介层的边界。
