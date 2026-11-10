# Chiplet And Die To Die Interconnect

上级：[06 AI NOC Specifics](./README.md)

相关：[Topology Physical Realization](../03-topology/topology-physical-realization.md)、[RAM: hbm 2.5d 3d tsv](../../../RAM/wiki/08-packaging-integration/hbm-2.5d-3d-tsv.md)

## 这页在回答什么问题

这页回答：当 AI 芯片从单 die 扩展到 chiplet 或 HBM 邻接系统后，NoC 问题为什么会变成层次化互连问题。

## 跨 die 不再是“多几 hop”

die-to-die 互连和片上 hop 的差别，不只是更长，而是一个不同层级的通路：

- 可能需要不同的串行化、时钟和封装接口
- gateway 队列、重组与可选的可靠性机制增加状态
- 延迟、带宽密度和能耗取决于技术、距离与实现；不能对所有跨 die 和片上路径作绝对排序

例如 die A 的 NI 发读请求 packet：本地 NoC 将其送至 gateway；gateway 入队、跨时钟、按 D2D 链路格式分包并串行发送。若链路协议实现 replay，则保存待确认数据、在错误时按该协议重发。die B gateway 接收并重组，再通过本地 NoC 到 memory；返回数据沿反向路径切包、传输、重组并交付请求者。若 A gateway 的待发送队列满，本地 NoC 会经有限缓冲和 credit 逐跳回压。不同 D2D 协议可无 replay 或使用其他粒度，需按实际接口建模。

## 为什么 AI 系统很容易碰到它

AI 芯片越来越常见：

- compute die + HBM
- 多 compute chiplet
- 分层 package fabric

原因很现实：

- reticle 限制
- HBM 封装形态
- 工艺和成本分拆

这意味着很多“片上通信问题”会自然升级为：

- die 内通信
- die 间通信
- HBM 邻接通信

三层并存。

## 编译器和 placement 必须感知层次

如果系统有明显的跨 die 代价，那么 placement 就不能只看 tile 坐标，还要看：

- 哪些流量必须留在 die 内
- 哪些 collective 可以先局部聚合再跨 die
- 哪些 memory access 要尽量打向本地或邻近 port

否则跨 die 代价会迅速吞掉原本在单 die 上成立的优化。

## 为什么 deterministic NPU 更要谨慎

对 deterministic 系统而言，若目标实现的跨 die 服务时间或波动更大，问题还包括：

- 时序等级突然断层
- static schedule 更容易失配
- buffering / double-buffering 需求更强

也就是说，chiplet 会把“路径长度差异”放大成“调度层次差异”。

## 工程上的直接结论

一旦进入 chiplet 设计，NoC 不应再被看成单一平面，而应看成分层 fabric：

- local intra-cluster
- on-die NoC
- die-to-die bridge
- HBM / package edge interface

这对 DSL 和仿真都意味着必须引入分层距离模型。

## 一句话理解

chiplet 让 NoC 从“片上路由问题”变成“层次化互连问题”；跨 die 不只是更远，而是另一种级别的通信。

## 建模启示

模型至少要区分：

- same-cluster
- same-die
- cross-die
- memory-edge

并分别赋予不同的：

- latency
- bandwidth
- buffer / bridge cost

如果模型把 cross-die 只当成多几个 hop，会系统性低估 chiplet 设计里的调度和 placement 难度。
