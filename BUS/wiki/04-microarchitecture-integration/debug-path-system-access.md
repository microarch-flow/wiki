# Debug Path 与 System Access

上级：[04 微架构与系统集成](./README.md)

相关：[Boot Path 与地址映射初始化](./boot-path-address-map-initialization.md)、[争用、QoS 与可观测性](../05-performance-debug/contention-qos-observability.md)

## 这页在回答什么问题

debug master 为什么经常被当成“特殊访问者”，以及它是怎样接入 bus fabric 的。

## Debug path 常见要做什么

- 读写寄存器
- 访问内存
- halt / resume CPU
- 在系统异常时取证

这意味着 debug path 常常需要绕过一部分正常软件路径，直接进入系统互连。

## 为什么它是特殊路径

因为它经常需要在这些时候仍然可用：

- CPU 卡死
- 软件没有初始化完整
- 外设异常
- boot 尚未完全结束

所以 debug access 的可达性、优先级和隔离策略都需要单独设计。

## 最常见的集成问题

- debug master 能访问的地址范围不清楚
- debug 和正常 CPU/DMA 访问发生冲突
- 某些低功耗或复位状态下 debug path 被意外切断

## 一句话理解

debug path 是 SoC 的“旁路观察与救援通道”，它必须接入 BUS，但又不能简单等同于普通 master。
