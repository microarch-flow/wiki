# Peer-to-Peer、Switch 与拓扑约束

上级：[07 高级主题](./README.md)

相关：[Root Complex、Switch、Endpoint 在系统里各做什么](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md)

## 这页在回答什么问题

为什么同样是两块 PCIE 设备，peer-to-peer 直连传输有时能做、有时很难做。

## P2P 在说什么

P2P 指的是设备和设备之间通过 PCIE fabric 直接交换数据，而不是每次都经 CPU 主动搬运。

## 为什么它受拓扑限制

- 设备可能不在同一个 switch 域下
- root complex 行为和平台策略可能不同
- 地址转换、隔离和路由规则可能不放行

## 工程上最重要的判断

P2P 不是“设备支持就行”，而是：

- 拓扑是否允许
- 平台是否支持
- 映射和安全策略是否闭环

## 一句话理解

P2P 的难点不在概念，而在它把拓扑、路由、隔离和平台策略同时拉进了同一个问题里。
