# Peer-to-Peer、Switch 与拓扑约束

上级：[07 高级主题](./README.md)

相关：[Root Complex、Switch、Endpoint 在系统里各做什么](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md)

## 这页在回答什么问题

为什么同样是两块 PCIE 设备，peer-to-peer 直连传输有时能做、有时很难做。

## P2P 在说什么

P2P DMA 指一个设备发起事务，把载荷直接读自或写入另一个设备可供访问的资源，例如对端 BAR 中可用于 DMA 的窗口。普通设备到主机内存的 DMA 同样无需 CPU 逐字节搬运，因此不能仅以 CPU 是否主动复制区分。

## 为什么它受拓扑限制

- 设备可能不在同一个 switch 域下
- root complex 行为和平台策略可能不同
- 地址转换、隔离和路由规则可能不放行

例如两个 EP 在同一 Switch 下，软件建立允许的对端 BAR 映射，EP A 向 EP B 的窗口发写请求；若路由与 ACS 配置允许，Switch 可在本地下行口转发，不占上行链路。ACS 重定向可能改变路径；跨主桥的转发、映射和隔离若不受平台支持，P2P 请求可能被拒绝或不可达。只有软件明确选择并建立主机缓冲中转时才应把它建模为两次普通 DMA，不能假定硬件自动回退。参见 [Linux P2P DMA 文档](https://docs.kernel.org/driver-api/pci/p2pdma.html)。

## 工程上最重要的判断

P2P 不是“设备支持就行”，而是：

- 拓扑是否允许
- 平台是否支持
- 映射和安全策略是否闭环

## 一句话理解

P2P 的难点不在概念，而在它把拓扑、路由、隔离和平台策略同时拉进了同一个问题里。
