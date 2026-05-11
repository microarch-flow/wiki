# 指标与实验设计

上级：[建模与评估](./README.md)

相关：[流量模式](../04-ai-dataflow-system/traffic-patterns.md)

## 为什么必须先定义指标

如果没有统一指标，NoC（片上网络）调参很容易退化成”看起来忙不忙”的直觉比较。

## NoC 层核心指标

- packet latency（数据包延迟）
- flit latency（流控单元延迟）
- throughput（吞吐量）
- per-link utilization（每条链路利用率）
- per-router occupancy（每路由器占用率）
- credit stall cycles（信用停顿周期数）
- switch stall cycles（交叉开关停顿周期数）
- saturation point（饱和点）

## Tile / 系统层指标

- tile（计算单元）utilization（利用率）
- producer stall ratio（生产者停顿比率）
- consumer starvation ratio（消费者饥饿比率）
- DMA（直接内存访问）overlap 成功率
- barrier（屏障同步）/ sync 放大延迟
- end-to-end tokens/s 或 workload completion time（工作负载完成时间）

## Memory 层指标

- HBM（高带宽内存）port utilization
- SRAM（静态随机存储）bank contention（存储体冲突）
- request / response queue occupancy（请求/响应队列占用率）
- read response return latency（读响应返回延迟）

## 至少应该做的实验

### 实验 1：单链路 credit 深度扫描

观察：

- buffer depth（缓冲深度）对吞吐的影响
- credit round-trip（信用往返延迟）导致的 bubble（气泡/空闲周期）

### 实验 2：destination 停顿触发反压

观察：

- ejection FIFO（弹出先入先出队列）满后，阻塞如何传回 source

### 实验 3：拓扑比较

例如：

- flat mesh（扁平网格）
- cluster-hierarchical NoC（分簇层次化片上网络）

观察：

- link utilization 分布
- 热点位置
- 平均与尾部延迟

### 实验 4：packet size / flit size 扫描

观察：

- serialization latency（串行化延迟）
- header overhead（包头开销）
- HOL blocking（队头阻塞）倾向

### 实验 5：AI-like workload trace

至少覆盖：

- GEMM-like（通用矩阵乘法类）
- attention prefill（注意力预填充）
- attention decode（注意力解码）
- MoE-like（混合专家模型类）

## 一个重要原则

只看平均值通常不够。  
尤其要关注：

- tail latency（尾部延迟）
- hotspot link（热点链路）
- stall breakdown（停顿分类统计）
- workload completion time

## 本页结论

NoC 评估最有价值的不是单个峰值数字，而是建立 `链路利用率 -> stall（停顿）类型 -> tile 利用率 -> workload 吞吐` 的因果链。
