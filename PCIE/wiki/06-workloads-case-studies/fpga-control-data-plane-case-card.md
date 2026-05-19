# FPGA / 采集卡控制面与数据面案例卡

上级：[06 工作负载与案例](./README.md)

相关：[MMIO、配置访问、DMA 地址空间视角](../03-configuration-enumeration-addressing/mmio-config-dma-address-view.md)、[设备 DMA 的读写路径](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)

## 这页在回答什么问题

为什么 FPGA 板卡、采集卡这类设备，最容易把 `控制面 MMIO` 和 `数据面 DMA` 的边界暴露得非常清楚。

## 典型系统位置

- 设备作为 PCIe endpoint 接入主机
- BAR 暴露控制寄存器、doorbell、状态窗口
- 大块数据通过 DMA 在 host buffer 和 device local buffer 之间搬运

## 最关键的两条路径

- 控制面：host 通过 MMIO 配置寄存器、描述符基址、启动位、状态查询
- 数据面：device 通过 DMA read/write 搬大块数据

## 为什么它特别适合拿来学

因为它很少把两条路径藏起来：

- 写寄存器成功，不等于 DMA 已通
- BAR 能访问，不等于数据面吞吐正常
- 中断能来，不等于 completion record 已经稳定可见

## 最常见问题

- BAR / MMIO 好用，但 DMA 地址映射错了
- 控制面顺序正确，但数据面 queue 深度不够
- 设备端缓冲和主机端 buffer 生命周期错位

## 最值得抄走的判断

很多板卡 bring-up 的第一性原则是：先把 `control plane` 和 `data plane` 分开验证，再看两者如何闭环。

## 一句话理解

FPGA / 采集卡案例最能提醒你：PCIe 系统不是“能读写寄存器就算通”，而是控制面和数据面都要各自闭环。
