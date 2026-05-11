# AXI 与 DMA 的系统接口

上级：[04 微架构与系统集成](./README.md)

相关：[AXI Channel、ID 与 Outstanding](../03-on-chip-protocol-families/axi-channel-id-outstanding.md)、[DMA Wiki 首页](../../../DMA/wiki/README.md)

## 这页在回答什么问题

为什么很多 SoC 里 DMA 看起来只是一个 master，但真正接到 AXI 上时会立刻暴露出一整串系统级约束。

## DMA 接 AXI 时通常至少有两类接口

### 控制面接口

常见是：

- CPU 通过 MMIO 配置 DMA 寄存器
- 软件写 queue / doorbell
- 软件读 status / completion

这部分通常强调：

- 正确性
- 低延迟控制
- 明确的软件语义

### 数据面接口

常见是：

- DMA 作为 AXI master 发起读写
- 读 descriptor
- 读源数据
- 写目的数据
- 写回 completion 或状态

这部分更强调：

- outstanding 深度
- burst 组织
- response 吞吐

## 为什么“同一个 DMA”会有多条 AXI 路

一个真实 DMA 往往不是只有一根 AXI 口，而是按职责拆分：

- register slave port
- descriptor read port
- data read/write port
- completion writeback port

拆分的目的是减少内部耦合，让控制流量不被大数据流淹没。

## 看 AXI + DMA 接口时最该追问什么

- descriptor 和 data 是否共用同一条 master 路
- writeback 是否会被大流量写数据拖住
- AXI ID 和 queue / channel 的映射是什么
- non-coherent buffer 的软件契约是否清楚

## 一句话理解

DMA 接 AXI 不是“把 master 口连上去”就结束了，而是把控制面、描述符面、数据面和完成面一起接入一个共享事务系统。
