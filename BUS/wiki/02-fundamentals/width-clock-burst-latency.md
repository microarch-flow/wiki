# 位宽、时钟、Burst 与延迟

上级：[02 基础对象与事务语义](./README.md)

相关：[Bridge、CDC 与 Width Adapter](../04-microarchitecture-integration/bridge-cdc-width-adaptation.md)、[带宽、延迟、利用率与拥塞](../05-performance-debug/bandwidth-latency-utilization.md)

## 这页在回答什么问题

为什么很多 BUS 设计看起来只是改了位宽、频率或 burst 参数，却会显著改变延迟和吞吐。

## 理论带宽来自两个最直接参数

- bus width
- clock frequency

近似可以写成：

`theoretical bandwidth = width per beat x beats per second`

但真实可用带宽还要扣除：

- 地址和响应开销
- 空拍
- 仲裁等待
- bridge / CDC 气泡

## Burst 为什么重要

burst 可以摊薄每次事务的固定开销，但也会带来：

- 单次占路时间更长
- 对小请求更不友好
- 对高优先级控制流量干扰更强

所以 burst 越长不一定越好。

## 位宽也不是越宽越好

更宽的总线意味着：

- 布线压力更高
- 时序更难收敛
- 窄传输 waste 更多
- 宽窄适配更常见

## 时钟域切换会增加隐藏延迟

当 BUS 穿过不同时钟域时，常见代价是：

- 弹性 FIFO
- 握手等待
- 峰值吞吐下降
- 突发流量被打散

## 一句话理解

BUS 的位宽、频率和 burst 决定理论上能跑多快，但真正决定体验的是这些参数在共享、桥接和回压条件下还能剩下多少有效吞吐。
