---
title: "设备 DMA 的读写路径：谁请求，数据往哪里走？"
---

<div id="设备-dma-的读写路径" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 设备 DMA 的读写路径：谁请求，数据往哪里走？

上级：[数据路径、DMA 与中断](README.md)

本文从设备视角命名 DMA read/write：read 是设备读取目标资源，write 是设备向目标资源写数据。以下目标均为已合法映射的主机内存；P2P 见独立文章。

## 一条常见提交路径

采用主机内存描述符队列的教学设备。驱动已经完成资源使能和[缓冲区交接](host-memory-pinned-buffer-visibility.md)，然后用 MMIO Doorbell 通知设备。设备取描述符，执行数据搬运，最后按接口发布完成状态。

这是常见软件接口，不是 PCIe 对所有 DMA 引擎规定的命令格式。有些设备从本地状态启动，或采用不同提交机制。

<div id="dma-write-常见特点" class="pcie-legacy-anchor"></div>

## 设备写主机：Memory Write 携带数据

设备已有待写数据和目的 DMA 地址。DMA 引擎按剩余长度、MPS、地址边界及实现限制生成 Memory Write TLP。链路在满足对应信用和排序条件时发送；主机侧按映射及平台规则接收数据。

> 设备数据 → 带载荷的 Memory Write → Switch / RC → 翻译与主机内存路径

普通 Memory Write 是 posted，没有逐笔事务 Completion。Non-Flit 链路 ACK 也只确认该跳。设备如何判定整个命令完成，必须由设备接口和平台可见性契约说明，不能把“最后一个 TLP 已送入控制器”直接等同于“CPU 已可消费”。

<div id="dma-read-常见特点" class="pcie-legacy-anchor"></div>

## 设备读主机：请求和数据走相反方向

设备掌握源 DMA 地址，但尚无载荷。DMA 引擎分配请求槽与 Tag，发 Memory Read。主机侧服务请求，以一个或多个 CplD 返回数据；设备匹配并收齐后才能正常回收该请求槽。

> 设备 → Memory Read → 主机目标；主机目标 → CplD 数据 → 设备

请求长度受 MRRS 和 4 KiB 边界等限制，返回载荷受适用 MPS、RCB 及 Completer 策略限制。增大 MRRS 并不保证返回包也同样变大。

## 用同一批数据比较两个方向

假设设备要传 4 KiB，起点 4 KiB 对齐，MPS=256 B、MRRS=512 B，且生成器选取最大合法长度。忽略描述符和通知开销：

| 操作 | 请求或数据包 | 返回 |
| --- | --- | --- |
| 设备写主机 | 16 个 256 B Memory Write | 无对应常规 Completion |
| 设备读主机 | 8 个请求，每个请求 512 B | 至少按适用 256 B MPS 拆成 16 个 CplD，也可能更多 |

“8 个读请求”不表示必须同时在途；可用 Tag、完成缓冲和调度决定并发。若起点靠近 4 KiB 边界，还须先拆请求，包数可能变化。

<div id="为什么两者不能混看" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 瓶颈由方向与资源决定

设备读容易受完整返回 RTT、Tag 窗口和 Completion 接收能力限制；设备写也会受数据供给、Posted 信用和主机接收服务限制。两者都可能达不到链路上界，不能把“写不等 Completion”理解成“写没有等待”。

下一步读[队列与通知](queues-doorbells-completions-msix.md)和[读延迟模型](pcie-read-completion-latency.md)。引擎如何把描述符拆成搬运任务由 [DMA 专题](../../../microarchitecture/DMA/wiki/05-system-integration/axi-pcie-view.md)展开；协议参数依据集中在[建模速查](../08-reference/pcie-modeling-params.md)。
