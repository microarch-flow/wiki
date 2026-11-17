---
title: "SR-IOV 与地址空间扩展：PF/VF、ATS、PASID、PRI"
---

<div id="sr-iovatspasidpri" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# SR-IOV 与地址空间扩展：PF/VF、ATS、PASID、PRI

上级：[高级主题](README.md)

这些能力解决两组不同问题。SR-IOV 将设备能力呈现为多个 Function；ATS、PASID、PRI 参与地址空间及翻译协同。使用 VF 不要求同时启用后三者，支持其中一项也不保证整条共享地址路径可用。

## SR-IOV：把功能呈现给不同使用者

PF（Physical Function）管理相关设备能力及 VF 的启用。VF（Virtual Function）有自己的 Function 身份和可用资源，可以由对应驱动使用，或在平台支持时分配给虚拟机。

| 输入 | 执行 | 输出与限制 |
| --- | --- | --- |
| PF 能力、资源和软件配置 | PF/系统启用允许数量的 VF | 出现可配置的 VF；不是凭空增加物理带宽 |
| VF 归属和 IOMMU 映射 | 为使用者建立访问与隔离路径 | 请求按身份接受权限检查 |
| 多 VF 同时工作 | 设备调度共享队列、内存及链路资源 | 吞吐隔离依赖实际资源和仲裁策略 |

例如四个 VF 共用一条上行链路。每个 VF 可独立分配，并不意味着每个 VF 都能独占整条链路的峰值带宽。功能隔离、内存访问隔离和性能隔离应分别评估。[Linux SR-IOV 指南](https://docs.kernel.org/PCI/pci-iov-howto.html)说明 PF/VF 的发现和使能方式。

<div id="这些词各自大致在解决什么" class="pcie-legacy-anchor"></div>

## ATS、PASID、PRI：分别补哪一段

| 能力 | 职责 | 不能单独保证 |
| --- | --- | --- |
| ATS | 设备向翻译服务请求翻译，并可缓存有效结果 | 缓存永远有效；映射变化仍需失效 |
| PASID | 请求携带地址空间标识，与请求身份共同选择上下文 | 访问已授权，或设备必然支持可分页内存 |
| PRI | 在支持的路径中请求页面服务并接收处理结果 | 每次缺页都成功，或收到响应后无需重新取得翻译 |

ATS 可缓存的不只是一个裸物理地址，还需要遵守返回权限和有效性规则。PASID 是上下文标识，不是绕过 IOMMU 的授权令牌。

<div id="为什么它们经常成组出现" class="pcie-legacy-anchor"></div>

## 一条受支持的 SVA 路径

教学前提：设备、IOMMU、驱动及进程绑定均支持该 SVA 模式。软件将进程地址空间绑定到设备上下文。设备带相应 PASID 访问，使用 ATS 获取翻译；若页面缺失且支持 PRI，则请求页面服务。

页面服务成功后，设备仍须按规则重新获取有效翻译再访问；失败时进入错误处理。页面映射变化后，平台需要使设备缓存的旧翻译失效；进程退出和设备解绑也要处理在途操作。具体 x86/ENQCMD 组合见 [Linux SVA 文档](https://docs.kernel.org/arch/x86/sva.html)，不能把该组合的全部细节推广到所有架构。

<div id="首版应该抓什么" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 设计时分别列出依赖

先写清要划分 Function，还是让一个设备服务多个进程地址空间。再检查资源、请求身份、翻译、缺页、失效和故障退出。普通显式 DMA 映射可能已经满足需求，不必为了缩写齐全引入可分页共享地址的复杂性。

前置概念见 [IOMMU](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)；路径是否能访问对端资源见 [P2P](p2p-switch-topology-constraints.md)。
