---
title: "主机缓冲区：生命周期、DMA 映射与可见性"
---

<div id="主机内存pinned-buffer-与设备可见性" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 主机缓冲区：生命周期、DMA 映射与可见性

上级：[数据路径、DMA 与中断](README.md)

设备获得一个地址之前，软件必须建立三个条件：页面在访问期间有效，地址对该设备可用，双方按照接口规定交接数据。Pin、DMA mapping 和同步分别解决不同问题。

## 三个必须同时成立的条件

| 条件 | 输入与操作 | 输出或保证 |
| --- | --- | --- |
| 生命周期稳定 | 分配合适的内存，必要时固定用户页 | DMA 期间页面仍可用，未被提前回收 |
| DMA 映射有效 | 给定设备、缓冲区、长度和方向，调用映射 API | 设备可用地址或明确失败 |
| 所有权与可见性正确 | 按映射类型同步、排序并发布 | 接收方能按契约访问本次数据 |

映射结果必须检查；地址宽度和 DMA mask 也必须匹配设备能力。Pin 不生成 DMA 地址，不刷新缓存，也不阻止设备越过其获准的缓冲区边界。

## coherent 与 streaming 的不同契约

coherent DMA 内存适合需要共享访问的描述符或队列。其一致性保证不等于字段写入顺序：软件仍要在发布有效位或 Doorbell 前完成规定的排序。

streaming 映射用于按方向交接的缓冲区。非一致平台可能需要缓存维护；可重复使用的映射在 CPU 与设备切换所有权时需要适用的 sync 操作。不能把“CPU 能读到这个地址”当成“此刻允许 CPU 访问设备仍拥有的缓冲区”。

## 一次设备读缓冲区的生命周期

以下示例采用显式 streaming 映射，设备读取 CPU 准备的数据。实际 API 顺序以目标平台为准。

1. CPU 拥有缓冲区，写入完整数据。
2. 新建映射，或对复用映射执行适用的 sync-for-device；检查地址和方向。
3. 按发布规则把描述符交给设备。设备拥有缓冲区期间，CPU 不并发改写它。
4. 设备按接口报告不再访问该缓冲区。软件确认所有权交还，而不只观察一次 Doorbell 写返回。
5. 按需要 sync-for-CPU 或解除映射，再让 CPU 使用；最终确认 DMA 已停止后释放内存。

对于设备写回数据，方向和缓存维护要求随之改变；不能机械复用设备读缓冲区的方向参数。错误、取消和复位路径同样必须解决“是否仍有 DMA 在途”。

<div id="pinned-buffer-常见价值" class="pcie-legacy-anchor"></div>

## Pinned buffer 的价值与边界

需要长期访问用户页时，驱动通常要使用适合 DMA 的固定页接口，并遵守长期固定的限制。内核中已按 DMA 要求分配的内存，不需要套用同一套用户页固定流程。见 [Linux pin_user_pages 说明](https://docs.kernel.org/core-api/pin_user_pages.html)。

支持 SVA、ATS、PRI 的平台可以建立可分页共享地址路径，但需要缺页服务、翻译失效和进程生命周期协同。它不是普通显式 DMA 映射的默认行为。

<div id="这里最容易出什么问题" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 故障怎样对应到三个条件

| 现象 | 可检验假设 |
| --- | --- |
| 少量传输正常，复用后数据损坏 | 缓冲区提前回收、所有权交接或同步缺失 |
| IOMMU 报地址或权限错误 | 错设备的映射、映射长度/方向错误、过期地址 |
| coherent 队列偶发看到半条描述符 | 发布顺序或有效位协议错误，不能仅靠 coherent 属性排除 |

映射 API 依据 [Linux DMA 指南](https://docs.kernel.org/core-api/dma-api-howto.html)，字段发布次序见[排序文章](../02-link-transaction-basics/posted-nonposted-completion-ordering.md)。下一篇读[设备 DMA 路径](device-dma-read-write-flow.md)。
