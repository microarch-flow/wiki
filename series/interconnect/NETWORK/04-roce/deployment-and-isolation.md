# RoCE 部署条件：地址、MTU、QoS 与权限怎样对齐？

上级：[RoCE](README.md)

链路建立只是起点。一次 RDMA 操作要成功，需要端点资源合法、网络路径可达，并且每一跳对帧大小和流量类别的处理符合部署设计。

## 按依赖顺序建立可用路径

先确认端口模式、速率、IP 地址与路由，再确认 RDMA 设备和端口与 netdev 的对应关系。选择 GID 时同时检查 GID 类型和关联接口，不能跨机器机械复制一个索引。之后核对连接参数、QP path MTU 与两端内存权限，再执行简单传输。

| 配置层次 | 需要匹配的内容 | 常见误判 |
| --- | --- | --- |
| IP 与路径 | 地址、路由、邻居状态、路径 MTU | ping 通就认为 RDMA 可用 |
| RDMA 端点 | GID、传输类型、接收资源、MR 权限 | 端口 Active 就认为操作合法 |
| QoS | DSCP／PCP 到内部优先级、队列的映射 | 两端 DSCP 相同就认为每跳分类相同 |
| 拥塞与缓冲 | ECN、PFC、调度、阈值及设备能力 | 复制默认值就认为所有拓扑都适用 |

具体地址及连接规则见 [MLNX_OFED RoCE 文档](https://networking-docs.nvidia.com/mlnxofedswum/23103220lts/rdma-over-converged-ethernet-roce)。不同提供者可能使用不同配置接口，操作前应固定版本。

## 有损与无损不是一个开关的结论

[Cumulus Linux](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-515/Layer-1-and-Switch-Ports/Quality-of-Service/RDMA-over-Converged-Ethernet-RoCE/)明确区分基于 ECN 的 lossy 模式与启用 PFC、ECN 的 lossless 模式。这说明不能声称所有 RoCE 都必须开启 PFC。

同时，关闭 PFC 不会自动得到良好性能。端点的丢包恢复、拥塞控制、缓冲及业务负载需要共同验证。无损模式也要检查暂停传播、死锁恢复和资源隔离。选项应按目标吞吐、尾延迟、运维复杂度和故障影响比较。

## 隔离分布在多个位置

MR 权限保护特定端点资源；网络策略控制可达范围；虚拟功能和设备资源管理限制不同租户的使用。三者不能互相替代。rkey 不提供通用加密认证，优先级也不等于安全边界。

验证时先在隔离的测试范围内建立单连接基线，再增加并发、接收端压力和共享链路流量。不要直接在生产路径试改全局 PFC 或 MTU。记录变更前后计数、时延及配置，才能区分网络变化与端点资源变化。具体工具见[测试方法](../07-performance-and-reference/benchmarking.md)。
