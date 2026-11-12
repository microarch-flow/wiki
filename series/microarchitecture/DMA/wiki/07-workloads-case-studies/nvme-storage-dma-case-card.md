# NVMe / 存储路径中的 DMA

上级：[07 工作负载与案例](./README.md)

相关：[PCIe NIC DMA 案例卡](./pcie-nic-dma-case-card.md)、[AXI / PCIe 视角下的 DMA](../05-system-integration/axi-pcie-view.md), [PCIE: 队列、Doorbell、Completion 与 MSI-X](../../../../interconnect/PCIE/wiki/04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)

## 这页在回答什么问题

为什么存储系统里的 DMA 和网络 DMA 有相似结构，但性能目标和瓶颈又不完全一样；以及为什么 NVMe 更适合训练你对 `queue depth + steady-state + completion` 的直觉。

## 典型系统位置

NVMe controller 位于设备侧，通过 PCIe 与 host memory 交互，并和 submission/completion queue 协同。它和 NIC DMA 一样属于 device DMA to host memory，但 workload 形状与软件目标不同。

## 它通常在解决什么问题

典型职责包括：

- 高吞吐块数据传输
- 大量并发 I/O 的稳定推进
- 尽量减少 CPU 参与每次数据移动

I/O 大小、queue depth、轮询和中断策略由应用与设备决定。4 KiB、低 queue depth 的延迟敏感读也是有效场景；不能默认 NVMe 总是大数据、深队列或比 NIC 中断少。

## 核心机制

这类路径通常包含：

- submission / completion queue pair
- PRP / SGL 一类 buffer 描述
- DMA read / write host memory
- host 软件消费 completion queue

例如 host 发布 SQE 并敲 doorbell，控制器 DMA read 获取命令及 PRP/SGL。NVMe Read 从介质侧取数据，通常用 PCIe posted Memory Write 写主机 buffer；NVMe Write 则发 Memory Read 并接收一个或多个 CplD，读取主机数据后处理介质写。命令结束后控制器写 CQE，主机通过轮询或可选 MSI-X 发现并消费 CQE，再按接口更新 CQ head 以回收位置。PCIe CplD 是事务返回，CQE 是存储命令状态。

命令完成并不无条件等于断电持久：具体取决于设备 volatile write cache、命令 FUA/flush 和设备契约。实验需分别定义控制器接收、介质/持久域及软件可见的边界。Flush 的适用范围和写缓存语义见 [NVM Express Base Specification 2.2](https://nvmexpress.org/wp-content/uploads/NVM-Express-Base-Specification-Revision-2.2-2025.03.11-Ratified-1.pdf)。

## 最常见瓶颈

常见瓶颈包括：

- 小 I/O 下控制开销占比过高
- host buffer 分散，PRP/SGL 组织成本升高
- completion 延迟拖累 queue depth 收益
- host 软件消费 completion 不及时

这类问题经常会表现成“明明深队列了，吞吐还是起不来”，本质上是 steady-state 没形成，而不是单次 DMA 太慢。

## 为什么它和 NIC 类似但不相同

两者都依赖 queue、host memory 和 completion，但 NIC 的包率与 NVMe 的 I/O 大小、介质服务及 queue depth 有不同分布；具体瓶颈须依 workload 测量。

所以它们适合共用某些抽象，但不适合共用全部调优直觉。

## 常见误解

常见误解：`NVMe 必须依赖深队列`。实际上低队列深度的单次延迟和高并发 steady-state 都是合法目标。

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
