# Root Complex、Switch、Endpoint 在系统里各做什么

上级：[02 链路、分层与事务基础](./README.md)

相关：[分层架构：Transaction / Data Link / Physical](./layered-architecture-transaction-data-link-physical.md)、[枚举、总线号与资源分配](../03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md)

## 这页在回答什么问题

PCIE 拓扑里最核心的几个角色分别在系统里承担什么职责，它们为什么要分开。

## 三个基本角色

- `Root Complex`：主机侧进入 PCIE fabric 的根，负责把 CPU / memory / host software 和 PCIE 世界连起来
- `Switch`：扩展拓扑，把一个上行口分成多个下行口
- `Endpoint`：设备侧功能承载者，比如 NIC、NVMe、GPU 或加速器

## 这三个角色不是平替关系

- Root Complex 决定主机如何发 config、MMIO 和 DMA 相关事务
- Switch 决定拓扑扩展能力、P2P 可行性和部分隔离边界
- Endpoint 决定设备侧 DMA、queue、interrupt 和本地缓冲行为

## 一个最常见系统图

1. CPU 和 memory 在主机域内
2. Root Complex 把主机事务送入 PCIE fabric
3. Switch 扩展成多个下游端口
4. Endpoint 对应具体设备功能

这条路径决定了很多现象：

- 为什么设备要先被枚举
- 为什么同一台主机上的不同插槽行为会不同
- 为什么设备 DMA 不只是“自己读内存”

## 对体系结构最重要的判断

PCIE 拓扑不是背景板，它直接影响：

- 资源分配
- 中断路由
- P2P 能否成立
- 带宽共享和拥塞位置
- 热插拔和可管理性

## 一句话理解

Root Complex 决定主机入口，Switch 决定拓扑扩展，Endpoint 决定设备行为，三者一起定义了 PCIE 系统的边界条件。
