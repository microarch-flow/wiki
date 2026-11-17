# InfiniBand 子网：SM、LID、GID 与路径怎样建立？

上级：[InfiniBand](README.md)

InfiniBand 子网不是把 Ethernet 交换机换一个名称。它有自己的端口状态、地址、分区与子网管理机制。物理链路正常后，仍需要管理状态使端点能够通信。

## 管理器先建立什么

Subnet Manager（SM）发现拓扑、分配子网内标识、配置转发及相关策略，并处理拓扑变化。Subnet Administrator（SA）提供路径等管理信息服务。管理功能可以部署在支持的平台上，不能假设一定运行于交换机或一定运行于某个计算节点。

若同一子网配置多个 SM，需要按相应机制选出主 SM，其余承担备用角色。多个管理实例不是让每个包任意选择一个控制器。[NVIDIA InfiniBand 管理说明](https://docs.nvidia.com/networking/display/nvidia-infiniband-security-overview-and-guidelines.pdf)

## 地址和分区分别回答什么

| 对象 | 主要职责 |
| --- | --- |
| GUID | 标识设备或端口等对象，具体使用看管理接口 |
| LID | 在子网中标识可寻址目标，参与本地转发 |
| GID | 提供全局标识，涉及跨子网等路径语义 |
| P_Key | 表示分区成员关系及相应访问约束 |
| QP 标识 | 在到达端点后区分传输上下文 |

同一端口可能有多个逻辑地址或分区配置。P_Key 不是 IP 地址，也不是对所有负载的加密保护。分区检查、成员类型及执行位置应按部署配置核对；不能仅因物理相连就认为两端允许交换数据。

## 从端口到应用的三次检查

先确认物理状态与速率，再确认逻辑端口、SM、地址和路径，最后确认 QP、MR 及应用契约。链路已经建立而端口未进入可通信状态时，应先排查管理配置；应用权限错误则不能靠更换路由解决。

构造例子：A 与 B 均已连接交换机，但尚未获得可用路径或分区不匹配，物理连通仍不能保证业务可达。管理状态修复后，还需要连接建立并发布合法资源，才可以执行[RDMA 操作](../03-rdma-endpoints/send-read-write-and-atomics.md)。

InfiniBand 的架构范围见 [IBTA](https://infinibandta.org/ibta-specification/)。RoCE 不使用相同的子网管理流程，相关差别见[协议比较](ib-roce-iwarp-comparison.md)。
