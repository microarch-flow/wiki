# 03 RDMA 端点

上级：[系统网络](../README.md)

RDMA 不仅是一条搬运数据的硬件路径，还包含资源、授权、操作和完成契约。本章以 RC 为主要示例，逐项说明适用条件；不把 RC 保证套到所有服务。

## 阅读顺序

1. [QP、CQ 与连接](queues-and-connection.md)：请求进入设备前后有哪些状态。
2. [注册与权限](memory-registration-and-permissions.md)：目标地址怎样成为合法访问对象。
3. [操作与接收资源](send-read-write-and-atomics.md)：双方分别需要准备什么。

## 阅读提示

读完三类操作后，可以回到[4 KiB 案例的完成时序](../01-foundations/host-nic-data-path.md#completion)，核对提交、工作完成和应用消费分别释放哪一项资源。

接下来阅读[RoCE](../04-roce/README.md)。排查具体问题时，可直接使用[性能与诊断](../07-performance-and-reference/README.md)，并沿文中链接补足机制前提。
