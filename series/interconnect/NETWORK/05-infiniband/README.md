# 05 InfiniBand

上级：[系统网络](../README.md)

InfiniBand 有自己的子网管理、地址和链路资源组织。本章复用 RDMA 端点契约，补足这些网络机制，再与 RoCE 和 iWARP 做同层比较。

## 阅读顺序

1. [子网、地址与 SM](subnets-addresses-and-sm.md)：拓扑发现、路径配置与分区的职责。
2. [SL、VL 与信用](vl-credit-routing-and-congestion.md)：分类、仲裁、缓冲和前进条件。
3. [IB、RoCE 与 iWARP](ib-roce-iwarp-comparison.md)：比较承载和运维条件，避免只比较峰值。

## 阅读提示

本章不重复 MR 与 CQ 基础。遇到操作完成问题，回看[RDMA 端点](../03-rdma-endpoints/README.md)；分析真实系统时继续读[系统集成](../06-system-integration/README.md)。
