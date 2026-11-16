# CXL：从设备发现到内存访问

CXL（Compute Express Link）把 I/O、缓存和内存访问协议组织在同一系统互连体系中。读懂一条路径时，应先确认主机、设备类型、链路模式和软件配置，而不是仅凭连接器或线速率判断能力。

## 三类协议各做什么

以 [CXL 3.0 规范](https://computeexpresslink.org/wp-content/uploads/2024/02/CXL-3.0-Specification.pdf) 描述的典型主机与设备关系为例：

| 协议 | 主要职责 |
| --- | --- |
| CXL.io | 设备发现、配置、寄存器访问等 I/O 功能，基于 PCIe 事务。 |
| CXL.cache | 支持设备对主机内存进行一致性访问和缓存。 |
| CXL.mem | 支持主机访问设备连接的内存，并提供相应内存语义。 |

具体设备不一定实现全部能力。更复杂的交换和设备间访问应按目标版本和拓扑核查，不能把上表当成所有事务方向的完整清单。

## 一次内存扩展访问

假设主机连接支持 CXL.io 和 CXL.mem 的 Type 3 内存扩展设备，双方链路已就绪，软件也已发现并配置可访问的设备内存。处理器读取其中一个地址时，主机将访问送往该设备；设备的内存控制器访问其连接的内存，并将数据返回。应用何时能使用这块内存，还取决于系统的软件资源管理。

这个例子说明访问路径，不代表该设备会用 CXL.cache 缓存主机内存，也不表示设备内存的延迟一定高于或低于某个本地内存。要比较性能，需要给出具体拓扑、负载和测量边界。

## 扩展、池化与共享

**扩展**关注主机可使用的内存容量；**池化**关注设备内存如何在主机之间分配；多个主机能否同时访问同一位置并保持所需一致性，是另一项能力。它们依赖规范版本、设备、交换结构和软件配置。现有[存储系统文章](../../storage/06-system-integration/future-packaging-cxl-near-memory.md)继续讨论数据放置和系统代价。

先读 [PCIe 与 CXL 的边界](../PCIE/07-advanced-topics/cxl-and-pcie-boundary.md)，可补齐设备发现、配置和物理链路的背景。关于 CXL 2.0 池化与共享的区分，参见[联盟问答](https://computeexpresslink.org/blog/cxl-2-0-specification-memory-pooling-questions-from-the-webinar-part-2-2391/)。
