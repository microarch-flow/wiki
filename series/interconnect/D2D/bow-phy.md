# BoW PHY 2.0：数据怎样通过并行线路跨越芯粒？

上级：[02 接口与案例](./SUMMARY.md#interfaces)

OCP 的 Bunch of Wires（BoW）芯粒互连规范包含不同文档。本文聚焦 [BoW PHY 2.0](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/) 的主带物理层（PHY）接口：发送端怎样把数据与时钟送过封装，接收端怎样还原数据。上层交换的是读取、写入还是其他消息，需要由所选协议另行定义。

## 一个 slice 有哪些信号

先看一个普通宽度的 **单向 slice**。假设芯粒 A 发送，芯粒 B 接收；数据和时钟经封装内的连接从 A 到 B。

| 信号 | 作用 |
| --- | --- |
| 16 条单端数据线 D0–D15 | 并行传送数据；每条线传输对应的数据位。 |
| 一对差分时钟线 CLK+、CLK− | 由发送端随数据送出，供接收端确定采样时刻。 |
| FEC、AUX 信号线 | 可选信号；是否提供以及具体用途需要两端配合。 |

这里统计的是信号线，不包含供电、接地和其他系统连接。FEC 是前向纠错（Forward Error Correction）相关信号，AUX 可用于辅助功能；这些名字本身不保证系统已具备某一种纠错或流控机制。

时钟由发送端随数据发送，称为**源同步（source-synchronous）**。它为接收端提供与数据相关的时间参考，但时钟和数据经过的通道仍可能有不同延迟。接收端还要满足电压和时序要求，才能正确采样。[BoW PHY 2.0，第 6、10、12 节](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)

## 怎样同时向两个方向传输

普通 slice 在工作时沿一个方向传输。下面的构造使用两组独立的单向 slice，因而可以同时交换两个方向的数据：

| 方向 | 本例的路径 |
| --- | --- |
| A → B | A 的发送 slice → 封装通道 → B 的接收 slice |
| B → A | B 的发送 slice → 封装通道 → A 的接收 slice |

在这个例子中，两方向共有 32 条数据线和 4 条时钟线；可选信号及供电、接地不计入。两方向不必具有相同数量的 slice。

BoW PHY 2.0 也定义了 8 条数据线的半宽 slice，以及可配置为发送或接收的 slice。**可配置方向**表示运行时选择一个方向，不表示同一组线可以同时收发。[BoW PHY 2.0，第 6.1、8.4 节](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)

## 一个数据字要占用多久

下面是**教学计算**，不是器件实测。假设 A → B 使用一个普通宽度 slice，接口已就绪并完成必要的对齐；16 条数据线都持续以 **8 Gb/s** 工作。随路时钟为 **4 GHz**，数据在每个时钟周期的两个边沿传输，因此每线数据率为 8 Gb/s。

假设发送侧将一个 128 bit 的并行数据字分成 8 组，每组 16 bit：

1. 第一个传输时隙，16 条数据线各发送第 1 组中的一位。
2. 下一个时隙，数据线发送第 2 组；后续时隙依次发送其余各组。
3. 接收侧按时钟采样并恢复这些数据，再交给上层处理。

8 个传输时隙占 4 个时钟周期。4 GHz 的周期为 0.25 ns，因此这个数据字占用 **1 ns 的线路传输时间**。如果假定发送侧使用 8∶1 串行化，128 bit 并行接口的对应数据节拍为 1 GHz。[BoW PHY 2.0，第 5.4、10 节](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)；[OCP 事务与链路层规范，速率示例](https://www.opencompute.org/documents/transaction-and-link-layer-specification-for-bunch-of-wires-bow-interfaces-pdf-pdf/)

同一条件下，单方向数据线的理论原始速率为 **16 × 8 Gb/s ÷ 8 = 16 GB/s**。这里的 GB 按十进制计算。8 Gb/s 已经是每线数据率，不能再额外乘以 DDR 的系数。

这个结果不包含空闲、上层包头、对齐或其他开销，也不是应用有效吞吐。1 ns 是本例数据字占用线路的时间，不包含发送、封装传播、接收和上层处理所需的完整端到端延迟。

## 采样之后还需要什么

源同步不意味着各数据线和时钟线到达得完全一致。通道偏斜、串扰和接收端采样窗口都会影响结果。复位、配置和必要的初始化完成后，仍应按所选实现检查时序与信号质量。

接收端还要按约定还原数据次序。多个 slice 一起使用时，跨 slice 的数据对齐也要有明确的实现责任。PHY 2.0 说明，某些字边界对齐可以由 PHY 提供，也可以交给链路层处理；不能因为线路上收到了比特，就假设上层已经取得正确的数据字。[BoW PHY 2.0，第 10.1–10.2 节](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)

当可选 FEC 信号线用于纠错时，PHY 只负责承载相应比特；纠错逻辑由链路层实现。是否使用纠错、如何报告不可纠正错误，以及是否重传，都要看双方选定的上层机制。

## PHY 怎样接入上层协议

BoW PHY 2.0 不规定一次 AXI 或 PCIe 读取何时完成。OCP 另有[事务与链路层规范 Rev A、1.0](https://www.opencompute.org/documents/transaction-and-link-layer-specification-for-bunch-of-wires-bow-interfaces-pdf-pdf/)，用于组织事务流与链路传输；具体总线协议映射还需要相应的协议变体和接口配置。

例如，两颗芯粒都提供 BoW PHY，也都在片内使用 AXI，仍需确认两端采用相容的上层映射、数据格式和流控。只有这些条件配合，才能讨论 AXI 请求和响应怎样跨越连接。

[UCIe 1.1 读取案例](./ucie-pcie-read.md)从 PCIe 事务出发，解释请求和 Completion；本文聚焦 BoW PHY 怎样传输数据。两者的观察层次不同，不能仅凭文章中的例子比较完整系统的性能。OCP 的 [Universal D2D 事务与链路层资料](https://www.opencompute.org/documents/spec-universal-d2d-transaction-link-layer-ventana-docx-pdf)还描述了向 UCIe 接口扩展的方案；具体组合仍需检查规范版本和双方实现。

## BoW.Flexi 的边界

[BoW.Flexi 1.0.0](https://www.opencompute.org/wp-content/uploads/2026/10/bow-flexi_1p0_final.pdf) 是另一套有独立范围的规范，包含事务、链路和物理层。它的物理接口采用单数据率（SDR），使用时钟、Frame 和可配置数据线；该版本没有定义 PHY training，但仍有复位和配置要求。

因此，本文对 BoW PHY 2.0 普通主带 slice 的 16 条数据线和 DDR 示例，不能直接套用到 BoW.Flexi。[BoW.Flexi 读取案例](./bow-flexi.md)使用 AHB 桥示例，解释请求怎样封包并返回。

## 接下来怎么读

- [芯粒怎样在封装内连接](./01-foundations/in-package-connections.md)：先区分两端 PHY 和封装布线路径。
- [UCIe 1.1 读取案例](./ucie-pcie-read.md)：从一次 PCIe 读取理解事务与跨 die 承载。
- [AIB 2.0](./02-interfaces/aib-2.md)：比较另一种并行接口的数据线、时钟和封装连接。
- [跨芯粒读取的有效性能](./03-system-design/effective-bandwidth-and-latency.md)：从原始线路速率继续分析有效吞吐上界。
- [SerDes：封装内接口的物理取舍](../SERDES/08-system-applications/chiplet-and-d2d.md)：比较接口宽度、每线速率和封装通道。
- [NoC：跨 die 网关与排队](../NOC/06-ai-noc-specifics/chiplet-and-die-to-die-interconnect.md)：分析片上网络与跨 die 接口之间的队列和回压。

本文使用 OCP 收录的 BoW PHY 2.0 公开文本；其修订表仍保留了 Draft 2.0 字样。实际设计和互通验证应核对项目采用的规范修订版、接口配置和器件资料。
