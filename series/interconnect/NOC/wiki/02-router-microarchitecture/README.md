# 02 Router Microarchitecture

这一章只回答一个问题：一个 packet 进入 NoC 之后，到底是怎样在 router 里逐跳前进、等待、占资源、再释放资源的。

你在这里会看到 NoC 的最小工作机制：

- packet / flit / phit 为什么必须分层
- header、body、tail 为什么在 router 里不是同一种对象
- VC、buffer、allocator、credit 如何共同决定 forward progress
- wormhole 为什么省 buffer，却又把 HoL blocking 和 deadlock 风险带上来
- 为什么 router 的面积和功耗经常主要花在 buffer，而不是“计算路由”

## 本章入口

- [Packet Flit Phit Hierarchy](./packet-flit-phit-hierarchy.md)
- [Router Pipeline Stages](./router-pipeline-stages.md)
- [Input Buffer Organization](./input-buffer-organization.md)
- [Virtual Channel Fundamentals](./virtual-channel-fundamentals.md)
- [Allocator Design VC Switch](./allocator-design-vc-switch.md)
- [Credit Based Flow Control](./credit-based-flow-control.md)
- [Wormhole Vs VCT Vs Store Forward](./wormhole-vs-vct-vs-store-forward.md)
- [Router Power Area Tradeoff](./router-power-area-tradeoff.md)

## 一句话总纲

对 AI NoC 来说，router 不是“包转发器”，而是把 `排队、流控、资源依赖、延迟上界和隔离策略` 具体化的地方；很多系统级 stall，最后都能沿着这条链追溯到 router 内部状态。
