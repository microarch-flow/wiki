# Non-Coherent vs Coherent DMA

上级：[02 基础对象与传输语义](./README.md)

相关：[缓存一致性、IOMMU 与地址空间](./consistency-cache-coherency.md)、[同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)

## 这页在回答什么问题

为什么 coherent DMA 往往被误解成“更高级、因此一定更简单更快”，以及什么时候 non-coherent 反而更合理。

## Non-Coherent DMA 的特点

- 软件必须显式做 cache 维护
- buffer ownership 边界更清楚
- 硬件复杂度通常更低
- 在嵌入式或专用系统里很常见

## Coherent DMA 的特点

- CPU 和 DMA 共享更一致的数据视图
- 软件易用性更高
- 会引入一致性流量和协议开销
- 不自动解决同步和性能竞争

## 不要把“正确性便利”误当成“性能免费”

coherent DMA 并不保证：

- 更低延迟
- 更高带宽
- 更少拥塞

在高并发系统里，一致性维护本身就可能制造额外流量。

## 一个实用判断

如果系统强调：

- 通用 OS
- 用户态直通设备
- 多核共享 buffer

coherent DMA 通常更值得。  
如果系统强调：

- 简洁可控
- 功耗面积
- 固定数据路径

non-coherent DMA 往往更自然。

## 一句话理解

coherent 和 non-coherent 的核心差别，不在“谁更先进”，而在 `谁承担一致性复杂度，以及系统是否愿意为此付出代价`。
