# 02 Router 微架构

本章解决的问题是：

1. 一个 packet（数据包）是怎样在 NoC 里逐跳推进的
2. credit（信用计数）和 backpressure（反压，下游阻塞向上游传播的停发效应）为什么会影响系统吞吐
3. VC（Virtual Channel，虚通道）、allocator（分配器）、deadlock（死锁）为什么不是可选细节

## 本章入口

- [Packet / Flit / Wormhole](./packet-flit-wormhole.md)
- [Credit / Backpressure](./credit-backpressure.md)
- [VC / Deadlock](./virtual-channel-deadlock.md)
- [Router Pipeline 与 Allocator](./router-pipeline-allocator.md)
- [Buffer Depth / Credit Sizing / Allocator Policy](./buffer-depth-credit-sizing-allocator-policy.md)

## 一句话总纲

对 AI NoC 来说，router（路由器）不是简单”转发器”，而是把 `流控、排队、资源占用、协议隔离` 具体化的地方。很多系统级 stall（停顿），根源最后都能追到 router 和 NI（Network Interface，网络接口）的资源竞争。
