---
title: "PCIe 一页总览：从配置到软件完成"
---

<div id="pcie-一页版总览" class="pcie-legacy-anchor"></div>

# PCIe 一页总览：从配置到软件完成

上级：[查阅、建模与检查清单](README.md)

本页用于回顾。需要机制、推导或证据时，从表中进入正文。

<div id="一页抓住-pcie" class="pcie-legacy-anchor"></div>

## 一页抓住系统路径

| 要确认的事 | 关键对象 | 正文 |
| --- | --- | --- |
| 谁连接谁 | RC、Root Port、Switch、EP、Function | [拓扑](../02-link-transaction-basics/topology-root-complex-switch-endpoint.md) |
| 谁可以发送 | 类别信用、缓冲、链路及排序状态 | [信用与重放](../02-link-transaction-basics/credit-flow-control-and-replay.md) |
| 请求何时结束 | Requester ID、Tag、完整 Completion | [一次读取](../02-link-transaction-basics/tlp-dllp-completion-basics.md) |
| 地址如何可用 | BDF、BAR、桥窗口、DMA 映射 | [配置与地址](../03-configuration-enumeration-addressing/README.md) |
| 软件何时能消费 | 所有权、同步、CQE、通知 | [运行路径](../04-data-path-dma-interrupts/README.md) |
| 为什么慢或失败 | 服务量、在途状态、错误证据 | [性能与调试](../05-performance-debug/README.md) |

## 最常见主线

发现 Function → 分配资源并准备驱动 → 建立 DMA 映射 → 发布工作 → 设备访问 → 发布结果 → 软件消费与回收。实际设备可以使用不同队列和通知接口，但每个阶段的必要条件仍须明确。

<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 最容易混淆的三组词

**链路 ACK、PCIe Completion、CQE**：ACK 确认一跳；Completion 返回 Non-Posted 请求的结果；CQE 保存设备命令状态。写 CQE 常用 posted Memory Write，不要求对应的事务 Completion。

**BAR 地址、DMA 地址**：BAR 描述目标资源窗口；DMA 地址供设备发起访问。P2P 的 DMA 目标也可以是对端 BAR 资源。两者数值及转换不能预先假定。

**链路上界、有效吞吐**：上界由指定链路、方向及模式决定；有效吞吐按实际交付字节计。协议开销、请求窗口、服务能力和软件供给都会影响结果。

开始计算前查[建模参数](pcie-modeling-params.md)；开始定位前查[调试清单](pcie-debug-checklist.md)。
