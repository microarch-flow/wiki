# GEMM Case Study

上级：[AI Dataflow 系统视角](./README.md)

相关：[流量模式](./traffic-patterns.md)、[Collective Communication](./collective-communication.md)

## 为什么先看 GEMM

GEMM 是最适合作为 NoC 第一批 workload case study 的对象，因为它：

- 结构规则
- 映射方式相对清楚
- 容易暴露 broadcast、forwarding、reduce 等典型通信

## 典型数据流问题

你至少要先明确：

- 权重是否常驻本地
- activation 是广播还是分片送达
- partial sum 是否本地归约还是跨 tile 归约
- 输出是否直接 forward 到下一阶段

## 常见通信形态

- one-to-many：权重或 activation 分发
- point-to-point：tile pipeline forwarding
- many-to-one：partial sum gather

## 对 NoC 最敏感的架构选择

- weight-stationary vs output-stationary
- tile placement
- cluster 内共享 SRAM 的大小
- 是否采用 tile-to-tile forwarding

## 常见热点位置

- 靠近 source 的 broadcast path
- partial sum 汇聚点
- cluster 间边界链路
- HBM / DMA 注入端

## 建模时至少要扫的参数

- packet size
- flit size
- local SRAM 大小
- cluster 大小
- forwarding 开关
- multicast 是否存在

## 你最可能看到的 stall

- `SWITCH_CONFLICT`：多个 tile 同时抢共享输出
- `NO_CREDIT`：destination FIFO 或聚合路径堵住
- `EJECTION_BLOCKED`：本地累加或写回接口来不及消费

## 一个高价值对比实验

比较：

- 回写 SRAM / HBM 再读出
- 直接 tile-to-tile forwarding

观察：

- link utilization
- latency
- producer stall
- 总工作完成时间

## 本页结论

GEMM 的价值不只是“容易建模”，而是它能帮助你把 broadcast、forwarding、reduce 这三类 AI NoC 基本流量一次串起来。
