# 系统网络：Ethernet、RDMA 与 InfiniBand 怎样配合？

服务器或计算节点交换数据时，需要共同的链路、网络和端点行为。网络采用哪种物理介质、怎样转发数据，以及应用使用什么访问语义，是不同问题。

## 先分清对象

| 名称 | 回答的问题 |
| --- | --- |
| Ethernet | 帧怎样通过 MAC 与所选物理层传输；物理介质可以是铜缆、背板或光纤等。 |
| RDMA | 怎样让一个端点对远端内存执行受支持的数据传输操作。 |
| RoCE | 怎样在以太网网络上承载 RDMA 传输。 |
| InfiniBand | 一套包括交换网络和传输语义的互连架构，也支持 RDMA。 |

[IEEE 802.3](https://standards.ieee.org/ieee/802.3/10422/) 定义 Ethernet 的 MAC 和多种物理层；[InfiniBand Trade Association](https://infinibandta.org/ibta-specification/) 维护 InfiniBand 和 RoCE 相关规范。RDMA 是访问能力，不能当作与 Ethernet 同一层的另一种线缆。

## 一次远端数据传输

假设两台服务器已建立兼容的 RoCE 连接，目标缓冲区已按软件和设备要求注册并授权。源端提交一次 RDMA 写请求；源端网卡通过以太网发送，交换网络将数据送到目标网卡；目标网卡按权限和协议处理写入。应用何时能安全读取结果，还要遵守该操作的完成与同步契约。

数据路径可以由网卡执行，但连接建立、缓冲区注册、权限和同步仍需要系统参与。实际时延和吞吐也受端点、网络拥塞、流控与负载影响，不能只用链路额定速率推断。

## 与其他专题的关系

服务器网卡连接主机的方式可读 [PCIe](../../PCIE/wiki/README.md)；网卡外侧的电信号可读 [SerDes](../../SERDES/wiki/README.md)，光引擎与封装可读 [CPO](../../CPO/wiki/README.md)。[加速器互连](../../SCALEUP/wiki/README.md)关注加速器访问对端资源的契约，两者可以在同一系统中同时出现。
