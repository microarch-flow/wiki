# GEMM Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[流量模式](./traffic-patterns.md)、[Collective Communication](./collective-communication.md)

## 读这页前先统一几个词

- `GEMM`：矩阵乘矩阵，是很多 AI 芯片最常见的核心算子
- `weight-stationary`：尽量让权重留在本地，激活值在网络里流动
- `output-stationary`：尽量让输出部分和留在本地累加
- `forwarding`：结果不先回全局存储，而是直接转给下游 tile
- `partial sum`：还没归并完成的中间累加结果

## 为什么先看 GEMM

GEMM（通用矩阵乘法）是最适合作为 NoC 第一批 workload（工作负载）case study 的对象，因为它：

- 结构规则
- 映射方式相对清楚
- 容易暴露 broadcast（广播）、forwarding（前传）、reduce（归约）等典型通信

## 典型数据流问题

你至少要先明确：

- 权重是否常驻本地
- activation（激活值）是广播还是分片送达
- partial sum（部分和）是否本地归约还是跨 tile（计算单元）归约
- 输出是否直接 forward 到下一阶段

## 常见通信形态

- one-to-many：权重或 activation 分发
- point-to-point：tile pipeline forwarding
- many-to-one：partial sum gather（收集）

## 对 NoC 最敏感的架构选择

- weight-stationary（权重驻留）vs output-stationary（输出驻留）
- tile placement（放置策略）
- cluster 内共享 SRAM 的大小
- 是否采用 tile-to-tile forwarding

## 常见热点位置

- 靠近 source 的 broadcast path
- partial sum 汇聚点
- cluster 间边界链路
- HBM（高带宽存储器）/ DMA（直接内存访问）注入端

## 建模时至少要扫的参数

- packet size（数据包大小）
- flit size（流控单元大小）
- local SRAM（本地静态存储）大小
- cluster 大小
- forwarding 开关
- multicast（组播）是否存在

## 你最可能看到的 stall

- `SWITCH_CONFLICT`：多个 tile 同时抢共享输出
- `NO_CREDIT`：destination FIFO 或聚合路径堵住
- `EJECTION_BLOCKED`：本地累加或写回接口来不及消费

## 一个高价值对比实验

比较：

- 回写 SRAM / HBM 再读出
- 直接 tile-to-tile forwarding

观察：

- link utilization（链路利用率）
- latency（延迟）
- producer stall（生产者停顿）
- 总工作完成时间

## 本页结论

GEMM 的价值不只是“容易建模”，而是它能帮助你把 broadcast、forwarding、reduce 这三类 AI NoC 基本流量一次串起来。
