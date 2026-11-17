---
title: "PCIe 术语表"
---

<div id="术语表" class="pcie-legacy-anchor"></div>

# PCIe 术语表

上级：[查阅、建模与检查清单](README.md)

本页给出查阅定义。完整单位、数值和模式条件集中在[建模速查](pcie-modeling-params.md)，避免多个页面维护不同参数表。

## 常见术语

| 术语 | 本专题含义 |
| --- | --- |
| Root Complex / Root Port | 主机与 PCIe 层次的连接体系 / 其中向下连接链路的端口 |
| Switch / Endpoint | 转发事务的交换组件 / 承载设备功能的端点 |
| Function / BDF | 可配置的 PCI 功能 / Bus、Device、Function 标识，完整定位还需 segment/domain |
| Requester / Completer | 一笔请求的发起者 / 为请求提供对应完成响应的组件 |
| TLP | 事务层包，包含请求、消息和 Completion 等类型 |
| DLLP | 传统 Non-Flit 模式中相邻端口的链路控制包 |
| Completion / CplD | Non-Posted 请求的事务返回 / 带数据的 Completion |
| CQE | 设备接口定义的软件完成项，不等于 PCIe Completion |
| Posted / Non-Posted | 不产生对应常规事务 Completion 的请求 / 需要 Completion 的请求 |
| BAR / MMIO | 设备地址资源的配置寄存器及其描述窗口 / 通过内存地址机制访问 I/O 资源 |
| DMA 地址 / IOVA | 设备使用的映射地址 / I/O 虚拟地址，需结合翻译模式理解 |
| IOMMU / IOTLB | 设备地址翻译与隔离组件 / 其翻译缓存 |
| MPS / MRRS / RCB | 数据 TLP 载荷上限 / 读请求长度上限 / 适用 Completion 拆分边界 |
| Tag | 跟踪待完成请求的标识，容量与能力、使能和实现有关 |
| Credit | 接收端承诺的分类缓冲容量；不是事务完成确认 |
| Replay | 对链路传输执行的重放，不是重新提交软件命令 |
| MSI-X | 通过配置的写消息通知 CPU 的中断机制 |
| AER | 扩展错误记录与报告；不是重放计数器 |
| SR-IOV / PF / VF | 单根 I/O 虚拟化 / 管理相关能力的物理功能 / 可分配的虚拟功能 |
| ATS / PASID / PRI | 地址翻译服务 / 地址空间标识 / 页面请求接口 |
| P2P | 设备直接访问对端可用资源，要求拓扑、映射与策略支持 |
| GT/s / GBd | PCIe 标注的原始传输速率 / 物理符号率；PAM4 下不能直接等同 |
| lane / xN | 一条全双工通道含发送与接收差分对 / N 条 lane |
| Flit | 指定模式下组织传输与保护的固定大小单元，不等于一个 TLP |

## 最常见误区

设备是 Endpoint，不妨碍它成为 DMA Requester；同一 DMA 地址数值不保证不同域访问同一物理页；有信用不保证有可用 Tag；轮询可以消费 CQE，但不会自动解决内存同步。

术语如何连成过程，见[一页总览](pcie-one-page.md)。
