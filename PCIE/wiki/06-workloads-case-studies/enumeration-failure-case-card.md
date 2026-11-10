# 枚举失败案例卡

上级：[06 工作负载与案例](./README.md)

相关：[配置空间、BAR 与 Capability](../03-configuration-enumeration-addressing/config-space-bar-capability.md)、[枚举、总线号与资源分配](../03-configuration-enumeration-addressing/enumeration-bus-number-resource-allocation.md)

## 这页在回答什么问题

设备插上去后“系统看不见”时，应该先怎样拆问题，而不是立刻怀疑所有层都坏了。

## 典型现象

- **配置读不可达**：设备未出现在枚举结果，检查训练状态、桥的次级/下级 bus 范围和配置请求路径。
- **BDF 可见但 MMIO 不通**：检查 BAR 是否获地址、上游桥窗口是否覆盖，以及 Function 的 Memory Space Enable 是否打开。BAR 资源不足不等于 Function 未枚举。
- **MMIO 正常但设备 DMA 不动**：检查 Bus Master Enable、DMA 映射、权限与设备状态。关闭 Bus Master 主要影响设备发起的内存事务，不会单独使配置读消失。所需 capability 是否使能另按设备接口检查。

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

因为它提醒你：配置发现、地址资源和运行使能是不同阶段；只说“枚举失败”会丢掉决定下一步的证据。

## 一句话理解

设备没被系统看见时，先把问题限定在 `链路建立 -> 配置空间可达 -> 资源分配闭环` 这条主线上。
