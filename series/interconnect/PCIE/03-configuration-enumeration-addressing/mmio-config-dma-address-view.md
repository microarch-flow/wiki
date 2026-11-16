# MMIO、配置访问、DMA 地址空间视角

上级：[03 配置、枚举与地址映射](./README.md)

相关：[IOMMU、地址翻译与设备隔离](./iommu-address-translation-device-isolation.md)、[设备 DMA 的读写路径](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)

## 这页在回答什么问题

为什么同样在说“地址”，配置空间、BAR/MMIO 和 DMA 地址却不是一回事。

## 三种常见地址视角

- `config space`：主机管理设备的配置入口
- `MMIO / BAR`：主机 CPU 视角访问设备寄存器或窗口
- `DMA address`：设备发起读写时所使用的主机内存地址视角

## 最容易混淆的地方

- BAR 地址是主机访问设备，不是设备访问主机
- DMA 地址是设备看主机内存，不一定等于 CPU 虚拟地址
- 配置访问是管理面，不是高频数据通路

## 一个典型交互

1. 软件通过 config space 识别设备和能力
2. 主机为 BAR 分配地址
3. 驱动通过 MMIO 配置 queue / doorbell / control register
4. 设备用 DMA 地址访问主机内存中的 descriptor 和 data buffer

## 一句话理解

config 在“认和配”，MMIO 在“控设备”，DMA 地址在“让设备碰主机内存”，三者方向和语义都不同。
