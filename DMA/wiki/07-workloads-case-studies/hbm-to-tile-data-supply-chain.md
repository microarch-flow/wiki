# HBM 到 Tile 的数据供给链

上级：[07 工作负载与案例](./README.md)

相关：[AI 加速器里的 DMA](./ai-accelerator-dma.md)、[DMA 与 Local Memory / DDR / HBM](../05-system-integration/dma-and-memory-system.md)、[DMA 与 NoC](../05-system-integration/dma-and-noc.md)

## 这页在回答什么问题

如果把 AI 芯片里一次典型的数据供给过程完整展开，DMA 到底处在什么位置；以及为什么这条链能否稳定运行，通常不取决于某个单点峰值，而取决于 DMA 是否把整条链路的节拍组织对了。

## 一条典型供给链长什么样

一条常见链路通常是：

1. runtime / mapper 决定下一批 tile
2. DMA 从 HBM 拉取 tensor block
3. NoC 把数据送到 cluster SRAM
4. local DMA 或 load 单元把数据推进 tile buffer
5. compute 消费
6. 结果沿 writeback 路径回流

单看每一步都不神秘，难点在于它们必须形成长期稳定的流水，而不是一轮偶然跑通。

## 为什么这条链常常是“哪里都像瓶颈”

HBM latency、NoC return path、SRAM bank、tile buffer ready、writeback 回压，每一项都可能把系统拖慢，所以这条链看起来很容易让人觉得“哪里都坏了”。但更准确的说法是：DMA 正在把这些资源串成一条供给链，只要其中某一段节拍错配，整个系统就会表现成 compute 利用率下降、tail latency 上升或局部断供。

因此这页真正想建立的判断是：不要孤立地看 HBM 问题、NoC 问题、SRAM 问题或 mapping 问题，而要看 DMA 是否在正确时间发出了足够但不过量的流量。

## 这条链最容易出问题的地方

最常见的问题通常落在：

- HBM latency 被低估，outstanding 不足以隐藏它
- NoC bulk transfer 压住关键 response
- cluster SRAM 写入与 tile 读取在端口或 bank 上打架
- writeback 与 refill 竞争同一条回流路径
- buffer flip / consumer-ready 时机晚于数据名义完成

这些问题的共同点是：它们都不是单个模块内部 bug，而是跨阶段节拍没有对齐。

## 一个系统判断框架

分析这条链时，最有用的三问是：

1. 数据在哪一级等，是 HBM、NoC、SRAM 还是 tile buffer。
2. 谁在等谁，是 DMA 等 memory、compute 等 DMA，还是 writeback 反过来堵住 refill。
3. 当前 DMA 流量是发得不够，还是发得太猛，把后端自己打爆了。

这三问的价值在于它们能把“供给链不稳”迅速压缩到某个交互边界上，而不是停留在“系统慢了”。

## 常见误解

常见误解：`HBM 带宽大就说明供数链应该没问题`。实际上 latency hiding、NoC return path 和 SRAM 端口冲突都可能先坏掉。

常见误解：`compute 利用率低就是 mapping 不好`。实际上 DMA 节拍和供数链状态经常是更直接的原因。

常见误解：`writeback 只是尾部问题`。实际上 writeback 很容易通过共享资源反向拖慢下一轮 refill。

## 一句话理解

在 AI 芯片里，HBM 到 tile 的供给链能否稳定运行，往往不取决于单点峰值，而取决于 DMA 是否把整条链路的节拍组织对了。

## 建模启示

这页最适合显式建一条多 stage pipeline，并用 `consumer_ready` 而不是只用 `transfer_done` 驱动阶段推进。

```text
HBMToTilePipeline {
  stage: hbm_fetch | noc_transit | sram_fill | tile_ready | compute | writeback
  in_flight_tiles
}
```

在 `07-workloads-case-studies` 里，这种 pipeline 最适合映射到 `Topology` 与 `Interaction`。若只关心峰值吞吐，可以折叠成最慢 stage；若关心断供和 bubble，就必须显式保留各 stage 切换。
