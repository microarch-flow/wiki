# PCIE vs AXI / NoC：边界与分工

上级：[06 工作负载与案例](./README.md)

相关：[BUS Wiki](../../../BUS/wiki/README.md)、[NOC Wiki](../../../NOC/wiki/README.md)

## 这页在回答什么问题

为什么 PCIE、AXI 和 NoC 都在“搬请求和数据”，但它们不是一个层面的替代品。

## AXI 更常解决什么

- SoC 内模块间事务传输
- 强调 channel、burst、ID、outstanding
- 更贴近片上时序与 RTL 组织

## NoC 更常解决什么

- 多节点片上扩展
- 强调拓扑、路由、拥塞、流控和局部性
- 更贴近大规模片上并发数据流

## PCIE 更常解决什么

- host 和 device 的系统级互连
- 强调枚举、配置、BAR、DMA、MSI-X、IOMMU
- 更贴近设备软件栈和平台资源组织

## 对体系结构最关键的判断

看到性能或调试问题时，先问自己问题属于哪一层：

- 片上数据供给问题
- host-device 契约问题
- 内存系统问题

例如某设备实现 PCIe-to-AXI 桥：主机发起 BAR Memory Read，桥先接收请求，再向片内发 AXI 读；AXI 目标经过 NoC 返回 R 数据后，桥才组装并发出 PCIe CplD。主机观察的是 PCIe 请求到完整 Completion 的时间；片内可分别观察 AXI 地址握手到 R 数据返回的时间。NoC 竞争会延长片内段，PCIe 返回链路竞争也会延长主机观察值。该映射是可选实现，其他设备不一定使用 AXI 或 NoC。

不要把不同层的问题混成“总线不够快”。

## 一句话理解

AXI / NoC 更偏片内互连组织，PCIE 更偏 host-device 系统契约，三者经常串联出现，但分工完全不同。
