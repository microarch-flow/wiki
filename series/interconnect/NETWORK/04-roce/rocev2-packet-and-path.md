# 一次 RoCEv2 传输：RDMA 怎样穿过 IP 网络？

上级：[RoCE](README.md)

RoCEv2 把 RDMA 传输放入 UDP/IP，再由 Ethernet 承载。外层负责在 IP 网络中转发，端点中的传输机制负责相应 RDMA 服务。交换机通常不需要理解应用的远端内存地址。

## 从操作到帧

以 RC Write 为例，A 提交本地源缓冲、长度、B 的目标地址与 rkey。NIC 按传输与路径参数生成一个或多个包。B 的 NIC 处理传输状态、检查权限并放置数据；相应确认和错误处理按 RC 契约执行。

| 封装层 | 主要作用 |
| --- | --- |
| Ethernet | 在当前链路上传输帧，支持相应链路 QoS |
| IPv4／IPv6 | 指明网络源和目的，经过路由到达目标 |
| UDP | 提供 RoCEv2 封装及可用于散列的字段 |
| RDMA 传输头及操作相关头 | 标识端点、操作、序号及所需远端访问信息 |
| 数据与完整性字段 | 携带载荷并支持对应校验 |

UDP 目的端口为 **4791**。UDP 自身不提供可靠传输；RC 的保证来自封装内的 RDMA 传输。RoCE 也可以使用不同传输服务，不能把 RC 的保证泛化到所有 QP。[NVIDIA RoCE 文档](https://networking-docs.nvidia.com/mlnxofedswum/23103220lts/rdma-over-converged-ethernet-roce)

## 与 RoCEv1 的区别

RoCEv1 直接使用 Ethernet 承载，通常限定在相应二层域。RoCEv2 增加 IP/UDP 封装，可以通过 IP 路由。两端必须选择兼容模式；普通 IP ping 成功不能证明 QP、GID、权限或 RDMA 资源已经正确建立。

RoCE 网络不依赖 InfiniBand 子网管理器。使用相似 verbs API，不表示它使用相同的 LID、路径管理和故障迁移机制。连接管理可通过 RDMA CM 处理相应地址和路径参数。

## 路径可达之后还要检查什么

先核对源设备、端口、GID 类型与网络接口，再核对路径 MTU、优先级分类、接收资源和拥塞配置。路由器转发成功，但某跳丢弃了大包、分类不一致或接收队列不足，仍会造成停顿或错误。

主机 socket 抓包和 netdev 统计未必覆盖全部卸载的 RDMA 流量，应使用设备支持的统计与抓包入口。不要把“看不到包”直接解释为“网卡没有发送”。配置关系见[部署条件](deployment-and-isolation.md)，恢复和拥塞机制见本章后续文章。
