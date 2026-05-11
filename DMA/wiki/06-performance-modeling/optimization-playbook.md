# 优化与调参手册

上级：[06 性能建模与调优](./README.md)

相关：[指标、瓶颈与实验设计](./metrics-bottlenecks.md)、[Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)

## 这页在回答什么问题

当 DMA 表现不佳时，应该优先调哪些旋钮，如何避免盲目试错。

## 先分清是哪一类问题

- 吞吐上不去
- 尾延迟太差
- overlap 不成立
- 多流公平性差
- 偶发错或偶发抖动

再往下一层，还要先分清当前优化对象是哪一类 DMA：

- queue-based / host-managed DMA
- device DMA to host memory
- pipeline-coupled local DMA

因为这三类对象的“completion”、瓶颈位置和软件可调旋钮并不完全相同。

## 常见调优旋钮

- transfer size
- burst size
- outstanding limit
- queue depth
- channel priority
- tile size / buffer size
- interrupt vs polling 策略

## 一个建议顺序

1. 先确认正确性和一致性
2. 再扫描粒度与并发窗口
3. 再看系统冲突点
4. 最后才做复杂 QoS 和高级调度

## 一句话理解

DMA 调优不是把所有旋钮都往大拧，而是找到让 `带宽利用、尾延迟和系统稳定性` 同时过关的平衡点。
