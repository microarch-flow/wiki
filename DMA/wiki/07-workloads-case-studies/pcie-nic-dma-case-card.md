# PCIe NIC DMA 案例卡

上级：[07 工作负载与案例](./README.md)

相关：[AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md)、[队列、Doorbell 与 Completion](../04-programming-model/queues-doorbells-completions.md)、[PCIE Wiki: NIC DMA 案例卡](../../../PCIE/wiki/06-workloads-case-studies/nic-dma-case-card.md)

## 这页在回答什么问题

网卡里的 DMA 为什么是理解 `device DMA + host memory + ring buffer` 最好的案例之一；以及为什么它的核心不在“网卡会 DMA”，而在 `ring + batching + moderation` 如何维持高速 steady-state。

## 典型系统位置

NIC DMA engine 位于设备侧，通过 PCIe 访问 host memory，并与 RX/TX ring、descriptor、MSI-X 中断和 IOMMU 紧密配合。它的系统画像天然是“设备侧发起者 + 主机软件回收者”。

## 它通常在解决什么问题

典型职责包括：

- 把收包数据写入 host buffer
- 从 host buffer 取包发出
- 用 ring 与 completion 把高速包流和 CPU 解耦

这里最关键的不是某一次收发包多快，而是大量小包和中包能否在长时间 steady-state 里持续推进。

## 核心机制

一张典型画像通常包括：

- RX/TX descriptor ring
- host memory DMA read / write
- completion / interrupt moderation
- IOMMU / 映射与隔离

NIC DMA 的复杂度恰恰来自这几个机制必须同时稳定工作。包流一旦足够密，中断、ring 回收、mapping 生命周期和 host cache locality 都会开始反作用到 DMA。

## 最常见瓶颈

最常见的问题往往不是链路带宽本身，而是：

- 小包导致 descriptor 和 completion 压力过大
- interrupt 过多，CPU 被 completion 路径拖住
- IOMMU / 映射管理开销显著
- host buffer locality 差，软件消费与 cache 行为恶化

这也是为什么 NIC DMA 的建模重点通常是 queue、moderation、completion visible latency，而不是单纯 PCIe 峰值带宽。

## 延迟要怎么拆

NIC DMA 最好至少拆成四段看：

- ring submit 到 DMA issue
- DMA 数据搬运本身
- completion 对 host 软件可见
- interrupt moderation / polling 带来的额外等待

如果这四段不拆，很多“网卡抖一下”的问题都会被误判成“PCIe 不稳定”。

## 常见误解

常见误解：`NIC DMA 的核心就是 PCIe 带宽`。实际上小包场景下，descriptor、completion 和 interrupt 路径常常先成为瓶颈。

常见误解：`moderation 只是省点中断`。实际上 moderation 直接在吞吐、尾延迟和 CPU 开销之间做 trade-off。

常见误解：`host buffer 只是存数据的地方`。实际上它的映射和 locality 直接影响 DMA 与软件消费的稳态。

## 一句话理解

PCIe NIC DMA 最值得学的不是“网卡会 DMA”，而是它如何用 `ring + batching + moderation` 维持高速 steady-state。

## 建模启示

这张案例卡最适合显式保留 host-visible completion 与 moderation。

```text
NICDMAProfile {
  ring_depth
  batch_size
  moderation_window
  iova_mapping_cost
}
```

在 `07-workloads-case-studies` 里，这类 profile 最适合映射到 `Capability` 和 `Interaction`。若只关心大包吞吐，可以弱化 moderation；若关心小包和尾延迟，它必须保留。
