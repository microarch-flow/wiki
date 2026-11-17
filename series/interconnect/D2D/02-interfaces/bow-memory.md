# BoW 存储接口：计算芯粒怎样连接存储芯粒？

上级：[02 接口与案例](../SUMMARY.md#interfaces)

计算芯粒访问内存时，芯粒间接口对面可以是一个内存控制器芯粒，也可以是存储芯粒。两种划分的请求处理、数据方向和时钟职责不完全相同。

本文以 [BoW Memory Addendum 1.0](https://www.opencompute.org/documents/bow-memory-addendum-final-pdf) 为例，说明 BoW PHY 2.0 怎样用于这些路径。Addendum 描述物理接口及其参考用例；具体上层命令、地址编码和完成语义仍需由所选系统定义。

## 控制器和存储放在哪里

| 用例 | 参考路径 | 要区分的职责 |
| --- | --- | --- |
| 内存控制器芯粒 | ASIC → BoW → 控制器芯粒 → DDR5 内存 | ASIC 与控制器之间是芯粒间接口；控制器还要通过另一段接口访问内存。 |
| 存储芯粒 | ASIC 内的控制器 → BoW memory PHY → 存储芯粒 | 控制器留在 ASIC 侧，通过芯粒间接口向存储侧发送命令、地址或写数据，并接收读数据。 |

第一行的 DDR5 是 Addendum 提供的参考用例，不表示所有控制器芯粒都连接同一种内存。第二行中，存储侧怎样组织存储阵列、具体命令如何编码，要看配套规范和器件。**相同的 BoW 名称不能代替对这两端职责的检查。**[BoW Memory Addendum，第 8.13 节](https://www.opencompute.org/documents/bow-memory-addendum-final-pdf)

## 两个 slice 怎样分配读写

Addendum 的一个存储芯粒参考连接使用两个单向 slice：一个用于从存储芯粒返回读数据，另一个由 ASIC 发向存储侧，在写数据与命令、地址之间复用。不同系统还可以选择其他允许的连接和分配方式。[BoW Memory Addendum，第 8.15 节](https://www.opencompute.org/documents/bow-memory-addendum-final-pdf)

一次构造的读取可以这样经过边界：

1. ASIC 侧控制器形成读取所需的命令和地址，并经发送 slice 送到存储侧。
2. 存储芯粒按双方选定的规则处理访问，准备返回数据。
3. 数据经反方向的 slice 返回 ASIC；控制器按系统规则检查并交付结果。

这只说明职责和方向，不规定特定 DRAM 命令、周期数或事务格式。接收到了线路数据，也不自动证明读取已按上层要求完成。

### 命令和写数据共享什么

假设每个 slice 有 16 条数据线，每线数据率为 **8 Gb/s**，且持续传输时数据线的单方向原始速率为：

> **16 × 8 Gb/s ÷ 8 = 16 GB/s**

再假设在某个观察窗口内，ASIC → 存储的 slice 有一半传输时间用于命令和地址，其余一半用于写数据。按这个**自设分配**，写数据最多占 **8 GB/s** 原始线路容量；反方向读数据 slice 的原始速率仍按各自条件计算。

这不是产品实测，也不是 Addendum 对所有工作负载规定的固定比例。编码、空闲、调度和存储服务能力等还可能降低有效吞吐；不能把两个方向的线路上界当作内存一定能同时达到的读写性能。[BoW PHY 2.0](../bow-phy.md)介绍同样口径的线路速率计算。

## 双向数据线怎样切换

另一个 Addendum 参考用例采用**动态半双工**数据 slice：同一组数据线在一个时刻沿一个方向工作，需要时在发送和接收之间切换。它与上面两个固定方向的 slice 是不同配置，也不表示同一组线可以同时双向传数据。

例如，先将该组数据线用于写入，再切换为读取。切换期间需要留出适当的 turnaround 时间，避免两端同时驱动线路；这段时间不能承载该组线的读写数据。控制器需要在调度中考虑转换。转换时间和读写比例会影响有效吞吐，具体时序以所选接口和实现为准。[BoW Memory Addendum，第 8.17、10.3.13 节](https://www.opencompute.org/documents/bow-memory-addendum-final-pdf)

Addendum 在存储芯粒的参考时钟方案中，把较复杂的时序控制放在 ASIC 一侧；该例与控制器芯粒用例中的对称时钟安排不同。不能仅凭“使用 BoW”就推断所有对端具有相同 PLL、时钟路径或训练步骤。[BoW Memory Addendum，第 10.2 节](https://www.opencompute.org/documents/bow-memory-addendum-final-pdf)

## ECC、备用线与 HBM 的边界

在 Addendum 的一些内存用例中，可选 AUX、FEC 线可以承载由内存控制器生成的 ECC 数据。这与链路层是否实现 FEC 纠错是不同问题。如果这两条线已用于 ECC 而系统还要求线路冗余，Addendum 说明需要额外备用线。[BoW Memory Addendum，第 6.2、13 节](https://www.opencompute.org/documents/bow-memory-addendum-final-pdf)；[BoW PHY 坏线重映射](./bow-phy-redundancy.md)

Addendum 还给出标准封装 HBM（SPHBM）芯粒的参考用例；它不能证明所有 HBM 都使用 BoW。HBM 堆栈内部连接、计算侧接口和该参考用例是不同观察边界。[HBM 的堆叠与封装内互连](../../../storage/06-system-integration/packaging/hbm-2.5d-3d-tsv.md)

[UCIe.mem 存储访问](./ucie-memory.md)说明 UCIe 4.0 中 SoC 与 memory logic die 之间的参考路径。它不是本文的 BoW 参考路径；具体协议和器件组合需要分别核对。[UCIe 4.0 发布说明](https://www.uciexpress.org/_files/ugd/0c1418_970201e6ba294a0fa690ae864082fc46.pdf)

## 接下来怎么读

- [BoW PHY 2.0](../bow-phy.md)：先认识数据线、随路时钟和 slice。
- [BoW PHY 2.0 坏线重映射](./bow-phy-redundancy.md)：看支持冗余时备用线的映射及资源边界。
- [BoW.Flexi 读取案例](../bow-flexi.md)：比较另一套独立规范如何组织一次读取。
- [UCIe.mem 存储访问](./ucie-memory.md)：比较计算侧与内存逻辑 die 之间的另一种职责划分。
- [跨芯粒读取的有效性能](../03-system-design/effective-bandwidth-and-latency.md)：从线路速率继续分析事务窗口和目标服务。
- [HBM：堆叠、宽接口与伪通道](../../../storage/03-dram/protocols/hbm-stacked-wide-io.md)：了解 HBM 的内存组织。
