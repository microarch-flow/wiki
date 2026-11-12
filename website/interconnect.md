# 芯片与系统互连

从通信请求出发，区分事务语义、网络转发和物理链路。一个系统可以同时使用这些层次。

- [片上事务与总线（BUS）](BUS/wiki/README.md)：事务、握手、仲裁和桥接。
- [片上网络（NoC）](NOC/wiki/README.md)：路由、缓冲、流控与拓扑。
- [系统 I/O 互连（PCIe）](PCIE/wiki/README.md)：设备枚举、地址和事务。
- [高速电链路（SerDes）](SERDES/wiki/README.md)：发送、接收、训练和验证。
- [共封装光学（CPO）](CPO/wiki/README.md)：光引擎、封装和系统集成。

跨芯粒应用可先读 [SerDes 的芯粒与 D2D 文章](SERDES/wiki/08-system-applications/chiplet-and-d2d.md)。CXL 的现有材料见 [CXL 与 PCIe 的边界](PCIE/wiki/07-advanced-topics/cxl-and-pcie-boundary.md)。这些链接属于相关专题的延伸阅读。
