# 观测、计数器与调试路径

上级：[06 性能建模与调优](./README.md)

相关：[指标、瓶颈与实验设计](./metrics-bottlenecks.md)、[DMA IP 评估清单](../08-industry-ip/dma-ip-checklist.md)

## 这页在回答什么问题

如果系统里的 DMA “偶发慢、偶发抖、偶发错”，需要哪些观测点才能把问题定位到可行动的层次。

## 最值得有的计数器

- descriptor submitted/completed
- outstanding occupancy
- queue full / empty cycles
- read/write bytes
- response latency histogram
- error / retry / timeout count

## 最值得有的状态观测

- 当前通道是否阻塞
- 阻塞在 issue、response、ejection 还是 completion
- 哪个 memory port 或 stream 最拥塞

## 一条实用调试路径

1. 先判定是正确性问题还是性能问题
2. 再判定卡在 submit、issue、network、memory 还是 completion
3. 最后才去细看单个队列、单个 burst 或单个 page 边界

## 为什么 observability 是 IP 能力的一部分

没有足够计数器时，DMA 性能问题很容易退化成猜测。  
这会直接抬高 bring-up 和优化成本。

## 一句话理解

DMA 调试最怕“黑盒搬运器”，最有价值的不是更多日志，而是能把阻塞位置和并发状态直接暴露出来的观测点。
