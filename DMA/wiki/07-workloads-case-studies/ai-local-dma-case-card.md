# AI Local DMA 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[AI 加速器里的 DMA](./ai-accelerator-dma.md)、[HBM 到 Tile 的数据供给链](./hbm-to-tile-data-supply-chain.md)、[多维 DMA 与 Stride 地址生成](../03-dma-microarchitecture/multidimensional-stride-dma.md)

## 这页在回答什么问题

为什么 AI accelerator 里常会有一类 “local DMA”，它和 SoC DMA、PCIe DMA 看起来相似，但优化目标明显不同；以及为什么它最值得关注的是 local memory 与 compute 的节拍耦合。

## 典型系统位置

AI local DMA 通常位于 cluster 或 tile 附近，连接 cluster SRAM、tile buffer、NoC endpoint 或专用 load/store 路径。它往往不直接面向通用 OS 或 host 软件，而更直接地服务编译器、runtime 和片上执行计划。

## 它通常在解决什么问题

典型职责包括：

- 局部 staging
- tensor tile 搬运
- refill / consume / writeback 协同

从功能上看不复杂，但它的关键在于“什么时候搬”通常比“怎么提交”更重要，因为它离 compute 很近，错一拍就可能直接断供。

## 核心机制

典型机制包括：

- 高频搬运触发与调度
- stride / 2D / 3D 地址生成
- 对 local memory 端口和 bank 布局的强耦合
- 与 compute pipeline 的细粒度同步

这里不要默认它一定由 CPU/driver 高频 submit。很多 local DMA 更常见的是由编译器、runtime 计划，甚至硬件依赖链自动触发。

## 最常见瓶颈

最常见的问题通常包括：

- bank conflict
- refill 和 compute 抢 local port
- outstanding 不足导致 pipeline 断供
- writeback 回压反向拖慢下一轮

这使得 AI local DMA 的重点不在通用软件接口，而在局部执行节拍是否匹配。

## 为什么它最能体现 DMA 的系统性

AI local DMA 看似最“局部”，其实最能体现 DMA 的系统性。因为它直接把上游 HBM/NoC 行为、局部 SRAM 结构、下游 compute 读取节拍和 completion/flip 状态绑在一起。它既不是纯 I/O block，也不是纯 micro-op 单元，而是局部数据流是否连续的守门人。

## 常见误解

常见误解：`local DMA 只是范围更小的普通 DMA`。实际上它的重点常常从软件通用性转向供数节拍与片上耦合。

常见误解：`只要 HBM 到 cluster 路径够快，local DMA 就不是瓶颈`。实际上 local SRAM port、bank 和 buffer flip 常常更早坏掉。

常见误解：`AI local DMA 不需要太多 completion 语义`。实际上哪怕没有复杂软件 completion，也仍然需要明确 ready/consume/release 的局部完成状态。

## 一句话理解

AI local DMA 是最能体现 DMA 系统性的一类对象，因为它直接决定 compute 是否能持续吃到数据。

## 建模启示

这张案例卡最适合显式保留局部 buffer 状态与 consumer-ready 边界。

```text
LocalDMAProfile {
  buffer_count
  local_port_class
  stride_pattern
  consumer_ready_latency
}
```

在 `07-workloads-case-studies` 里，这类 profile 最适合映射到 `Resource` 与 `Interaction`。若只关心高层带宽，可折叠 local state；若关心断供和 bubble，就必须显式建模 buffer / port 状态。
