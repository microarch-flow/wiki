# 指标与实验设计

上级：[建模与评估](./README.md)

相关：[流量模式](../04-ai-dataflow-system/traffic-patterns.md)

## 为什么必须先定义指标

如果没有统一指标，NoC 调参很容易退化成“看起来忙不忙”的直觉比较。

## NoC 层核心指标

- packet latency
- flit latency
- throughput
- per-link utilization
- per-router occupancy
- credit stall cycles
- switch stall cycles
- saturation point

## Tile / 系统层指标

- tile utilization
- producer stall ratio
- consumer starvation ratio
- DMA overlap 成功率
- barrier / sync 放大延迟
- end-to-end tokens/s 或 workload completion time

## Memory 层指标

- HBM port utilization
- SRAM bank contention
- request / response queue occupancy
- read response return latency

## 至少应该做的实验

### 实验 1：单链路 credit 深度扫描

观察：

- buffer depth 对吞吐的影响
- credit round-trip 导致的 bubble

### 实验 2：destination 停顿触发反压

观察：

- ejection FIFO 满后，阻塞如何传回 source

### 实验 3：拓扑比较

例如：

- flat mesh
- cluster-hierarchical NoC

观察：

- link utilization 分布
- 热点位置
- 平均与尾部延迟

### 实验 4：packet size / flit size 扫描

观察：

- serialization latency
- header overhead
- HOL blocking 倾向

### 实验 5：AI-like workload trace

至少覆盖：

- GEMM-like
- attention prefill
- attention decode
- MoE-like

## 一个重要原则

只看平均值通常不够。  
尤其要关注：

- tail latency
- hotspot link
- stall breakdown
- workload completion time

## 本页结论

NoC 评估最有价值的不是单个峰值数字，而是建立 `链路利用率 -> stall 类型 -> tile 利用率 -> workload 吞吐` 的因果链。
