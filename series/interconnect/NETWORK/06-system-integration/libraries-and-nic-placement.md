# 通信库与 NIC 放置：应用怎样选到真实网络路径？

上级：[系统集成与新协议](README.md)

应用调用通信库后，数据仍需映射到进程、内存、设备和网络端口。库的名称不能唯一确定线上协议；启动连接、控制通信和大块载荷还可能走不同接口。

## 分开看软件层次

MPI 规定应用通信语义；具体 MPI 实现可以使用 UCX 等通信框架。UCX 根据能力和配置选择适用传输。NCCL 为 GPU 集体通信和点对点操作选择其支持的网络后端及其他路径。这些关系存在版本与实现差异，不能画成所有系统都固定经过的单一栈。

[UCX FAQ](https://openucx.readthedocs.io/en/master/faq.html)说明设备和传输选择，包括多轨及 GPU 内存支持。NCCL 的控制接口选择和 RDMA 设备选择也应分别核对。[NCCL 网络排查](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting/networking_troubleshooting.html)

## 把放置写成可检查的映射

记录 rank→CPU 亲和性→内存 NUMA 节点→GPU→NIC 端口→网络轨道。两张网卡即使额定速率相同，也可能具有不同的 PCIe 距离和共享上行；通信线程放在远端 NUMA 节点还可能增加主机访问代价。

构造例子：两颗 GPU 分别靠近 NIC0 和 NIC1，但应用的全部跨节点数据都走 NIC0。NIC1 空闲并不说明任务不需要带宽，而可能说明放置或库选择没有利用该资源。若算法与网络允许分担，还要确认两条路径不会在更上层重新汇聚到同一瓶颈。

如果每台服务器只有一块网卡，放置还能改变什么？固定两台服务器各两张 GPU，改变逻辑环顺序，两张同机 GPU 的跨机流量可能叠加在同一个发送口。可以沿图计算每个方向的字节数，再推时间下界。[两机四卡的链路负载表](../../SCALEUP/04-software-and-collectives/four-gpu-allreduce-egress.md#link-bytes)

## 为什么不能只调一个环境变量

限制设备列表可用于定位问题，但可能排除用于初始化或辅助通信的接口；强制某种传输也可能关闭适合其他消息大小的路径。调试应先保存自动选择的日志，再做单变量对照，最后恢复目标配置。

多轨收益依赖消息大小、协议、端点能力和流量分配。两个端口的峰值之和不是单个小消息的可用带宽，更不意味着时延减半。

## 算法与承载分别验证

先用端点微基准确认选定 NIC 路径，再运行多进程或多 GPU 测试，最后观察应用关键阶段。NCCL 的参与者、流依赖与 Ring／Tree 选择继续阅读[通信库契约](../../SCALEUP/04-software-and-collectives/nccl-rccl-contracts.md)和[通信映射](../../SCALEUP/04-software-and-collectives/collective-mapping-and-offload.md)。本页只解释网络路径如何被选择和占用。
