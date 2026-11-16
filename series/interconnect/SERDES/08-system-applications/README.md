# 08 系统应用：把链路放回实际连接场景

上级：[SerDes Wiki](../README.md)

同一类高速收发原理可以服务不同系统，但协议、通道、封装和验证目标各不相同。本章比较常见场景，避免只用一个速率或距离判断接口。

## 阅读顺序

1. [PCIe 与以太网：共用什么，又在哪里不同？](./pcie-and-ethernet.md)
2. [增加 lane 还是提高单 lane 速率？](./lane-count-vs-rate.md)
3. [Chiplet 与 D2D：怎样选择封装内互连？](./chiplet-and-d2d.md)
4. [HBM 与 3D 堆叠：数据经过哪些连接？](./hbm-and-3d.md)
5. [CPO：电链路怎样接入光链路？](./cpo-electrical-optical.md)
6. [怎样阅读公开的 SerDes 产品声明？](./product-claims-and-evidence.md)

读完后，应能指出连接的两端、协议、物理路径和数据口径，并知道哪些产品结论仍需要证据。
