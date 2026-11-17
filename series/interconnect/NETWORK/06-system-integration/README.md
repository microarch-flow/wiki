# 06 系统集成与新协议

上级：[系统网络](../README.md)

从合法的端点传输出发，检查 GPU 内存、通信软件和 NIC 放置怎样组成实际路径。最后通过 UE 1.1 说明新协议的分层与能力声明。

## 阅读顺序

1. [GPUDirect RDMA](gpudirect-rdma.md)：NIC 访问 GPU 内存后的同步责任。
2. [通信库与 NIC 放置](libraries-and-nic-placement.md)：应用如何选择并占用真实网络。
3. [Ultra Ethernet 与 UET](ultraethernet-uet.md)：版本、子层、profile 与实现边界。

## 阅读提示

接下来阅读[性能、诊断与查阅](../07-performance-and-reference/README.md)。排查具体问题时，可直接使用[性能与诊断](../07-performance-and-reference/README.md)，并沿文中链接补足机制前提。
