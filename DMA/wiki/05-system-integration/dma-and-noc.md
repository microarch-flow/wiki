# DMA 与 NoC

上级：[05 系统集成](./README.md)

相关：[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)、[NOC：NI / DMA / 存储接口](../../NOC/wiki/04-ai-dataflow-system/ni-dma-memory-interface.md)

## 这页在回答什么问题

为什么在片上大系统和 AI accelerator 里，DMA 往往直接决定 NoC 上看到的 traffic 形状。

## DMA 是 NoC 的主动流量源

DMA 决定：

- request 注入节奏
- packet / burst 粒度
- response 回流密度
- 与 control / stream / collectives 的混跑关系

所以它不是 NoC 的边缘模块，而是 NoC 行为的重要塑造者。

## 只看链路不看 DMA 会得出什么错结论

- 误以为拓扑是主瓶颈
- 忽略端点 ejection / memory port 压力
- 忽略 request 与 response 的相互堵塞

## 在 AI 系统里最该关注的几类冲突

- bulk DMA 压住关键 response
- refill 和 writeback 互相放大波峰
- DMA 向 local SRAM 注入过快，导致 bank/port 冲突

这些冲突很多也会被软件或 runtime 的调度旋钮重新塑形，例如 queue 深度、tile size、batching、descriptor packing、polling/interrupt 策略。

## 一句话理解

在很多系统里，NoC 看到的不是“应用流量”，而是被 DMA 调度器重新塑形后的应用流量。
