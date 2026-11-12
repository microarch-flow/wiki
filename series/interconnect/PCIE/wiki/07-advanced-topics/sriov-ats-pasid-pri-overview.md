# SR-IOV、ATS、PASID、PRI

上级：[07 高级主题](./README.md)

相关：[IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 这页在回答什么问题

为什么现代虚拟化和高性能设备经常会把 SR-IOV、ATS、PASID、PRI 放在一起讨论。

## 这些词各自大致在解决什么

- `SR-IOV`：PF 管理和启用多个 VF。每个 VF 可用自己的 Function 身份配置和分配；VF 的存在不要求同时使用 ATS、PASID 或 PRI。
- `ATS`：设备向翻译服务请求地址翻译，并可缓存有效结果；命中设备缓存可减少再次查询。映射变化时必须遵循失效协议，不能继续使用旧翻译。
- `PASID`：请求附带地址空间标识，与设备请求身份一起选择上下文。相同虚拟地址在不同 PASID 下可以指向不同页面。
- `PRI`：在支持的缺页处理路径中，设备可发 page request，请求软件处理缺页；处理结果可能成功、失败或被拒绝。

例如支持 SVA 的系统把进程地址空间绑定到 PASID。设备以该上下文请求地址翻译；若页面缺失且 PRI 可用，设备请求缺页服务并等待响应。成功后按接口重新获取翻译；失败或拒绝时必须报告/处理失败，不能假设数据已可访问。具体组合由设备、IOMMU、驱动和平台共同决定。参见 [Linux SR-IOV 指南](https://docs.kernel.org/PCI/pci-iov-howto.html) 与 [SVA/ATS/PRI 文档](https://docs.kernel.org/arch/x86/sva.html)。

## 为什么它们经常成组出现

因为它们共同服务于：

- 多租户
- 虚拟机直通
- 更细粒度的设备地址空间管理

## 首版应该抓什么

先抓“它们在扩展 host-device 契约”，不急着吃透全部协议细节。

## 一句话理解

这组能力的核心价值，是把设备从“粗粒度 DMA 主体”推进成“能参与多地址空间和虚拟化协同的系统节点”。
