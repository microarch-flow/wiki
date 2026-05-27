# CIM 阵列间的互连与 Reduction：与 NoC 的关系

上级：[05 Architecture And System](./README.md)
相关：[NoC: Reduction Networks](../../../NoC/wiki/06-ai-noc-specifics/reduction-and-collective-networks.md), [NoC: Memory-Centric NoC](../../../NoC/wiki/06-ai-noc-specifics/memory-centric-noc.md), [Peripheral Overhead](../04-circuit-and-macro/peripheral-overhead.md)

## 这页在回答什么问题

CIM 已经在 array 内做了局部计算，为什么还需要关心 NoC 和 reduction？因为大矩阵、batch、multi-head attention 和多 tile 并行都会产生跨 macro 的 activation broadcast、partial sum merge 和 result movement。

## Traffic 类型

```text
activation broadcast
weight load / refresh
partial sum reduction
output writeback
calibration / control traffic
fallback traffic
```

activation broadcast 类似 AI NoC 中的 multicast；partial sum reduction 类似 collective network。区别是 CIM macro 数量多、单个 macro 输出粒度小，traffic 更贴近 memory array，容易在 tile 内形成密集局部通信。

## 三条 Paradigm 的互连压力

Analog CIM 的互连压力集中在 ADC 后 partial sum。array 内输出是 analog，数字化后才进入 reduction；如果 ADC 精度低，tile 级合并还要携带 scale、校正和误差预算。

Digital CIM 的互连压力来自 bit-serial 周期和 accumulator 输出。它可在 local logic 中做更多确定性归约，但 partial sum 宽度和 cycle count 会增加 buffer 与 NoC 占用。

Mixed-signal CIM 的互连压力取决于 analog/digital 边界。边界越靠近 macro，NoC 看到的是更干净的数字 partial sum；边界越分散，NoC 还要承受更多校正、scale 和分块累加状态。

## 拓扑选择

小规模 tile 可用局部 bus、tree 或 crossbar；大规模 chip 需要 NoC、hierarchical reduction 或 multicast tree。NoC wiki 的 [broadcast multicast tree](../../../NoC/wiki/06-ai-noc-specifics/broadcast-multicast-tree.md) 和 [tile architecture](../../../NoC/wiki/06-ai-noc-specifics/tile-architecture-and-noc.md) 可作为背景。

选择拓扑时要看 traffic 方向。如果 activation 是一对多，broadcast tree 有价值；如果 partial sum 是多对一，reduction tree 更合适；如果 workload 频繁 fallback 或多层流水，general NoC 的灵活性更重要。

macro 间 reduction 关注短距离 fan-in 和 accumulator 位宽；tile 内 reduction 关注 local buffer、tree depth 和 backpressure；tile 间 reduction 关注 NoC hop count、contention 和同步；chip 全局 reduction 则会碰到 global buffer、clock/power domain 和 host-visible completion。把这些层级合成一个平均带宽参数，会掩盖 CIM 最常见的系统瓶颈。

## PIM/NMC 对照

DRAM/HBM/GDDR-PIM 的 reduction 更靠近 bank/channel 和 memory command，瓶颈常在 result return、bank conflict 和 host coordination。HBM base die 或 interposer 上的 NMC 则依赖 die-to-die/package bandwidth。它们和 CIM macro 的 tile-level reduction 同源但不等价。

## 一句话理解

CIM 减少了 array 内搬运，却不会消除 macro 间通信；activation broadcast 和 partial sum reduction 是系统级收益能否保留的关键。

## 建模启示

互连建模不能只给平均带宽。需要记录 topology、link bandwidth、hop count、fanout/fanin、reduction tree depth、partial-sum width、reduction location、contention、backpressure、latency 和 energy per byte。早期模型可以折叠 router pipeline、VC 数量等微结构，但不能折叠 broadcast/reduction 模式和数据位宽，否则会误判 CIM 的有效利用率。
