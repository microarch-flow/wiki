# BoW.Flexi：AHB 读取怎样封装成跨芯粒数据包？

上级：[02 接口与案例](./SUMMARY.md#interfaces)

一颗芯粒上的 AHB 发起方要读取另一颗芯粒上的寄存器，跨芯粒接口怎样传递地址，又怎样把读数据交回来？本文使用 [OCP BoW.Flexi 1.0.0 规范](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)中的 AHB 桥作为参考，构造一次读取。

BoW.Flexi 定义了事务层、链路层和物理层。本文关注一次事务怎样封包与返回；[BoW PHY 2.0 文章](./bow-phy.md)则关注另一种接口的数据线、时钟和 slice。两者不能只凭名称假定可以直接互通。

## 先约定接口和读取

这是**构造案例**，不是产品实测。假设芯粒 A 的 AHB 发起方要读取芯粒 B 上一个 4 字节对齐的 32 位寄存器。目标地址为 **0x8000_1000**；假设目标成功返回 **0x1234_5678**。

两端都有适合本例的 AHB 桥和 BoW.Flexi 接口。A 的桥在本地 AHB 总线上接收请求；B 的桥在远端 AHB 总线上发起访问。两端已经配置好相容的地址映射、包格式和物理接口。

BoW.Flexi 接口由两条相反方向的单向链路组成。每个方向各有数据线、随路时钟和 Frame 信号。两方向的数据线数可以不同；本例假设双方已将每个方向配置为 **8 条数据线**，PHY 与链路层之间的并行数据通路也为 8 bit。[BoW.Flexi 1.0.0，第 4、7.1 节](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

接口从 x1 数据模式开始；本例的 x8 是配置完成后的状态，并以两端具有所需的物理连接为前提。1.0.0 没有定义 PHY training，但仍有复位和配置机制。实际系统还要确认时钟、电气条件及双方配置能够配合。[BoW.Flexi 1.0.0，第 5.1.5、7.6、7.8 节](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

## 一次读取经过哪些层

| 层 | 本例的职责 |
| --- | --- |
| 系统层 | A 的 AHB 桥接收读取；B 的桥访问远端 AHB 总线。桥还负责本地总线握手和响应。 |
| 事务层 | 将读取和响应组织成带命令的数据包，并把收到的包交给对应接口。 |
| 链路层 | 按配置加入可选 ECC，并补齐数据包；接收时执行相应处理。 |
| 物理层（PHY） | 使用数据线、Frame 和随路时钟跨芯粒发送或接收包。 |

不同层解决的问题不同。例如，PHY 已经接收到线路上的数据，并不表示 B 的寄存器已经完成读取。[BoW.Flexi 1.0.0，第 4.1 节](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

这里的事务层和链路层由 BoW.Flexi 规范定义，不能直接等同于为 BoW PHY 定义的独立 TLL 1.0。OCP 工作组也在推进通用 TLL 到多种 PHY 的映射；具体组合需要核对规范版本和双方配置。[OCP Link Layer 工作组](https://www.opencompute.org/projects/server/open-chiplet-economy/link-layer/)

## 请求和响应怎样封包

本例采用 32 bit 地址，不启用 ECC 和可选字段。以下是协议字段的作用，不是线路电平图：

| 方向 | 数据包 | 本例的内容 |
| --- | --- | --- |
| A → B | 读取请求 | 3 bit 命令、3 bit 大小、32 bit 地址。 |
| B → A | 读取响应 | 3 bit 命令、32 bit 读数据。 |

读取请求的命令为二进制 **001**，大小字段 **010** 表示 4 字节。读取响应的命令为二进制 **010**。本例的响应不重复发送地址或大小；A 的系统层需要保存待完成请求的状态，才能把返回数据交给正确的访问。[BoW.Flexi 1.0.0，第 5.1.3、5.1.7、11.4–11.5 节](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

在正常发包时，Frame 为高表示包正在传输，接收端按随路时钟采样数据；Frame 拉低标记包结束。接口使用单数据率（SDR）：发送端在时钟上升沿发送数据，接收端在随后下降沿采样。复位和唤醒还会以其他方式使用这些信号，不能把普通发包时的含义套用到所有状态。[BoW.Flexi 1.0.0，第 7.4–7.8 节](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

8 条数据线在每个链路时钟周期并行传送 8 bit。链路层在包末尾补零，使本例的包长度对齐到 8 bit：

| 数据包 | 补齐和线路占用 |
| --- | --- |
| 读取请求 | 3 + 3 + 32 = 38 bit；补 2 bit 得到 40 bit，占用 5 个链路时钟周期。 |
| 读取响应 | 3 + 32 = 35 bit；补 5 bit 得到 40 bit，占用 5 个链路时钟周期。 |

这是基于上述配置的**教学计算**，与规范附录 A 的 x8 示例一致。请求和响应分别经过两个方向的链路。两个 5 周期只表示各包占用线路的时间，不包含桥、目标访问、排队或时钟域转换，也不是端到端读取延迟。启用 ECC、可选字段或使用其他宽度时，包长和周期数都需要重新计算。[BoW.Flexi 1.0.0，第 6.2 节、附录 A.6.4–A.6.5](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

## 读取何时完成

1. **A 发起读取。** A 的 AHB 桥接收地址和访问大小，并将读取请求交给 BoW.Flexi 接口。A 的桥在等待期间使本地 AHB 的 HREADY 保持低电平，访问尚未完成。
2. **B 访问目标。** B 收到并解析请求。B 的 AHB 桥向本地总线发起读取，等待目标返回。
3. **B 返回结果。** 假设目标成功返回 0x1234_5678，B 将数据放入读取响应，从反方向发给 A。
4. **A 交付结果。** A 的桥将响应与待完成的请求对应起来，按 AHB 握手交付读数据和成功状态。若远端报告错误，桥应按该示例的错误处理路径返回错误，而不是交付成功数据。

在这个普通系统接口案例中，同一方向一次只允许一笔在途系统事务。可选的 Advanced System Interface 可以采用自己的流控和多在途策略；配置、错误和虚拟线等命令也有各自的规则。不能把本例的等待方式推广为整条链路同一时刻只能传一个事务。[BoW.Flexi 1.0.0，第 4.1、5.1.8 节及附录 A](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

## 写入响应和可选 ECC

读取需要等待读数据。写入也需要区分响应的含义：规范中的 **Non-Posted Write** 使用响应确认写入完成；**Posted Write** 的响应可以只表示接收端已经接纳写入、可以接收下一笔 posted write，并不要求目标写入已经完成。因此，收到 posted write 响应后，不能仅凭该响应断定远端目标已经完成写入。[BoW.Flexi 1.0.0，第 5.1.7 节](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

ECC 是可选项。启用时，链路层为数据包加入纠错信息；规范描述的码字可纠正单比特错误并检测双比特错误。这不表示任意多比特错误都能纠正，也不表示接口一定自动重传。双方需要采用相容的 ECC 配置，并按系统的错误处理机制处理不可纠正错误。[BoW.Flexi 1.0.0，第 4.3、6.1 节](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)

## 接下来怎么读

- [BoW PHY 2.0](./bow-phy.md)：看另一种 BoW 物理接口怎样组织数据线和随路时钟。
- [跨芯粒寄存器读](./ucie-pcie-read.md)。沿同一条路径看物理通道，再看 PCIe 的请求与 Completion 如何由 UCIe 1.1 承载。
- [NoC：跨 die 网关与排队](../NOC/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：继续分析请求进入网关后的缓冲和回压。

本文的 AHB 桥和包长计算参考规范附录 A。1.0.0 文本的第 1 章称附录仅供参考、属于非规范性内容；附录 D 的表 D.2 又将附录 A 列为规范性定义。因此，本文将 AHB 桥作为参考示例，附录的规范地位仍需向 OCP 核实。该版本第 8 章也说明完整的一致性定义留待后续修订；实际互通仍需核对采用的规范版本、配置和器件资料。[BoW.Flexi 1.0.0，第 1、8 章及附录 D](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf)
