# DMA 与 Local Memory / DDR / HBM

上级：[05 系统集成](./README.md)

相关：[Tiling、Double Buffer 与 Overlap](../04-programming-model/tiling-double-buffering.md)、[RAM：地址映射、Channel/Rank/Bank/Row/Col](../../RAM/wiki/06-memory-controller/address-mapping-channel-rank-bank-row-col.md)、[RAM：访问模式与 Row Locality](../../RAM/wiki/07-system-architecture/sram-vs-dram-access-pattern.md)

## 这页在回答什么问题

为什么 DMA 的瓶颈经常不在 DMA 本体，而在它连接的 local memory、DDR、HBM 和 memory controller；以及为什么 DMA 的 burst 和 stride 选择会直接改写 DRAM row locality 与片上 SRAM 冲突形状。

## DMA 的真实上限由三类端点共同决定

任何一笔 DMA 路径至少都牵涉三类资源：

- 源端能不能稳定供出数据
- 互连能不能把数据运过去
- 目的端能不能按节拍接住数据

这意味着 DMA 的理论峰值几乎从来不是自己说了算。一个 AXI DMA 即使有足够深的 outstanding，也可能被 DDR return latency 压住；一个 AI local DMA 即使 NoC 很宽，也可能被 SRAM port conflict 压住；一个 writeback 路径即使写带宽够，也可能因为与 refill 共用 bank 而互相干扰。

## Local memory 里的问题常常比外存更“硬”

很多人天然更容易先盯 DDR/HBM，但片上 local memory 常常是更刚性的瓶颈。因为它的端口数、bank 数和仲裁策略都很有限，DMA 与 compute 之间的冲突会直接落成：

- bank conflict
- shared port arbitration
- refill 写入压住 compute 读取
- writeback 占住有限 staging buffer

这些问题的危险在于它们常常不会表现成“大带宽不够”，而会表现成“偶发断供”“steady-state 起不来”或“某个 tile 特别慢”。对 deterministic NPU 来说，这类局部冲突往往比外存平均带宽更致命。

## DDR / HBM 真正卡人的地方不是规格值，而是访问形状

外部 memory 最常见的误解是“规格书带宽够，就应该够”。但 [RAM wiki](../../RAM/wiki/06-memory-controller/address-mapping-channel-rank-bank-row-col.md) 已经说明，DRAM/HBM 的表现高度依赖请求落成什么形状。DMA 的 burst 长度、stride、alignment 和 stream 混合方式，会直接决定：

- row locality 是好是坏
- bank 并行能否被利用
- request 是否集中打到少数 channel 或 bank
- memory controller 是否能做有效调度

尤其是 stride 访问。软件视角下它只是“每行跳过一些字节”；DRAM 视角下，它可能意味着每次都打断 row hit 序列，让 controller 不断付 `PRE -> ACT -> RD/WR` 的代价。也就是说，`DMA ↔ RAM` 的关键关系不是“DMA 使用 DDR”，而是“DMA 的访问模式直接塑造了 DDR 能否兑现 row locality”。

## Burst、tile 和 row locality 为什么必须一起看

这三者在系统里是连锁关系。大 tile 往往更利于长 burst，也更可能形成稳定 row locality；但大 tile 同时会吃掉更多片上 buffer，让双缓冲和多流并发更难。小 tile 则可能让 local SRAM 调度更灵活，却会让外存侧 burst 变碎、header 开销变高、row reuse 变差。

所以 tile 不是 compute 自己的参数，burst 也不是 DMA 自己的参数；它们是 memory hierarchy 上下游共同决定的系统参数。最典型的错误做法，是只按算子映射选 tile，然后再寄希望于 DMA 自动把 memory system 用满。

## 一个工程上很好用的判断

如果 DMA 指标显示“request 发得出去，但 completion 慢”，优先检查这些点：

- memory controller 的实际端口利用率，而不是峰值规格
- response latency 分布，而不是平均值
- 是否存在 channel/bank 热点
- destination ejection / SRAM port 是否在后面排队

这条判断的价值在于，它能把“DMA 不快”的锅迅速拆开：是 memory 端真的慢，还是 DMA 把流量喂成了 memory 不喜欢的形状，还是目的端根本接不住。

## 从系统建模角度怎么看

这一页同样适合显式接入 `Resource / Topology / Interaction / Capability`：

- `Resource`：SRAM bank、SRAM port、MC port、channel、bank、row buffer
- `Topology`：DMA 到 local memory / DDR / HBM 的层级路径
- `Interaction`：burst、stride、row hit/miss、bank conflict、read/write 切换
- `Capability`：DMA 的 burst policy、tile size、outstanding depth，MC 的调度与 QoS

把这四层合起来，才能解释“为什么某个 DMA 访问模式在一代芯片上很好，在另一代上却突然变差”。

## 常见误解

常见误解：`DMA 瓶颈大多在互连上`。实际上 local SRAM port、bank conflict 和外存 return latency 常常更早卡住系统。

常见误解：`连续地址天然就对 DRAM 友好`。实际上还要看地址映射后是否真的形成 row locality 与 bank parallelism。

常见误解：`tile 只影响计算局部性`。实际上 tile 同时决定 burst 形状、row locality、buffer 占用和 completion 频率。

## 一句话理解

DMA 的真实上限不是自己定义的，而是由 `local memory + interconnect + DDR/HBM controller` 共同钳制出来的，而访问模式正是这条钳制链的核心变量。

## 建模启示

这页的最小模型，至少要同时保留片上端口冲突和外存返回延迟两个层次。event-driven 仿真里，建议显式追踪 `sram_port_busy`、`bank_conflict_count`、`row_hit_rate`、`mc_return_latency`。

一个可直接用的结构是：

```text
MemoryInteraction {
  burst_len
  stride
  tile_bytes
  row_hit_prob
  sram_port_class
}
```

如果只关心粗粒度吞吐，可以把 `row_hit_prob` 当成统计参数；如果关心不同 tile shape、stride pattern 或 bank hotspot 的真实差异，就必须显式展开地址映射与 bank/row 归属。
