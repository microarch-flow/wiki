# 01 基础概念

上级：[系统网络](../README.md)

先固定通信对象和观察层，再从主机数据路径理解链路指标。读完本章，应能区分一条应用消息、一次 RDMA 操作和多个线上帧。

## 阅读顺序

1. [对象与分层](objects-and-layers.md)：应用、端点、包与帧分别表示什么。
2. [主机与 NIC 路径](host-nic-data-path.md)：软件、设备、内存和网络怎样衔接。
3. [帧、MTU 与包率](frame-mtu-and-rate.md)：把额定速率换算成明确口径的预算。

## 阅读提示

后续先读[Ethernet 与 IP 网络](../02-ethernet-and-ip/README.md)，再进入 RDMA。已有网络基础的读者可直接转到[RDMA 端点](../03-rdma-endpoints/README.md)。
