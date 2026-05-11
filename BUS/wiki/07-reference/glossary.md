# 术语表

上级：[07 术语与检查清单](./README.md)

## BUS

面向多个 master / slave 的共享事务互连。

## Master / Initiator

发起读写请求的一侧，例如 CPU、DMA。

本 wiki 默认正文优先使用 `master`，在更抽象或跨协议语境里会补充 `initiator` 作为同义词。

## Slave / Target

接收请求并提供数据或状态的一侧，例如 SRAM、DDR controller、peripheral block。

本 wiki 默认正文优先使用 `slave`，在更抽象或更中性的语境里会补充 `target` 作为同义词。

## Transaction

一次完整访问行为，通常包含地址、控制、数据和响应。

## Outstanding

已经发出但尚未完成的事务数量。

## Ordering

请求和响应是否必须按某种顺序出现的规则。

## Arbitration

多个请求竞争共享资源时的选择规则。

## Backpressure

下游无法继续接收流量时，向上游传播的节流机制。

## Bridge

在不同协议、位宽或时钟域之间做转换的互连模块。

## Crossbar

允许多个输入和多个输出并发匹配的一类互连组织方式。

## MMIO

通过内存映射地址空间访问设备寄存器的方式；语义上不同于普通可缓存内存。

## Doorbell

软件或上游模块用于通知 device / DMA“有新任务可取”的控制面写操作或寄存器机制。

## Completion

把“硬件任务已完成”传回软件或上游模块的记录、状态或事件机制。

## Response Path / Return Path

请求完成后，数据或状态从 target 返回到 initiator 的路径；很多系统里它比 request path 更早成为瓶颈。

## Timeout

事务最终可能会返回，但已经明显超过系统预期时限的现象。

## Fault

事务被明确判定为错误，例如 decode error、slave error、translation fault 或 permission fault。

## Hang

事务既没有成功完成，也没有明确报错，而是长时间失去 forward progress 的状态。
