# 02 路由器与逐跳流控

> <span id="02-router-microarchitecture"></span>本页保留原章节导读。[查看现行分类与阅读顺序](../SUMMARY.md)。

本章从网络传输单位出发，讨论一个分包路由器怎样接收、排队、分配资源并向下一跳发送。文章以输入缓冲、wormhole 和逐跳 credit 作为主要教学例子；其他实现可以选择不同的交换和流控方式。

## 本章入口

- [Packet、Flit 与 Phit](./packet-flit-phit-hierarchy.md)
- [转发与交换方式](./wormhole-vs-vct-vs-store-forward.md)
- [路由器流水线](./router-pipeline-stages.md)
- [输入缓冲组织](./input-buffer-organization.md)
- [虚通道基础](./virtual-channel-fundamentals.md)
- [Credit 与反压](./credit-based-flow-control.md)
- [VC 与交换分配](./allocator-design-vc-switch.md)
- [路由器面积与功耗](./router-power-area-tradeoff.md)

## 一句话总纲

路由器需要协调队列、路径、缓冲授权和共享输出；这些资源何时取得、释放和重新可用，决定了 flit 能否继续前进。具体时序和成本由实现及流量决定。
