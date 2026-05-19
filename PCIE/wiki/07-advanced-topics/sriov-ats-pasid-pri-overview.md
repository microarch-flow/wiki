# SR-IOV、ATS、PASID、PRI

上级：[07 高级主题](./README.md)

相关：[IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 这页在回答什么问题

为什么现代虚拟化和高性能设备经常会把 SR-IOV、ATS、PASID、PRI 放在一起讨论。

## 这些词各自大致在解决什么

- `SR-IOV`：把一个物理设备切分出多个可分配功能
- `ATS`：让设备参与地址翻译相关协同
- `PASID`：帮助区分不同地址空间上下文
- `PRI`：让设备在缺页或地址依赖场景下和主机进一步协作

## 为什么它们总成组出现

因为它们共同服务于：

- 多租户
- 虚拟机直通
- 更细粒度的设备地址空间管理

## 首版应该抓什么

先抓“它们在扩展 host-device 契约”，不急着吃透全部协议细节。

## 一句话理解

这组能力的核心价值，是把设备从“粗粒度 DMA 主体”推进成“能参与多地址空间和虚拟化协同的系统节点”。
