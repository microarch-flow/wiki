# Packet Flit Phit Hierarchy

上级：[02 Router Microarchitecture](./README.md)
相关：[Router Pipeline Stages](./router-pipeline-stages.md), [Wormhole Vs VCT Vs Store Forward](./wormhole-vs-vct-vs-store-forward.md)

## 这页在回答什么问题

为什么 NoC 不能只用“包”一个概念描述通信，而必须把一次传输拆成 packet、flit、phit 三层。

这三个名字不是教材礼仪，而是三种不同约束的边界：packet 承载事务语义，flit 承载流控和仲裁，phit 承载物理线宽和真实传输时间。你如果把三层混成一层，后面关于 wormhole、credit、链路宽度和 buffer 深度的判断会全部走样。

## Packet 是通信语义单位

packet 回答的是“这一笔通信到底在做什么”。它通常包含源、目的、消息类型、顺序信息和有效载荷。对 AI NoC，一个 packet 可能代表：

- 一块 activation 数据
- 一次 DMA read request
- 一次 DMA read response
- 一段 partial sum
- 一条 barrier 或 descriptor 消息

这说明 packet 先是系统对象，再是网络对象。packet 的大小首先受软件、编译器和系统接口约束，而不是受 router 喜好约束。

为什么不能直接用 packet 做所有建模？因为 packet 太粗。router 不会等整包都到齐再决定仲裁，credit 也不会按“整包剩余空间”计数。真正决定网络行为的是更细的传输粒度。

## Flit 是流控与仲裁单位

flit 是 flow control unit。它回答的是：“router buffer 一次装什么、allocator 一次放行什么、credit 一次计什么。”

一个 packet 会被切成若干 flit。最常见的划分是：

```text
packet
  ├── header flit
  ├── body flit 0
  ├── body flit 1
  └── tail flit
```

header 承载路由相关信息；body 主要承载 payload；tail 标记 packet 结束并触发资源释放。这个分工非常重要，因为 wormhole router 里的很多状态变化都围绕“header 建路、body 跟随、tail 释放”展开。

为什么 flit 必须独立于 packet？因为 wormhole 的价值恰恰来自“整包不必存满再走”。如果 router 只能按 packet 工作，你就会退回 store-and-forward 或至少 VCT 的世界，buffer 成本和延迟模型都会变。

常见误解：flit 只是 packet 的固定切片。  
实际上：flit 是 router 级行为单位；切多大，不只是格式问题，而是直接影响 buffer 粒度、credit round-trip 和 allocator 压力。

## Phit 是物理传输单位

phit 是 physical transfer unit。它回答的是：“这条链路一个 cycle 实际能搬走多少位。”

如果 flit 宽度和链路宽度相同，那么 `phit = flit`，一个 flit 一拍过链路。如果 flit 比链路宽，则一个 flit 要分多个 phit 才能传完。

例子：

```text
flit_width = 256b
link_width = 128b

一个 flit 需要 2 个 phit：
cycle 0: phit0[127:0]
cycle 1: phit1[255:128]
```

这就是为什么“链路宽度”不是漂亮参数，而是直接决定 hop latency 和 buffer 占用时间的硬约束。很多概念图默认一个 flit 一拍传完，这在实际芯片里未必成立，尤其当全局长线宽度受布线和功耗限制时。

## 为什么必须分三层，而不是两层

如果只分 packet 和 phit，会丢掉 router 行为层。你无法表达：

- header 与 body 走不同 pipeline 阶段
- credit 按 buffer slot 计数，而不是按 packet 计数
- allocator 每周期争的是“谁的队首 flit 过”，不是“哪个 packet 整体过”

如果只分 packet 和 flit，会低估物理实现问题。你会错误地假设 flit 总能一拍通过链路，从而忽略：

- 长线需要更窄链路以保频率
- phit 数量增加会拉长 link traversal 时间
- 同样的 flit 宽度在不同区域未必都能承受

所以三层不是“更完整的定义”，而是分别对应语义层、微架构层和物理层。

## 一个具体例子：64B packet 在 128b 链路上怎么走

假设：

- packet size = 64B = 512b
- flit width = 128b
- link width = 128b

那么：

```text
1 packet = 4 flit
1 flit  = 1 phit

cycle 0: header flit 过链路
cycle 1: body0 flit 过链路
cycle 2: body1 flit 过链路
cycle 3: tail flit 过链路
```

如果链路宽度降到 64b：

```text
1 packet = 4 flit
1 flit  = 2 phit

cycle 0-1: header flit
cycle 2-3: body0 flit
cycle 4-5: body1 flit
cycle 6-7: tail flit
```

同一个 packet，语义没变，flit 数没变，但 hop 传输时间翻倍。这正是 phit 层存在的意义。

## 和 BUS 世界的一个关键差别

BUS 里你更常直接面对 beat。beat 同时承担协议交付和物理传输两个角色，因为一条 channel 的语义和一拍的数据交付关系很近。NoC 里这两个角色被拉开了：flit 更像“router 能理解的一拍对象”，phit 更像“物理线真正搬的一拍对象”。

相同点是都在处理分段传输；差异在于 NoC 明确引入了一个中间层，把网络流控和物理带宽解耦。这个解耦是后面讨论 wormhole 和 link width 取舍的基础。

## 常见误解

常见误解：packet 越大越高效，所以应该尽量做大。  
实际上：packet 大确实能摊薄 header 开销，但也会拉长 wormhole 路径占用时间，放大 HoL blocking 和尾延迟。

常见误解：phit 只是实现细节，前期建模可以永远忽略。  
实际上：如果 flit 宽度和链路宽度不匹配，忽略 phit 会系统性低估 hop latency 和链路占用时间。

## 一句话理解

packet 决定你在传什么，flit 决定 router 怎样管它，phit 决定物理链路几拍才能把它搬过去。

## 建模启示

cycle-level 模型至少要显式保留：

```text
Packet {
  id
  src
  dst
  traffic_class
  num_flits
}

Flit {
  packet_id
  flit_id
  kind  // HEADER, BODY, TAIL
  num_phits
}
```

如果只关心 topology 对平均带宽的影响，`Packet -> bytes` 的近似还勉强可用；但一旦你关心 wormhole、credit 或 allocator，flit 就不能再折叠掉。因为 `credit_count`、`vc_buffer_occupancy` 和 `switch_allocation` 都是按 flit 发生的。

如果链路宽度固定且与你选择的 flit width 一致，可以先把 `num_phits=1` 折叠掉；如果要比较不同 link width、长链路窄化、或不同区域不同链路规格，必须保留 `num_phits` 或直接保留 `link_transfer_cycles`，否则你会把物理约束误当成 topology 差异。
