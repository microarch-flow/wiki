# ECN、CNP 与 DCQCN：发送端怎样知道该减速？

上级：[RoCE](README.md)

拥塞通常发生在共享出口，发送方却位于别处。端到端控制需要把网络中的拥塞信息送回发送方，并由发送方改变注入速率。ECN 是标记，CNP 是反馈消息，DCQCN 是一种具体调速方案。

## 跟踪一次反馈

回到[两股流争用一个出口的算例](pfc-headroom-and-stalls.md#one-egress)。第 2 μs，S 的出口积压达到 25,000 B，开始给可标记的数据包设置 CE。此时 A 的网卡还在按原速发送：标记在发往 B 的包上，A 暂时看不到它。

跟着来自 A 的一个标记包往下走。它先排队、离开 S，再到达 B 的网卡。B 的拥塞反馈逻辑识别标记，按相应规则向 A 发送 CNP。原 DCQCN 设计对同一流的反馈频率做了限制，不能用标记包数直接代替 CNP 数。只有 CNP 送达 A、源端调低发送速率，而且随后发出的包抵达 S，S 的入口才真正看到流量变化。源 C 有自己的反馈过程。[DCQCN 原论文，第 3 节](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/lossless.pdf)

同一传输中，**B 发 CNP 表示 B 的网卡观察到了拥塞信号**。A 的应用不能据此复用源缓冲，B 的应用也不能据此读取整条消息。应用应观察所选传输操作规定的成功完成或通知；另一个线程或设备接手数据时还要按平台约定同步。[发送方与接收方各观察哪种完成](../01-foundations/host-nic-data-path.md#completion)

## DCQCN 的关键状态

A 的网卡为受控流保存当前速率、恢复时参考的目标速率和拥塞程度估计。原方案处理 CNP 时记录减速前的当前速率作为目标，再按拥塞估计降低当前速率。之后由定时器或已发送字节数触发恢复，先向目标速率靠拢，再按算法逐步抬高目标。降得太晚，S 仍会继续积压；降得过多，而恢复又慢，S 的出口即使有空也可能等不到包。

这里解释控制职责，不复制厂商默认参数。具体 NIC 可能提供不同算法、参数单位和扩展，必须固定设备、固件和驱动版本。[DCQCN 原论文](https://www.microsoft.com/en-us/research/publication/congestion-control-for-large-scale-rdma-deployments/)

## 与 DCTCP、PFC 区别在哪里

<div class="bus-read-trace" markdown="1">

| 机制 | 反馈或控制位置 | 核心作用 |
| --- | --- | --- |
| DCTCP | TCP 接收反馈与发送端窗口 | 根据标记比例调整 TCP 拥塞窗口 |
| DCQCN | RoCEv2 接收反馈与源 NIC | 根据反馈调节发送速率 |
| PFC | 相邻链路及优先级 | 接收资源不足时暂停相应上游发送 |

</div>

DCTCP 的 TCP ACK 反馈不能直接当作 CNP，PFC 暂停时间也不是端到端公平性指标。[DCTCP 规范说明](https://www.rfc-editor.org/rfc/rfc8257.html)

## 怎样判断控制环有效

用相同消息大小和并发对比吞吐、尾延迟、队列、ECN/CNP 增量、重传和 PFC 暂停。单独看到 CNP 增多，可能表示拥塞更严重，也可能表示反馈开始正确工作，需要结合其他证据判断。

反馈报文本身也需要得到服务。RoCE 流量与 CNP 如何分类和调度，应核对整条路径的配置；本专题不把某一产品使用的优先级数字当作协议常量。配置实例的适用边界见 [Cumulus RoCE](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-515/Layer-1-and-Switch-Ports/Quality-of-Service/RDMA-over-Converged-Ethernet-RoCE/)。
