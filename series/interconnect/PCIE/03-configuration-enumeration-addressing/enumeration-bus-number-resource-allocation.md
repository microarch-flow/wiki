# 枚举、总线号与资源分配

上级：[03 配置、枚举与地址映射](./README.md)

相关：[配置空间、BAR 与 Capability](./config-space-bar-capability.md)

## 这页在回答什么问题

为什么设备插上去以后不是天然就能工作，主机到底做了哪些组织工作。

## 枚举在做什么

枚举过程通常要完成：

1. 从上游扫描配置空间，发现已有的 device/function 和 bridge；BDF 是它们在拓扑中的标识，软件不是凭空分配设备功能。
2. 为桥设置下级 bus number 范围，使配置请求能转发到下游。
3. 读取 Function 的标识、BAR 和 capability；分配 BAR 地址并配置上游桥资源窗口。
4. 驱动按需使能 Memory Space、Bus Master 和所选中断模式。MSI-X 不是枚举或 DMA 的必选项。

## 它为什么本质上是系统资源组织

因为主机不仅是在“找设备”，还在决定：

- 哪段地址留给哪个设备 BAR
- 哪些设备可以发 DMA
- 多级 switch / bridge 下资源窗口怎么切

## 为什么这里经常出问题

常见故障包括：

- BAR 空间不够
- bus number 规划不合理
- 某级 bridge 窗口没打开
- capability 配置不完整

这些问题表面像“设备不工作”，本质上常是资源组织没闭环。诊断时分别记录：①配置读是否能发现 BDF；②BAR 已分配且桥窗口与 Memory Space Enable 是否允许 MMIO；③Bus Master Enable、DMA 映射及设备状态是否允许设备发起 DMA。第二或第三项失败时，第一项仍可能成功；下游总线号超出桥转发范围则可能连配置发现都失败。

## 一句话理解

枚举不是点名，而是把拓扑、资源和能力装配成一张可运行的系统地图。
