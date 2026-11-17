# OIF 112G XSR+：高速串行信号怎样跨越芯粒？

上级：[02 接口与案例](../SUMMARY.md#interfaces)

封装内不只有多条数据线并行工作的接口，也可以使用每条 lane 速率更高的电接口。本文以 **OIF CEI-112G-XSR+-PAM4** 为例，说明信号怎样经过封装内通道，以及电接口还需要系统提供什么。

OIF 将该接口用于 die-to-die 和 die-to-optical-engine 等场景。本文只讨论**两颗芯粒位于同一封装内**的示意系统；其他应用的封装边界可能不同。[OIF XSR+ 发布说明](https://www.oiforum.com/oif-unveils-cei-112g-xsr-pam4-extended-extra-short-reach-implementation-agreement-paving-the-way-for-advanced-interconnectivity/)

## 一条 lane 经过哪里

假设芯粒 A 向芯粒 B 发送数据。两端和封装通道已经按同一 XSR+ 配置设计，系统也已完成所需准备。一条方向上的简化路径是：

> A 的发送逻辑 → A 的发送器 → 封装通道 → B 的接收器 → B 的接收逻辑

发送器把待发送的比特映射成 PAM4 信号；封装通道将信号送到对端；接收器根据收到的信号恢复数据，再交给后续逻辑。真实系统怎样组织多条 lane、启动链路和处理错误，还取决于它采用的其他规则。

PAM4 使用四种信号状态，每个符号可以表示 2 bit。**符号率**以 Gsym/s 计，**线路比特率**以 Gb/s 计；两者不能混用。[SerDes：NRZ 与 PAM4](../../SERDES/05-signaling-and-metrics/nrz-and-pam4.md)

## 两条 lane 能传多快

OIF 对 XSR+ 指定的符号率范围是 **36–58 Gsym/s**。下面选择其中的 **48 Gsym/s**，只作为教学计算，不是某个器件的实测工作点。

假设 A → B 有两条这样的 lane，均持续发送 PAM4 符号。每符号表示 2 bit，则单方向原始线路速率为：

> **2 条 lane × 48 Gsym/s × 2 bit/符号 = 192 Gb/s = 24 GB/s**

这里的 GB 按十进制计算。两条 lane 能否在同一系统中共同承载数据、怎样分配和重组数据，要由系统另行约定。计算没有扣除编码、纠错、包头或空闲等可能的开销，也不包含反方向，因此不是应用有效吞吐。

## 与宽接口怎样比较

作为另一组**构造条件**，假设 [BoW PHY 2.0](../bow-phy.md) 使用三个同方向的普通 slice。每个 slice 有 16 条数据线，每条线以 BoW-64 模式的 4 Gb/s 工作。三组数据线的原始线路速率也是：

> **3 × 16 条数据线 × 4 Gb/s = 192 Gb/s**

本例只使两种方案在同一方向的**原始线路速率口径**相同。BoW slice 还需要时钟等连接；XSR+ 系统也需要考虑参考时钟、辅助、供电和其他必要连接。不能把两条 lane 与 48 条数据线直接当作完整凸点数量或封装面积的比较。[BoW PHY 2.0，第 5 节](https://www.opencompute.org/documents/bow-specification-v2-0d-final-pdf/)

线路速率相同也不能证明有效吞吐、延迟或能耗相同。两种方案的信号、通道、接口电路和开销不同，必须在共同的系统条件下比较。宽接口的内部也可能使用串并转换；“并行数据线”和“存在串行化”不是互斥条件。[SerDes：增加 lane 还是提高单 lane 速率](../../SERDES/08-system-applications/lane-count-vs-rate.md)

## 封装通道短，为什么还要检查

XSR+ 的通道参数有指定参考面。OIF 描述的插入损耗上限为：在奈奎斯特频率处，**从发送端凸点到接收端凸点最多 13 dB**。上述 48 Gsym/s 教学工作点的奈奎斯特频率是 **24 GHz**。[OIF XSR+ 发布说明](https://www.oiforum.com/oif-unveils-cei-112g-xsr-pam4-extended-extra-short-reach-implementation-agreement-paving-the-way-for-advanced-interconnectivity/)

这不是仅凭长度就能验证的条件。还要按所用规范检查通道、发送器和接收器的其他适用要求，例如损耗随频率的变化、串扰和时序。即使某一项损耗满足限值，也不能单凭它证明整个链路满足要求或已经互通。

**XSR 和 XSR+ 是不同接口条目。** 不能把另一个条目的距离或损耗数字直接作为本文 XSR+ 的要求。[OIF CEI 5.3](https://www.oiforum.com/wp-content/uploads/OIF-CEI-05.3.pdf)

## 电接口还需要什么

XSR+ 规定相关的电接口和通道要求，不单独定义一次读取的地址、响应和完成语义。系统还要确定两端如何组织数据、进行必要的流控和错误处理。是否使用前向纠错、链路重传或其他机制，取决于选用的系统和协议，不能只从 XSR+ 名称推断。

[UCIe 1.1 读取案例](../ucie-pcie-read.md)从 PCIe 请求及返回结果出发；本文只看一种电接口怎样承载线路信号。两个名称的规范范围不同，也不能仅凭它们都用于芯粒就认为可以直接互连。

## 接下来怎么读

- [BoW PHY 2.0](../bow-phy.md)：看并行数据线和随路时钟怎样组成 slice。
- [Stratix 10 TX 产品案例](../04-product-cases/stratix-10-tx.md)：区分产品的封装内接口和对外高速链路。
- [芯粒互操作与启动](../03-system-design/interoperability-and-bring-up.md)：从电气条件继续检查两端和系统配置。
- [跨芯粒读取的有效性能](../03-system-design/effective-bandwidth-and-latency.md)：从线路速率继续分析有效吞吐。
- [SerDes：NRZ 与 PAM4](../../SERDES/05-signaling-and-metrics/nrz-and-pam4.md)：理解符号与比特的关系。
