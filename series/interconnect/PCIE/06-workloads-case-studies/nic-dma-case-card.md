---
title: "NIC 数据路径：RX、TX 分别占用哪个 PCIe 方向？"
---

<div id="nic-dma-案例卡" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>
<div id="典型系统位置" class="pcie-legacy-anchor"></div>

# NIC 数据路径：RX、TX 分别占用哪个 PCIe 方向？

上级：[工作负载与案例](README.md)

本例采用主机内存中的 RX/TX 描述符与完成状态，NIC 作为 Endpoint。重点是把网络方向转换成 PCIe 事务方向；ring 调度和 DMA 引擎组织由 [DMA 专题 NIC 案例](../../../microarchitecture/DMA/wiki/07-workloads-case-studies/pcie-nic-dma-case-card.md)负责。

<div id="最关键的三条主线" class="pcie-legacy-anchor"></div>

## RX：网络载荷写入主机

主机先发布可用接收缓冲区。NIC 从描述符取得合法 DMA 地址，收到网络包后发 Memory Write，把载荷写入主机，再按接口发布完成状态。描述符本身可能需要 NIC 发 Memory Read 取得，因此 RX 并不是完全没有 PCIe 读取。

当接收描述符耗尽，设备可能丢包或暂停，具体行为及计数由 NIC 定义。此时即使链路还有带宽，也不能写入未授权的任意缓冲区。

## TX：网络载荷从主机读取

主机发布待发送缓冲区，NIC 发 Memory Read，接收 CplD，再交给网络发送路径。其 PCIe 大块载荷通常沿主机→NIC 方向，与 RX 载荷相反。

TX 完成状态的定义依设备接口。例如“设备不再读取主机缓冲区”允许软件回收缓冲区，但不自动证明远端已收到，更不证明上层可靠传输完成。

## 从包率计算基础流量

教学假设：每秒 1,000 万个包，每包主机载荷 64 B；每包另有 16 B 描述符读取和 16 B 完成记录写回，不计批处理差异。这些大小是构造参数，不代表特定网卡。

| 场景 | 主机→NIC 的有效数据 | NIC→主机的有效数据 |
| --- | --- | --- |
| RX | 描述符 0.16 GB/s | 载荷 0.64 + 完成记录 0.16 = 0.80 GB/s |
| TX | 描述符与载荷共 0.80 GB/s | 完成记录 0.16 GB/s |

这不是线上总流量：还缺读请求头、CplD/写包头、Doorbell、通知和链路控制。包率上升时，固定的每包工作会增加；载荷带宽相同也可能产生不同的事务压力。

<div id="最常见瓶颈" class="pcie-legacy-anchor"></div>
<div id="最值得抄走的判断" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 怎样判断真正瓶颈

RX 首先看可用缓冲、Posted 信用与主机消费；TX 还要看读 Tag、完整返回 RTT 和 Completion 缓冲。多个 NIC 共用 Switch 上行口时，按载荷方向分别求和，不能把全双工两向流量与一个单向上界比较。

中断合并和批处理可能减少软件开销，但也改变首个完成的等待时间。若 CQ 已积压而 PCIe 空闲，应先检查软件消费，不应继续提高 MRRS。观测方法见[瓶颈拆解](../05-performance-debug/host-device-bottleneck-breakdown.md)，通知机制见 [Linux MSI 指南](https://docs.kernel.org/PCI/msi-howto.html)。
