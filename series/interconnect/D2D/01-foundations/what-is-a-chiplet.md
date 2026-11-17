# 芯粒是什么，为什么要把系统拆开？

上级：[01 芯粒与连接基础](../SUMMARY.md#foundations)

一颗处理器可以由一块裸片完成，也可以把计算、I/O 等功能分到多块裸片，再把它们装进同一个封装。**芯粒（chiplet）**通常指为与其他裸片共同组成系统而设计的功能裸片。它的关键是参与系统集成的方式，而不是尺寸小到某个固定值。[OCP 对芯粒的定义](https://www.opencompute.org/documents/ocp-odsa-cdx-proposed-standardization-of-chiplet-models-for-heterogeneous-integration-2-pdf)

## 先分清裸片、芯粒和封装

| 名称 | 在说什么 |
| --- | --- |
| 晶圆 | 制造集成电路时使用的圆形半导体片；上面通常形成许多相同的电路单元。 |
| 裸片（die） | 从晶圆上分割出的单块半导体器件。裸片可以承担完整系统，也可以只承担系统的一部分。 |
| 芯粒 | 为与其他裸片协同工作而设计的功能裸片，例如计算芯粒或 I/O 芯粒。 |
| 封装（package） | 为一个或多个裸片提供支撑、连接和保护等功能的组件，并提供与外部系统连接的接口。 |

封装不是芯粒本身。两颗芯粒在同一封装中，也不意味着已经能通信：设计还需要为它们提供物理连接和兼容的接口。

## 从一个拆分示例出发

假设一个处理器需要计算核心、内存控制器和外部 I/O。单裸片方案可以把这些功能做在一块 die 上。另一种方案把计算核心放在计算芯粒，把内存与 I/O 接口放在 I/O 芯粒，再通过封装内连接交换请求和数据。

这只是划分示例。实际产品可以包含多颗计算芯粒，也可以采用不同的功能边界。例如，[AMD EPYC 9005 架构资料](https://www.amd.com/content/dam/amd/en/documents/epyc-technical-docs/user-guides/58462_amd-epyc-9005-tg-architecture-overview.pdf)描述了计算核心 die 通过 I/O die 访问内存、I/O 和其他计算资源的组织。这个产品实例不代表所有芯粒系统都采用相同拓扑或接口。

## 为什么拆分，也要付出什么代价

拆分可能让不同功能选择不同工艺，也可能让已有芯粒在多个产品中复用。对于一定的缺陷条件，较小裸片可能更容易获得可用器件；但系统的最终成本还受裸片数量、测试、封装、组装良率和产量等影响。

拆分也把原来在同一裸片内的部分通信变成跨裸片通信。两端需要接口电路和封装连接，还要考虑带宽、延迟、功耗、散热和测试。因此，芯粒方案并不自动更便宜或更快，需要按具体系统比较。[OCP 芯粒成本分析](https://www.opencompute.org/chiplets/66/cost-modeling-analysis-for-heterogeneous-integration-of-chiplets)

## 接下来怎么读

- [芯粒怎样在封装内连接](./in-package-connections.md)：看数据线如何经过凸点、布线结构或键合界面。
- [一次跨芯粒通信](./cross-die-communication.md)：从一次读取理解接口、通道和返回结果的分工。
- [AMD EPYC 9004 产品案例](../04-product-cases/amd-epyc-9004-gmi.md)：看另一代 EPYC 的计算芯粒与 I/O die 怎样连接。
