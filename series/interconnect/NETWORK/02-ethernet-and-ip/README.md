# 02 Ethernet 与 IP 网络

上级：[系统网络](../README.md)

本章从可达性进入共享网络，依次解释转发、多路径、排队和传输控制。先理解包经过哪里，再判断为什么会等待或重传。

## 阅读顺序

1. [转发与传输分工](forwarding-and-transport.md)：Ethernet、IP、TCP 和 UDP 的职责。
2. [Clos、ECMP 与多轨](clos-ecmp-and-rails.md)：拓扑、流映射和共享出口的关系。
3. [队列与 Incast](queues-incast-and-tail-latency.md)：突发怎样产生排队与尾延迟。
4. [重传与拥塞控制](loss-recovery-and-ecn.md)：可靠性、接收流控和网络拥塞分别如何处理。

## 阅读提示

接下来阅读[RDMA 端点](../03-rdma-endpoints/README.md)。排查具体问题时，可直接使用[性能与诊断](../07-performance-and-reference/README.md)，并沿文中链接补足机制前提。
