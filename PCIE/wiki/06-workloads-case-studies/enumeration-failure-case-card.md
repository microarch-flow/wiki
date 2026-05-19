# 枚举失败案例卡

上级：[06 工作负载与案例](./README.md)

相关：[配置空间、BAR 与 Capability](../03-configuration-enumeration-addressing/config-space-bar-capability.md)、[枚举、总线号与资源分配](../03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md)

## 这页在回答什么问题

设备插上去后“系统看不见”时，应该先怎样拆问题，而不是立刻怀疑所有层都坏了。

## 典型现象

- 设备没有出现在系统枚举结果里
- 设备能被看到，但 BAR 没正确分配
- 某些 capability 缺失或 bus mastering 没打开

## 最短排查链

1. 先看链路是否训练成功
2. 再看配置空间是否可读
3. 再看 bridge / switch / bus number / 资源窗口是否闭环
4. 最后再看驱动是否依赖了未开启的 capability

## 最常见根因

- 物理链路没起来或训练不稳
- 上游 bridge 资源窗口配置不完整
- BAR 空间规划冲突
- 多级拓扑下 bus number 不够或分配异常

## 为什么这个案例很重要

因为它提醒你：`枚举失败` 常常是资源组织问题，不一定是设备功能本身有问题。

## 一句话理解

设备没被系统看见时，先把问题限定在 `链路建立 -> 配置空间可达 -> 资源分配闭环` 这条主线上。
