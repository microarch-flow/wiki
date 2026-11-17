# InfiniBand、RoCE 与 iWARP：相似 RDMA 接口为何需要不同网络？

上级：[InfiniBand](README.md)

选择 RDMA 方案时，应比较完整路径及运维条件。仅比较某一代产品的峰值速率，无法回答应用移植、网络管理或故障恢复问题。

## 把比较放在同一层

| 维度 | InfiniBand | RoCEv2 | iWARP |
| --- | --- | --- | --- |
| 典型承载 | InfiniBand 交换网络 | Ethernet 上的 UDP/IP | 通常采用 TCP/IP 上的 RDMA 协议栈 |
| 网络管理 | SM、SA、LID、分区等 | Ethernet/IP 路径及 QoS 配置 | IP 路径、TCP 及端点能力 |
| 可靠性来源 | 所选 IB 传输服务 | 所选 RDMA 传输服务，不能归功于 UDP | TCP 与其上的 DDP/RDMAP 规则 |
| 接口观察 | 可使用 verbs 等软件接口 | 可使用相似 verbs 接口 | 接口支持取决于软件与提供者 |
| 部署评估 | 设备、管理、路由和资源配置 | 拥塞控制、丢包恢复及可选 PFC | TCP 行为、端点卸载与应用支持 |

此处的 InfiniBand 和 RoCE 不限定所有应用都使用 RC。RC、UC、UD 的能力边界见 [RDMA 编程手册](https://docs.nvidia.com/rdma-aware-networks-programming-user-manual-1-7.pdf)。iWARP 的分层和适用性见 [RFC 5045](https://www.rfc-editor.org/rfc/rfc5045.html)，操作语义见 [RFC 5040](https://www.rfc-editor.org/rfc/rfc5040.html)。

## API 相似不能证明线上互通

应用可以通过通用接口表达发送或读写，但提供者仍需把操作映射到具体设备与协议。两个端点都能调用 libibverbs，不说明一个 IB 端口能直接与 Ethernet 端口交换相同帧。双模式设备也要核对端口模式和实际连接。

同样，iWARP 使用 TCP，不表示普通 TCP socket 对端无需 RDMA 协议支持就能执行远端写。网络可路由、传输可连接、操作可执行是逐层增加的条件。

## 先明确业务约束再选择

如果已有 IB 设施，应评估管理和路径策略、应用支持及故障域；如果复用 Ethernet，应评估混合流量、QoS、拥塞和端点恢复；如果使用 TCP 承载的 RDMA，应核对实现能力及实际工作负载。

比较实验应使用相同消息规模、完成定义、CPU/GPU 内存位置和并发，分别报告吞吐、延迟分布与主机开销。不能把一项设备微基准写成某一协议在所有场景下更快。

Ultra Ethernet 的新传输另见 [UET](../06-system-integration/ultraethernet-uet.md)。它不应被简化为 RoCE 的新名称，也不以“替代所有现有方案”为本文结论。
