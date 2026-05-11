# 分层总线与协议分工

上级：[03 片上总线协议族](./README.md)

相关：[AXI / AHB / APB 对照](./axi-ahb-apb-comparison.md)、[互连组件与数据路径分解](../04-microarchitecture-integration/interconnect-components.md)

## 这页在回答什么问题

为什么现代 SoC 常见的不是“一条总线”，而是多层 bus fabric 加若干 bridge。

## 单层共享总线的问题

当系统增大时，单层 BUS 会同时遇到：

- master 数量增加
- slave 数量增加
- 地址 decode 变深
- 争用更严重
- 时序更难收敛

## 分层总线的常见拆法

### 高性能主干层

连接：

- CPU cluster
- DMA
- memory controller
- accelerator

常见选择是 AXI 或类似高性能 fabric。

### 外设层

连接：

- UART
- SPI
- I2C
- timer
- GPIO

常见选择是 APB 一类简单协议。

### 中间桥接层

负责：

- AXI 到 APB 转换
- clock domain crossing
- width adaptation
- buffering 和节流

## 分层的收益

- 把高带宽路径和低速控制路径隔离
- 降低大面积共享仲裁压力
- 让不同复杂度 IP 用最合适的协议接入

## 一句话理解

分层总线的本质不是“多画几层框图”，而是把 `高带宽数据路径` 和 `低复杂度控制路径` 分开管理。
