# NVMe / 存储路径中的 DMA

上级：[07 工作负载与案例](./README.md)

相关：[PCIe NIC DMA 案例卡](./pcie-nic-dma-case-card.md)、[AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md), [PCIE: 队列、Doorbell、Completion 与 MSI-X](../../../PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

为什么存储系统里的 DMA 和网络 DMA 有相似结构，但性能目标和瓶颈又不完全一样；以及为什么 NVMe 更适合训练你对 `queue depth + steady-state + completion` 的直觉。

## 典型系统位置

NVMe controller 位于设备侧，通过 PCIe 与 host memory 交互，并和 submission/completion queue 协同。它和 NIC DMA 一样属于 device DMA to host memory，但 workload 形状与软件目标不同。

## 它通常在解决什么问题

典型职责包括：

- 高吞吐块数据传输
- 大量并发 I/O 的稳定推进
- 尽量减少 CPU 参与每次数据移动

与网络 DMA 相比，NVMe 更少受到极端小包节拍和中断风暴影响，但更强依赖深队列 steady-state 和 completion 回收效率。

## 核心机制

这类路径通常包含：

- submission / completion queue pair
- PRP / SGL 一类 buffer 描述
- DMA read / write host memory
- host 软件消费 completion queue

它的“数据大、队列深、完成驱动强”这三个特征，会直接决定实验和建模方法。

## 最常见瓶颈

常见瓶颈包括：

- 小 I/O 下控制开销占比过高
- host buffer 分散，PRP/SGL 组织成本升高
- completion 延迟拖累 queue depth 收益
- host 软件消费 completion 不及时

这类问题经常会表现成“明明深队列了，吞吐还是起不来”，本质上是 steady-state 没形成，而不是单次 DMA 太慢。

## 为什么它和 NIC 类似但不相同

两者都依赖 queue、host memory、completion 和 PCIe completion path，但 NIC 更怕小包率和 moderation，NVMe 更怕 completion 回收速度与深队列稳态不匹配。网络流量更偏连续包流，存储流量更偏块导向和 I/O 并发。

所以它们适合共用某些抽象，但不适合共用全部调优直觉。

## 常见误解

常见误解：`NVMe DMA 的重点是单次传输极限速度`。实际上它更强调深队列下的 steady-state completion。

常见误解：`storage DMA 和 network DMA 调优一样`。实际上两者对小包/小 I/O、moderation 和 completion 回收的敏感点不同。

常见误解：`completion 只是通知软件一下`。实际上 completion 路径常直接决定队列深度收益能否兑现。

## 一句话理解

NVMe DMA 是“高并发、块导向、completion 驱动”的代表性案例，适合训练你对 queue depth 与 steady-state 的感觉。

## 建模启示

这张案例卡最适合显式保留 queue depth 与 host completion consume rate。

```text
NVMEDMAProfile {
  queue_depth
  io_size
  sgl_segments
  completion_consume_rate
}
```

在 `07-workloads-case-studies` 里，这类 profile 最适合映射到 `Interaction` 与 `Capability`。若只关心大块顺序 I/O，可以弱化 `sgl_segments`；若关心小 I/O 和 mixed workload，就必须保留。
