# 指标、瓶颈与实验设计

上级：[06 性能建模与调优](./README.md)

相关：[调度、Outstanding 与回包组织](../03-dma-microarchitecture/scheduling-outstanding.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)

## 这页在回答什么问题

看 DMA 性能时，哪些指标值得盯，哪些实验最能快速暴露真正瓶颈。

## 不要只盯平均带宽

至少要同时看：

- effective bandwidth
- completion latency
- tail latency
- outstanding occupancy
- queue depth
- memory port utilization
- overlap 成功率

## 最常见的瓶颈位置

- software submit 太慢
- descriptor / queue 太浅
- DMA issue 不够激进
- NoC 拥塞
- destination ejection 慢
- DDR / HBM latency 或 bank 冲突

## 三组最值得先做的实验

### 1. 大小扫描

观察小包、大块、边界跨越时的效率变化。

### 2. Outstanding 扫描

观察 latency hiding 和热点放大的拐点。

### 3. 并发流扫描

观察单流、双流、多流下的公平性与 completion 尾延迟。

## 一句话理解

DMA 的性能分析要同时关注吞吐、尾延迟和并发占用，否则很容易把“局部高效”误判成“系统高效”。
