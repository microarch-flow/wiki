---
title: "一次 PCIe 读取：TLP、链路确认与 Completion"
---

<div id="tlpdllp-与-completion-语义" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 一次 PCIe 读取：TLP、链路确认与 Completion

上级：[链路、分层与事务基础](README.md)

一次 Memory Read 至少包含请求与事务返回。链路确认是另一层事件，设备向软件报告的命令完成又是第三层。区分三者，才能正确计算延迟和回收资源。

<div id="tlp-是什么" class="pcie-legacy-anchor"></div>

## TLP 承载什么

TLP（Transaction Layer Packet）携带内存、配置、I/O、消息或 Completion 等事务信息。Memory Read 请求包含目标地址和请求长度，但不携带要读取的数据；Memory Write 携带写入数据；成功读返回由带数据的 Completion（CplD）承载。

常规 Non-Flit TLP 的字段随包类型、地址宽度及可选能力变化。不能把所有 TLP 都建成固定头长加 MPS：MPS 是载荷上限，无数据请求根本没有该载荷。

<div id="completion-是什么" class="pcie-legacy-anchor"></div>

## 沿两跳追踪一个 Tag

教学前提：传统 Non-Flit 模式、EP 经 Switch 读主机内存，请求合法且最终成功。请求长度 256 B，目标允许拆成两笔 128 B CplD；此例只描述事件关系，不规定 ACK 与返回之间的固定时延。

| 事件 | 参与者保留或更新的状态 |
| --- | --- |
| EP 分配 Tag 并发出 Memory Read | Requester 保留地址、长度和待完成状态 |
| Switch 接收并转发 | 各链路独立维护确认、信用和重放状态 |
| EP 收到第一跳 ACK | 可按链路规则回收已确认的重放条目；读 Tag 仍占用 |
| EP 收到第一笔 128 B CplD | 按 Requester ID、Tag 及返回字段匹配，记录尚缺数据 |
| EP 收到最后一笔合法 CplD | 全部所需数据收齐，成功请求槽可正常回收 |

不同请求的 Completion 可以交错返回，因此不能只用“最近发出的请求”匹配。对于一笔被拆分的读取，还要检查 Byte Count、Lower Address、长度和状态等适用字段；仅 Tag 相同不足以证明返回完整且合法。[AMD Completion 接口说明](https://docs.amd.com/r/en-US/pg213-pcie4-ultrascale-plus/Requester-Completion-Descriptor-Format)展示了这些信息在具体 IP 中的表达。

<div id="dllp-是什么" class="pcie-legacy-anchor"></div>

## DLLP 确认的是哪一段

Non-Flit 的 ACK/NAK DLLP 作用于相邻端口；ACK 可以累计确认多个 TLP。Switch 下游链路的 ACK 不替代上游链路的 ACK，也不代替事务 Completion。信用更新同样只说明相应接收容量。

发送端重放缓冲、接收端 TLP 缓冲与 Requester 的在途请求表是不同资源，释放条件见[信用流控与链路重放](credit-flow-control-and-replay.md)。

<div id="为什么它很关键" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## Completion 不总是数据，也不是 CQE

成功配置写等 Non-Posted 请求返回无数据 Cpl；UR、CA 等错误也可通过 Completion 状态返回。错误终止与超时须按协议和设备恢复规则处理，不能把不完整数据当成成功结果。

CQE（Completion Queue Entry）是设备接口定义的软件完成项。设备通常用 posted Memory Write 写 CQE，该写没有对应的常规事务 Completion。一个软件命令可能包含很多 PCIe 读写；这些事务都完成，也不自动证明设备计算或存储操作已经结束。

下一篇读[信用与重放](credit-flow-control-and-replay.md)，再读[请求类型与排序](posted-nonposted-completion-ordering.md)。
