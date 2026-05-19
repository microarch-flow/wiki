# TLP、DLLP 与 Completion 语义

上级：[02 链路、分层与事务基础](./README.md)

相关：[Posted / Non-Posted / Completion 与 Ordering](./posted-nonposted-completion-ordering.md)、[设备 DMA 的读写路径](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)

## 这页在回答什么问题

PCIE 里最常见的几个词到底分别是什么，以及 completion 为什么是很多性能和调试问题的中心。

## TLP 是什么

TLP 是事务层包，承载：

- memory read / write
- config read / write
- message
- completion

可以把它理解成“系统级请求在链路上的可传输载体”。

## DLLP 是什么

DLLP 更偏链路级控制，常见作用包括：

- ack / nak
- flow control 信息交换
- 维持相邻链路可靠传输

它不直接等价于上层的业务请求。

## Completion 是什么

completion 是对某些请求的返回，常见于：

- memory read 返回数据
- config read 返回寄存器内容
- 某些 non-posted 请求需要响应

这里的 `completion` 是 PCIe 协议事务返回，不要和软件里的 `completion queue entry` 混成同一个词。

## 为什么它很关键

因为 write 和 read 的系统体验很不一样：

- posted write 发出去后通常不要求同路径返回数据
- read 则必须等待 completion 回来

这会直接影响：

- DMA read 和 DMA write 的性能差异
- 延迟链条长度
- tag / outstanding 深度的需求

## 一句话理解

TLP 承载事务，DLLP 维持链路可靠性，completion 则决定很多读取路径为什么天然更敏感。
