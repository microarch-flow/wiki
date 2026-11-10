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

在传统 Non-Flit 模式，DLLP 用于相邻端口间的链路控制，常见作用包括：

- ack / nak
- flow control 信息交换
- 维持相邻链路可靠传输

它不直接等价于上层的业务请求。

## Completion 是什么

completion 是对某些请求的返回，常见于：

- memory read 返回数据
- config read 返回寄存器内容
- 配置写等 non-posted 请求返回无数据的状态

例如 EP 经 Switch 向主机发一个带 Tag 的 Memory Read。EP 向 Switch 发请求 TLP 后，Switch 向 EP 回 ACK；Switch 向 RC 转发该 TLP 后，RC 向 Switch 回 ACK。每个 ACK 只确认对应一跳，且 ACK 可以累计确认多个 TLP。主机随后可能把数据拆成多个 CplD TLP。EP 按请求身份和 Tag 匹配并检查返回，成功请求要等全部所需数据收齐后才正常释放 Tag；错误终止另按错误处理。两跳 ACK 与 credit 更新都不是端到端事务完成。

设备执行软件命令后还可能把 **CQE** 写到主机内存。CQE 是软件队列中的命令状态，和上述 PCIe Completion 是不同对象；CQE 写入本身通常是 posted Memory Write，不要求对应的事务 Completion。Non-Flit 链路控制和重放可参见 [PCIe 2.1 基础规范](https://www.intel.com/content/dam/support/us/en/programmable/support-resources/fpga-wiki/asset03/pci-express-base-r2.1.pdf)。

## 为什么它很关键

因为 write 和 read 的系统体验很不一样：

- 普通 posted Memory Write 不要求事务级 Completion
- read 则必须等待 completion 回来

这会直接影响：

- DMA read 和 DMA write 的性能差异
- 延迟链条长度
- tag / outstanding 深度的需求

## 一句话理解

TLP 承载事务，DLLP 维持链路可靠性，completion 则决定很多读取路径为什么天然更敏感。
