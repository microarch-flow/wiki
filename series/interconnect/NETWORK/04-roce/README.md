# 04 RoCE

上级：[系统网络](../README.md)

先跟踪一次 RoCEv2 传输，再分别解释逐跳暂停和端到端调速，最后把这些机制放回部署条件。基本操作与完成由上一章负责，本章集中讨论以太网承载与控制。

## 阅读顺序

1. [RoCEv2 封装与路径](rocev2-packet-and-path.md)：UDP/IP 与 RDMA 传输怎样配合。
2. [PFC 与 Headroom](pfc-headroom-and-stalls.md)：接收空间、暂停传播和停顿风险。
3. [ECN、CNP 与 DCQCN](ecn-cnp-and-dcqcn.md)：网络信号怎样改变源端速率。
4. [部署条件与隔离](deployment-and-isolation.md)：地址、MTU、QoS、权限如何对齐。

## 阅读提示

RoCE 与[InfiniBand](../05-infiniband/README.md)是并列的网络学习分支。只研究其中一种时，可以在完成[RDMA 端点](../03-rdma-endpoints/README.md)后选择相应分支。
