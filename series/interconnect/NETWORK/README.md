# 系统网络：节点之间怎样传输数据并确认完成？

<span id="系统网络ethernetrdma-与-infiniband-怎样配合"></span>

服务器、存储和加速器交换数据，需要端点准备合法资源、网络传输数据，以及软件正确观察完成。本专题沿这条路径展开七章、34 页：本导读、七篇章节导读和 26 篇正文。

## 先分清对象

| 名称 | 主要职责 |
| --- | --- |
| Ethernet | 定义 MAC 与物理层等链路能力，介质可以是铜缆、背板或光纤 |
| IP、TCP、UDP | 分别提供网络寻址转发和不同传输服务 |
| RDMA | 通过支持的传输与访问操作交付数据，仍需要权限和同步 |
| RoCE | 在 Ethernet 网络上承载相应 RDMA 传输 |
| InfiniBand | 包含交换网络、管理与传输服务的互连架构 |
| Ultra Ethernet | 涉及软件接口、UET 传输及网络增强，需核对版本和 profile |

这些名称不处于同一抽象层。RDMA 不是与 Ethernet 对立的一种线缆，使用网络也不自动扩展 CPU 或 GPU 的缓存一致性域。[IEEE 802.3](https://standards.ieee.org/ieee/802/10422/)、[IBTA](https://infinibandta.org/ibta-specification/)

## 阅读顺序

1. [01 基础概念](01-foundations/README.md)：区分消息、操作、包和帧，建立主机与 NIC 数据路径。
2. [02 Ethernet 与 IP 网络](02-ethernet-and-ip/README.md)：解释转发、多路径、排队、重传与拥塞控制。
3. [03 RDMA 端点](03-rdma-endpoints/README.md)：建立队列、授权、操作、完成和缓冲区生命周期契约。
4. [04 RoCE](04-roce/README.md)：跟踪 RoCEv2 封装、PFC、ECN/CNP 与部署条件。
5. [05 InfiniBand](05-infiniband/README.md)：解释子网管理、SL/VL、信用，并比较不同 RDMA 承载。
6. [06 系统集成与新协议](06-system-integration/README.md)：分析 GPU 内存访问、通信库选路及 UE 1.1 的能力边界。
7. [07 性能、诊断与查阅](07-performance-and-reference/README.md)：从业务流量建立预算、测试与诊断证据，并提供资料入口。

## 按目标选择路线

- 建立整体理解：基础概念 → Ethernet 与 IP → RDMA → 对应协议 → 性能与诊断。
- 学习 RDMA：基础概念 → RDMA 端点 → RoCE 或 InfiniBand → 测试。
- 分析多机 GPU：RDMA 完成 → 系统集成 → 性能预算，并联读加速器专题。

## 一次远端数据传输

构造例子：A、B 使用兼容的 RoCEv2 RC 连接。双方建立合法资源，A 持有有效源缓冲，B 授权目标 MR，并提供应用协议所需的接收与通知资源。A 提交写操作，NIC 经交换网络发送，B 的 NIC 检查并放置数据。

A 的提交成功、A 的成功工作完成、B 的相应通知以及 B 的应用消费是不同事件。普通 Write 和 Write with Immediate 的通知方式不同，详细见[操作比较](03-rdma-endpoints/send-read-write-and-atomics.md)与[完成时序](03-rdma-endpoints/completion-ordering-and-lifetime.md)。

网卡卸载数据路径后，软件仍需建立连接、管理内存和处理失败。实际性能取决于端点、网络、拥塞与消费者，不能只用链路额定速率推断。

## 与其他专题的关系

| 专题 | 保留的主要职责 | 本专题补充什么 |
| --- | --- | --- |
| [PCIe](../PCIE/README.md)与 [DMA](../../microarchitecture/DMA/wiki/README.md) | 主机设备事务、地址、ring 与缓冲交接 | NIC 两侧如何连接端到端通信 |
| [NoC](../NOC/README.md) | 通用路由、信用、拓扑与前进性基础 | Ethernet／IB 的转发与管理机制 |
| [一致性与内存互连](../COHERENCE/README.md) | 缓存副本、顺序与设备一致性域 | 数据到达后消费者如何建立正确依赖 |
| [加速器互连](../SCALEUP/README.md) | 多卡访问、集体通信与并行流量 | NIC 放置、网络承载及跨节点拥塞 |
| [SerDes](../SERDES/README.md)、[CPO](../CPO/README.md) | 物理信号、光引擎与封装 | 物理路径在网络中的观察边界 |

所有数值算例均注明假设。命令示例不冒充实测，具体设备能力和规范版本见[术语与资料](07-performance-and-reference/glossary-and-sources.md)。
