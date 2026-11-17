---
title: "系统 I/O 互连：从发现设备到完成一次 DMA"
---

<div id="pcie-wiki" class="pcie-legacy-anchor"></div>

# 系统 I/O 互连：从发现设备到完成一次 DMA

PCI Express（PCIe）把主机与设备连接成可枚举、可寻址的事务网络。读懂它，需要分别追踪设备发现、地址配置、数据传输和完成通知：设备能被发现，并不代表 BAR 已可用；链路收到了包，也不代表软件命令已完成。

<div id="dashboard" class="pcie-legacy-anchor"></div>

## 先看一条完整路径

以主机内存队列型设备为例，软件先发现 Function 并配置资源，再建立 DMA 映射、准备描述符，通过 Doorbell 通知设备。设备发起 Memory Read 或 Memory Write 搬数据，按设备接口发布完成记录，软件通过轮询或中断处理结果。队列格式属于设备接口，PCIe 负责承载相关事务。

| 阶段 | 必须回答的问题 | 阅读入口 |
| --- | --- | --- |
| 连接 | 请求经过哪些端口，哪里共享带宽？ | [拓扑与角色](02-link-transaction-basics/topology-root-complex-switch-endpoint.md) |
| 发现与配置 | Function、BAR 和桥窗口怎样建立？ | [配置、枚举与地址](03-configuration-enumeration-addressing/README.md) |
| 运行 | 缓冲区何时可用，读写如何返回？ | [DMA、队列与通知](04-data-path-dma-interrupts/README.md) |
| 分析 | 等待来自信用、Tag、内存还是软件？ | [性能与调试](05-performance-debug/README.md) |

<div id="快速开始" class="pcie-legacy-anchor"></div>
<div id="路线-1第一次系统学-pcie" class="pcie-legacy-anchor"></div>
<div id="路线-2想把-host-device-数据路径学透" class="pcie-legacy-anchor"></div>
<div id="路线-3想做性能分析bring-up-或故障定位" class="pcie-legacy-anchor"></div>
<div id="工作台" class="pcie-legacy-anchor"></div>
<div id="学习" class="pcie-legacy-anchor"></div>
<div id="分析" class="pcie-legacy-anchor"></div>
<div id="查阅" class="pcie-legacy-anchor"></div>

## 选择阅读路径

- 第一次学习：按[学习路线图](01-overview/learning-roadmap.md)建立前置概念。
- 已有工程问题：用[按目标学习 PCIe](01-overview/goal-oriented-navigation.md)直接找负责的文章。
- 查看全部文章：打开[知识地图](SUMMARY.md)。
- 随时查数与排错：使用[查阅、建模与检查清单](08-reference/README.md)。

<div id="这套-wiki-的边界" class="pcie-legacy-anchor"></div>
<div id="维护原则" class="pcie-legacy-anchor"></div>

## 本专题的边界

主线是拓扑、事务、配置、DMA、中断和系统性能。基础链路机制以传统 Non-Flit 模式为起点；涉及 Flit Mode 时单独说明，不能只看 Gen 编号选择模型。例子中的地址、延迟和容量均按所在文章的假设解释。

片内事务见 [BUS](../BUS/README.md)，路由与拥塞见 [NoC](../NOC/README.md)，DMA 引擎组织见 [DMA](../../microarchitecture/05-dma/README.md)，电气与均衡见 [SerDes](../SERDES/README.md)，CXL 内存访问见[一致性与内存互连](../COHERENCE/README.md)。本专题保留这些接口交界处的必要条件。
