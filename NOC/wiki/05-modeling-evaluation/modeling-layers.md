# 建模层次

上级：[建模与评估](./README.md)

相关：[学习路线图](../01-overview/learning-roadmap.md)

## 不要一开始就追求“工业级精确”

更有效的方法是分层推进。

## Level 0：理想 NoC

假设：

- 无限带宽
- 零拥塞
- 固定通信延迟

价值：

- 给系统模型提供上界
- 先判断 compute / memory 是否本就主导

## Level 1：带宽受限 NoC

加入：

- per-link bandwidth
- per-port bandwidth
- 简化 contention（竞争冲突）

价值：

- 能初步看出链路是否成为瓶颈
- 适合快速扫描参数空间

## Level 2：Topology-aware NoC

加入：

- 具体拓扑
- 具体端点位置
- hop（跳数）相关延迟

价值：

- 能比较 flat mesh（扁平网格）和 hierarchical NoC（层次化片上网络）
- 能看到 memory placement（存储放置位置）对热点的影响

## Level 3：Flit-level NoC

加入：

- packet（数据包）/ flit（流控单元）
- wormhole（虫孔转发）
- credit（信用计数）
- input buffer（输入缓冲）
- arbitration（仲裁）
- destination ejection（目的端弹出）

价值：

- 能区分不同 stall 类型
- 能看到 backpressure（反压）如何放大成系统吞吐下降

## 第一版最值得做到哪里

如果你的目标是架构探索而不是 RTL（寄存器传输级）对齐，建议尽快做到：

- 拓扑感知
- flit-level（流控单元级别）
- credit-based flow control（基于信用的流量控制）
- 简化 VC（虚通道）/ message class 分离
- workload trace injection（工作负载轨迹注入）

这已经足够支撑大量 first-order insight。

## 先别急着引入的东西

- 极复杂 adaptive routing（自适应路由）
- 高精度物理链路建模
- 完整 cache coherence（缓存一致性）
- 过多 micro-optimization

## 本页结论

好的 NoC（片上网络）建模路线，不是从最复杂开始，而是从”能回答架构问题的最小模型”开始，然后按瓶颈逐层加真实度。
