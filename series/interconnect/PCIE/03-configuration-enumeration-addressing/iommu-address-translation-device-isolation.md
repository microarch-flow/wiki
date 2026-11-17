---
title: "IOMMU：设备地址如何翻译并受到隔离？"
---

<div id="iommu地址翻译与设备隔离" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# IOMMU：设备地址如何翻译并受到隔离？

上级：[配置、枚举与地址映射](README.md)

IOMMU 根据设备请求身份选择翻译与权限上下文，把允许的设备地址映射到目标物理资源。它解决“哪个设备可以访问哪些页面”，并不自动建立正确的描述符、缓存同步或缓冲区生命周期。

<div id="iommu-在解决什么问题" class="pcie-legacy-anchor"></div>

## 从请求身份选择映射

以启用翻译的普通 DMA 为例，请求携带 Requester ID，平台据此选择相应域或上下文；支持 PASID 的路径还可以进一步区分地址空间。输入是身份、设备地址、访问类型及当前映射，结果是允许访问的物理目标，或翻译/权限错误。

教学例：设备 A 属于域 A，设备 B 属于域 B。两者都访问 IOVA `0x1000`，域 A 可映射到物理页 P，域 B 可映射到物理页 Q。同一个数值不会自动表示共享缓冲区；共享必须由软件显式建立并维护权限。

## IOTLB 命中、缺失与 fault

| 条件 | 处理 | 性能或正确性结果 |
| --- | --- | --- |
| 有有效缓存翻译且权限允许 | 使用 IOTLB 缓存结果 | 避免重复页表访问 |
| 无缓存翻译，但页表映射有效 | 按实现执行页表遍历并填充缓存 | 增加服务与排队开销 |
| 映射缺失或权限不允许 | 产生 fault，按平台策略终止或进入受支持的恢复流程 | 不能当作普通慢访问继续成功 |
| 旁路或直通模式 | 使用对应平台路径 | 不具有同样的逐页翻译隔离效果 |

miss 不是 fault；页表遍历也不一定需要访问所有级别的外部内存，缓存与实现会改变代价。延迟必须按目标平台测量。

<div id="为什么这对-pcie-尤其关键" class="pcie-legacy-anchor"></div>
<div id="没有-iommu-会怎样" class="pcie-legacy-anchor"></div>

## 隔离依赖完整路径

启用 IOMMU 是重要条件，但不能只看一个启动开关。还要检查域绑定、映射权限、请求身份处理、ACS 与设备组，以及路径是否会绕过预期检查。对端直转的 P2P 流量尤其需要单独评估。

没有适当隔离时，错误 DMA 可能破坏其他内存；但 IOMMU 也不会阻止设备写坏其已获授权的缓冲区。数据格式验证和软件所有权仍然必要。

<div id="工程上最重要的判断" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 映射变化需要失效与生命周期管理

软件撤销映射前须确认设备不再使用它，并按平台 API 完成所需失效。若设备通过 ATS 缓存了翻译，还必须遵守设备侧失效协议。仅修改页表而继续使用旧缓存结果，会破坏权限与资源回收假设。

驱动应从 DMA API 获得并管理 DMA 地址；不要自行猜测 IOVA 与物理页关系。[Linux DMA 指南](https://docs.kernel.org/core-api/dma-api-howto.html)说明普通映射；[SVA 文档](https://docs.kernel.org/arch/x86/sva.html)说明一种带 PASID、ATS 与 PRI 的平台组合。缓冲区交接见[生命周期与可见性](../04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md)。
