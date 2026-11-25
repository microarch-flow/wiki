---
title: "系统 I/O 互连：从发现设备到完成一次 DMA"
---

<div id="pcie-wiki" class="pcie-legacy-anchor"></div>

# 系统 I/O 互连：从发现设备到完成一次 DMA

主机通过 PCI Express（PCIe）读取加速卡上的数据。请求到达卡边以后，还得经过桥和片内路径才能取到目标值。从[《一次跨桥读取：设备已经收到请求，主机为什么还在等？》](06-workloads-case-studies/pcie-vs-axi-noc-boundary.md)读起，沿请求和返回各走一次。

跨桥读从窗口已经配置好时开始。如果从刚上电的卡看起，主机怎样在还没有窗口地址时发现它，又怎样决定把哪一段地址交给它？接着读[《主机第一次读卡上的寄存器，地址是怎么来的？》](03-configuration-enumeration-addressing/config-space-bar-capability.md)。

<div id="dashboard" class="pcie-legacy-anchor"></div>

## 先看一条完整路径

以主机内存队列型设备为例，软件先发现 Function 并配置资源，再建立 DMA 映射、准备描述符，通过 Doorbell 通知设备。设备发起 Memory Read 或 Memory Write 搬数据，按设备接口发布完成记录，软件通过轮询或中断处理结果。队列格式属于设备接口，PCIe 负责承载相关事务。

| 阶段 | 必须回答的问题 | 阅读入口 |
| --- | --- | --- |
| 连接 | 请求经过哪些端口，哪里共享带宽？ | [拓扑与角色](02-link-transaction-basics/topology-root-complex-switch-endpoint.md) |
| 发现与配置 | 主机见到一张卡后，怎样把第一次读送到卡上？ | [第一次寄存器读与 BAR](03-configuration-enumeration-addressing/config-space-bar-capability.md) · [章节目录](03-configuration-enumeration-addressing/README.md) |
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

- 想顺序学到设备怎样发起 DMA、软件何时可以复用缓冲区，可沿[学习路线图](01-overview/learning-roadmap.md)继续。
- 已有工程问题：用[按目标学习 PCIe](01-overview/goal-oriented-navigation.md)直接找负责的文章。
- 查看全部文章：打开[知识地图](SUMMARY.md)。
- 随时查数与排错：使用[查阅、建模与检查清单](08-reference/README.md)。

<div id="这套-wiki-的边界" class="pcie-legacy-anchor"></div>
<div id="维护原则" class="pcie-legacy-anchor"></div>

## 本专题的边界

主线是拓扑、事务、配置、DMA、中断和系统性能。基础链路机制以传统 Non-Flit 模式为起点；涉及 Flit Mode 时单独说明，不能只看 Gen 编号选择模型。例子中的地址、延迟和容量均按所在文章的假设解释。

片内事务见 [BUS](../BUS/README.md)，路由与拥塞见 [NoC](../NOC/README.md)，DMA 引擎组织见 [DMA](../../microarchitecture/05-dma/README.md)，电气与均衡见 [SerDes](../SERDES/README.md)，CXL 内存访问见[一致性与内存互连](../COHERENCE/README.md)。本专题保留这些接口交界处的必要条件。
