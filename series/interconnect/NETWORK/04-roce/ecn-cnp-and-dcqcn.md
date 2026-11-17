# ECN、CNP 与 DCQCN：发送端怎样知道该减速？

上级：[RoCE](README.md)

拥塞通常发生在共享出口，发送方却位于别处。端到端控制需要把网络中的拥塞信息送回发送方，并由发送方改变注入速率。ECN 是标记，CNP 是反馈消息，DCQCN 是一种具体调速方案。

## 跟踪一次反馈

1. 多个流争用出口，队列达到所配置的 ECN 标记条件。
2. 支持 ECN 的网络设备在包中记录拥塞信号。
3. RoCEv2 接收端处理信号，按相应规则向源端发送 CNP。
4. 源端 NIC 的拥塞控制逻辑更新状态并调节发送速率。
5. 调整后的流量经过网络，形成下一轮队列与反馈。

该过程存在时延。收到反馈前，已经发出的流量不会消失。阈值过晚、反馈延迟或恢复过快，都可能让队列继续增长；调速过强又可能浪费容量。

## DCQCN 的关键状态

DCQCN 原方案维护拥塞程度估计及速率恢复相关状态。收到反馈时降低发送速率，没有持续反馈时分阶段恢复。应把减速、恢复和更新周期放在一起分析，不能只调整一个阈值就声称优化完成。

这里解释控制职责，不复制厂商默认参数。具体 NIC 可能提供不同算法、参数单位和扩展，必须固定设备、固件和驱动版本。[DCQCN 原论文](https://www.microsoft.com/en-us/research/publication/congestion-control-for-large-scale-rdma-deployments/)

## 与 DCTCP、PFC 区别在哪里

| 机制 | 反馈或控制位置 | 核心作用 |
| --- | --- | --- |
| DCTCP | TCP 接收反馈与发送端窗口 | 根据标记比例调整 TCP 拥塞窗口 |
| DCQCN | RoCEv2 接收反馈与源 NIC | 根据反馈调节发送速率 |
| PFC | 相邻链路及优先级 | 接收资源不足时暂停相应上游发送 |

DCTCP 的 TCP ACK 反馈不能直接当作 CNP，PFC 暂停时间也不是端到端公平性指标。[DCTCP 规范说明](https://www.rfc-editor.org/rfc/rfc8257.html)

## 怎样判断控制环有效

用相同消息大小和并发对比吞吐、尾延迟、队列、ECN/CNP 增量、重传和 PFC 暂停。单独看到 CNP 增多，可能表示拥塞更严重，也可能表示反馈开始正确工作，需要结合其他证据判断。

反馈报文本身也需要得到服务。RoCE 流量与 CNP 如何分类和调度，应核对整条路径的配置；本专题不把某一产品使用的优先级数字当作协议常量。配置实例的适用边界见 [Cumulus RoCE](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-515/Layer-1-and-Switch-Ports/Quality-of-Service/RDMA-over-Converged-Ethernet-RoCE/)。
