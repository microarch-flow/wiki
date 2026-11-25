# 03 配置、枚举与地址映射

上级：[系统 I/O 互连（PCIe）](../README.md)

从主机第一次读加速卡上的寄存器开始。先看主机怎样发现这张卡、给它的 64 KiB 窗口分配地址，再沿途检查桥怎样把请求送往设备。换成设备主动访问主机内存时，还要分别弄清 CPU 使用的地址和 DMA 使用的地址由谁映射。

## 推荐阅读顺序

1. [第一次寄存器读与 BAR](./config-space-bar-capability.md)
2. [桥的总线号与地址窗口](./enumeration-bus-number-resource-allocation.md)
3. [配置、BAR 与 DMA 地址](./mmio-config-dma-address-view.md)
4. [IOMMU 翻译与隔离](./iommu-address-translation-device-isolation.md)
