# Non-Coherent vs Coherent DMA

上级：[02 基础对象与传输语义](./README.md)

相关：[缓存一致性、IOMMU 与地址空间](./consistency-cache-coherency.md)、[同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)、[BUS：Coherent Bus vs Non-Coherent Bus](../../../series/interconnect/BUS/wiki/03-on-chip-protocol-families/coherent-bus-vs-noncoherent-bus.md)

## 这页在回答什么问题

为什么 coherent DMA 往往被误解成“更高级，因此一定更简单更快”；以及什么时候 non-coherent 反而是更清晰、更便宜、甚至更合适的选择。

## 这不是先进与落后之争，而是谁承担复杂度

讨论 coherent 和 non-coherent 时，最容易犯的错误就是把它讲成代际升级关系，好像 coherent 一定全面优于 non-coherent。更准确的说法是：两者只是在不同位置承担复杂度。

non-coherent DMA 把更多一致性劳动留给软件。软件必须明确何时 clean、何时 invalidate、何时切 ownership，但硬件路径通常更简单，流量也更可控。

coherent DMA 把一部分复杂度推给互连和缓存协议。软件更容易拿到统一视图，但系统要为 snoop、一致性维护和额外流量付代价。它减少的是“人肉维护副本”的成本，不是免费送来吞吐。

## Non-coherent 什么时候反而更自然

如果系统路径固定、参与者少、buffer 生命周期边界清楚，non-coherent 往往更自然。典型例子是很多 MCU/SoC 外设 DMA、固定数据流 pipeline、强实时嵌入式路径。这类系统更关心低复杂度、低功耗、可控时序，不愿意为了更通用的共享语义付出全系统成本。

从软件角度看，non-coherent 像传纸条。谁在什么时候把纸条交给谁，责任非常清楚；代价是每次都要手工确认交接动作。这个类比只成立在“边界清楚的交接”这一点上；它不能被延伸成“non-coherent 总是更慢”或“总是更低效”。

## Coherent 什么时候值得

当系统强调多核共享 buffer、用户态直通设备、复杂 driver/runtime 协同或多 VM 共用设备时，coherent DMA 的收益会迅速放大。因为软件若还要手动维护大量共享 buffer 的可见性，复杂度和出错率都会爆炸。

从直觉上看，coherent 更像共享白板。参与者看到的是更统一的状态，不需要每次都复印和交接；但白板越大、参与者越多，维护秩序的成本也越高。这个类比的边界同样要明确：共享白板只解释“共享视图”，不解释具体的 snoop latency、NoC 流量或协议死角。

## 性能上到底谁更好

这个问题如果不加条件，基本没有意义。coherent DMA 在某些共享访问工作流里会明显降低软件开销和错误率，于是端到端性能更好；但在高带宽、长流、固定路径系统里，一致性维护本身可能就是额外负担。non-coherent DMA 若软件能把 ownership 切换做得足够规整，完全可能得到更干净的数据路径。

更尖锐地说：

- 关心软件易用性和共享语义时，coherent 往往更值。
- 关心低复杂度、可预测性和功耗面积时，non-coherent 往往更值。
- 关心端到端性能时，不能只盯 coherence 标签，必须把 traffic pattern、buffer 生命周期和系统共享程度一起看。

## Linux 示例：映射、可见性和所有权

硬件路径是否参与 cache coherence，与 Linux 的 coherent mapping、streaming mapping 是不同维度。`dma_alloc_coherent()` 给出的 coherent mapping 由 DMA API 提供 CPU 与设备的共享可见性；这不保证硬件实现方式，也不消除顺序与并发访问规则。streaming mapping 以方向和交接为接口，即使底层硬件具备一致性，也仍须遵守 DMA API 的 mapping 和同步契约。

以下是构造示例。前提是设备文档规定：descriptor 的 `valid` 是设备可读取的所有权标志；设备观察到它后才读取其他字段；completion 表示相应 DMA 写入已完成。设备的实际 doorbell、状态位和总线顺序规则必须另查手册。

### Coherent descriptor：可见性不等于顺序

1. 驱动用 `dma_alloc_coherent()` 分配 descriptor ring，检查分配结果；记录 CPU 地址和设备 DMA 地址。
2. CPU 写 descriptor 地址、长度等字段，执行适用于该协议的写屏障，再发布 `valid/owner`。若设备用 MMIO doorbell 通知，还要按 Linux MMIO accessor 与设备契约保证 descriptor 发布先于 doorbell；必要时处理 posted write。
3. 设备处理后按其协议发布 completion。CPU 观察完成标志后，按该协议执行必要的读顺序约束，再读取设备写入的其他字段；直到设备已放弃所有权才复用该槽位。

关键点：coherent mapping 让双方可观察更新，但 CPU 仍可能重排 descriptor 字段的写入。用 `wmb()` / `dma_wmb()` 还是其他同步原语，取决于共享对象和平台接口；不能把屏障当成 cache 维护，也不能假设 doorbell 自带所有设备所需的顺序。见 [Linux DMA API 指南](https://docs.kernel.org/core-api/dma-api-howto.html) 和 [Linux memory barriers](https://docs.kernel.org/core-api/wrappers/memory-barriers.html)。

### Streaming 接收 buffer：设备写、CPU 读

1. 准备可供 DMA 映射的 buffer，调用 `dma_map_single(dev, buf, len, DMA_FROM_DEVICE)` 并用 `dma_mapping_error()` 检查。成功后把返回的 `dma_addr_t` 交给设备；它不必等于 CPU 虚拟地址或物理地址。设备拥有 buffer 期间，CPU 不读写该区域。
2. 等待设备定义的、确实保证数据写入完成的 completion。若保留映射并由 CPU 读取，先调用 `dma_sync_single_for_cpu(dev, dma_addr, len, DMA_FROM_DEVICE)`，再由 CPU 消费数据。
3. 若继续复用保留的 streaming mapping，CPU 访问结束后，按 DMA API 调用 `dma_sync_single_for_device()` 再交回设备。若不复用映射，则在设备活动结束后调用 `dma_unmap_single()`；保持原设备、长度和方向匹配。设备再次使用前必须重新映射或按 API 重新交接。

这是方向为 `DMA_FROM_DEVICE` 的例子；`DMA_TO_DEVICE` 是 CPU 写完数据并通过 map 或 `sync_for_device` 交给设备读取。`DMA_BIDIRECTIONAL` 必须满足双向访问的同步要求。不要把 `sync` 当成等待 DMA 完成：先有设备完成契约，再执行同步。非一致性系统还应避免 DMA buffer 与不相关 CPU 数据共享 cache line，防止缓存维护影响邻近数据。具体接口以 [Linux DMA API 指南](https://docs.kernel.org/core-api/dma-api-howto.html) 为准。

## 常见误解

常见误解：`coherent DMA 一定更快`。实际上 coherent 可能引入额外 snoop 和一致性流量，速度取决于系统共享模式，而不是名字。

常见误解：`non-coherent DMA 一定落后`。实际上很多固定功能、强实时系统恰恰更适合 non-coherent，因为它把状态边界说得更清楚。

常见误解：`选了 coherent 就不会再有脏数据 bug`。实际上 barrier、completion 语义和 buffer 生命周期仍然会制造 bug。

## 一句话理解

coherent 和 non-coherent 的核心差别，不是谁更先进，而是谁承担一致性复杂度，以及系统是否愿意为共享视图付出代价。

## 建模启示

在仿真里，coherent 和 non-coherent 至少要体现为不同的可见性状态机。最小做法不是模拟完整协议，而是显式建一个 `visibility_update_cost` 和 `software_sync_cost` 的 trade-off。

例如：

```text
CoherenceModel {
  mode: coherent | noncoherent
  software_sync_cost
  hw_visibility_cost
}
```

如果只关心粗粒度性能，可以把 coherent 额外开销折叠成 `hw_visibility_cost`，把 non-coherent 的 flush/invalidate 折叠成 `software_sync_cost`；如果关心正确性，就必须再补 `owner_transition` 和 `completion_visible_after_sync` 这类显式事件。
