# 什么样的 Workload 适合 CIM、什么样的不适合

上级：[07 Workloads](./README.md)
相关：[Problem Statement](../01-overview/problem-statement.md), [RAM: Data Movement First Principle](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md), [NoC: Memory-Centric NoC](../../../NoC/wiki/06-ai-noc-specifics/memory-centric-noc.md), [BUS: DMA Path](../../../BUS/wiki/04-microarchitecture-integration/dma-descriptor-fetch-data-move-writeback.md), [FAB: Process Variation](../../../FAB/wiki/02-front-end-fabrication/process-nodes-and-ppa-tradeoffs.md)

## 这页在回答什么问题

判断 workload 是否适合 CIM，应该看哪些特征？核心不是 MAC 数量，而是数据是否值得留在 array 附近、计算是否规整、误差是否可容忍、fallback 是否会吞掉收益。

## 判断维度

| 维度 | 适合 CIM 的信号 | 不适合 CIM 的信号 |
| --- | --- | --- |
| 数据流 | MVM/GEMM/Conv 规整、reuse 高 | 控制流强、稀疏随机访问 |
| 权重 | 固定或低频更新 | 高频更新、在线训练、动态专家频繁切换 |
| 精度 | INT4/INT8 或更低，误差可训练吸收 | FP16/FP8 强精度、outlier 敏感 |
| 映射 | array utilization 高、partial sum 局部合并 | tiling 碎片多、跨 tile reduction 重 |
| 系统 | fallback 少、host sync 少 | unsupported op 多、张量往返频繁 |
| 时延 | batch 可摊销或 latency target 宽松 | 小 batch、强同步、token-by-token |

## 三条 Paradigm 的 Workload 差异

Analog CIM 要求最苛刻：低比特、固定权重、可校准、误差可容忍。ReRAM/Flash analog CIM 适合长期驻留权重的 MVM，而不适合频繁重写或高精度动态模型。

Digital CIM 的 workload 覆盖更宽。SRAM digital/mixed-signal 可以处理更多 INT4/INT8 子图，但必须证明 bit-serial cycle、accumulator、buffer 和 NoC 没有抵消收益。

Mixed-signal CIM 的 workload 需要同时满足 analog 局部收益和数字校正可控。它不怕一定量的误差，但怕误差不可建模、scale 随 workload 强烈变化、runtime metadata 过重。

## CIM/PIM/NMC 的 Workload 分界

CIM 更适合 array-native MVM、Conv、低比特固定推理和局部 reduction。DRAM/HBM/GDDR-PIM 更适合 memory die/bank 侧 offload，例如大容量权重读取、KV cache 和 bandwidth-bound kernel。HBM base die、interposer 或 package-side compute 属于 NMC，更适合把 memory subsystem 附近的带宽转成系统收益。

## 一句话理解

适合 CIM 的 workload 不是“算得多”，而是“数据复用高、映射规整、误差可控、fallback 少”。

## 建模启示

架构探索应把 workload 拆成 phase 与子图：每个子图记录 operator type、tensor shape、batch、reuse、precision sensitivity、memory footprint、data movement、NoC traffic、system utilization、mapping efficiency、unsupported-op ratio、fallback target、synchronization frequency、latency target 和 energy target。cell 波形、RTL FSM 和具体 training recipe 可折叠成 latency/energy/precision/utilization 参数；phase-level traffic、residency、partial-sum merge point 和 fallback 不能折叠。
