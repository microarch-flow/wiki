# Digital CIM 深入：Bit-Serial、Bit-Parallel、Popcount、典型 Macro

上级：[03 Compute Paradigms](./README.md)
相关：[Digital CIM 基础](./digital-cim-fundamentals.md), [SRAM-CIM 深入](../02-memory-technologies/sram-cim-deep-dive.md), [Macro Primitives](../04-circuit-and-macro/cim-macro-primitives.md)

## 这页在回答什么问题

Digital CIM 的精度和吞吐如何形成？同样标称 INT8，bit-serial、bit-parallel 和 popcount 路线的面积、周期数、数据流和系统瓶颈完全不同。

## Bit-Serial

Bit-serial 把多比特输入或权重拆成 bit plane，多周期在 array path 中执行，再由外围或局部 accumulator 按位权累加。它的好处是 cell 和 read path 简单，支持可变精度；代价是 latency 和 energy 随位宽增加。

以 INT8 × INT8 为例，如果权重和激活都按 bit-serial 展开，周期数和 partial sum 管理会迅速上升。实际设计会利用 weight stationary、bit-plane reuse、稀疏性或低比特量化降低开销。

## Bit-Parallel

Bit-parallel 用更多 cell、更多列、更多 read path 或更宽 local logic 同时处理多个 bit。它吞吐更高，但面积、布线、local accumulator 和时序压力更大。对 SRAM-CIM 来说，bit-parallel 的问题不是数学上能不能做，而是 array density 和 routing 是否仍然优于传统 MAC array。

## Popcount 路径

Binary/ternary network 和 XNOR-popcount 是 digital CIM 的经典形态。XNOR 可以在 cell/read path 或局部逻辑中完成，popcount 负责把 bitwise match 数量转成 partial sum。这个路线适合低比特模型，但对现代 INT8/FP8/FP16 workload 的覆盖有限。

如果 popcount 完全在远离 array 的外围做，CIM 属性会变弱；如果 sense path、bitline grouping 或 local reduction tree 与 array 紧密耦合，才更符合 digital CIM。

## 典型 Macro 数据路径

```text
activation bit plane
  -> WL/read driver
  -> SRAM array bitwise operation
  -> SA / local logic
  -> popcount or partial sum accumulator
  -> bit-weighted accumulation
  -> output buffer
```

这个路径里的每一级都可能成为瓶颈。WL driver 和 read disturb 限制同时激活行数；local accumulator 决定 partial sum 精度；output buffer 决定 macro 与 tile 的耦合方式。

## Memory Technology 边界

Digital CIM 深入讨论以 SRAM 为主，因为 SRAM read path、sense amp、local logic 和 CMOS peripheral 能以可验证方式合在一起。MRAM 只有在 read/sense path 参与 bitwise compute、comparison 或 local reduction 时才成立；如果只是 MRAM array 存权重，旁边放数字 MAC，就越过了 CIM 边界。

ReRAM/Flash 的 digital CIM 不自然，因为它们的优势来自 multi-level cell state 和 analog current summation。把它们改成 digital bit plane 会增加读取次数、sense 判决和外围编码，且 write endurance、write-verify、retention drift 仍然存在。PCM 也类似：可以数字化使用，但 resistance drift 和写入代价让它难以成为 digital CIM 主线。

DRAM/HBM/GDDR 的 digital processing 更应归入 PIM。它的 compute unit 是 memory die/bank 上的独立逻辑，服务于高带宽、大容量和 command/dataflow 扩展；这和 SRAM digital CIM 把 bitwise/popcount 推进 array path 是两类问题。

## 与 Analog 的真正差异

Digital CIM 的精度由离散位宽和数字累加定义，因此可扩展性更好；analog CIM 的精度受 ADC、noise 和 device variation 约束。Digital CIM 的能效优势较温和，但更容易给出 worst-case 行为和 silicon signoff 路径。对于车载、工业和可量产 SoC，这种确定性本身是价值。

## 一句话理解

Digital CIM 的设计空间是用周期、面积和局部逻辑换取确定性；bit-serial 省面积但慢，bit-parallel 快但重，popcount 适合低比特但覆盖面有限。

## 研究启示

Digital CIM 的开放问题集中在公平 baseline 与可扩展精度：必须和 SRAM buffer + MAC、small systolic array、NPU local memory 做同口径比较。研究若只报告低比特 peak TOPS/W，而不报告 INT8 扩展、buffer、routing、utilization 和模型覆盖范围，很难说明产品价值。
