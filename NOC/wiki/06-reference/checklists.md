# 检查清单

上级：[06 术语与检查清单](./README.md)

## 开始做第一版 NoC 模型前

- 是否已经明确目标 workload 是什么
- 是否已经明确 tile、SRAM、DMA、HBM 的端点位置
- 是否已经决定拓扑与基础 routing
- 是否已经明确 packet / flit 粒度
- 是否已经决定是否做 request / response / control 分离

## 第一版 flit-level simulator 最低能力

- packet 被拆成 flit
- link 逐周期传输
- wormhole 资源占用
- credit-based flow control
- input buffer 深度限制
- destination ejection / FIFO
- 至少一种 arbitration
- workload 或 synthetic traffic 注入

## 统计项检查

- 是否统计了 per-link utilization
- 是否统计了 credit stall 和 switch stall
- 是否统计了 packet latency 分布而不只是平均值
- 是否统计了 source injection stall
- 是否统计了 destination ejection stall
- 是否统计了 tile utilization 或 workload completion time

## 结果解读前自检

- 这个瓶颈来自 NoC 还是端点
- 是 routing 问题还是 memory placement 问题
- 是 bulk traffic 淹没小消息，还是 buffer 太浅
- 是平均性能问题还是尾部热点问题
- 结论是否只在某一种 traffic pattern 下成立

## 当前阶段不必过早深挖

- 高复杂度 adaptive routing
- 过度精细的物理链路模型
- 完整 CPU coherence 协议
- 脱离 workload 的参数堆砌
