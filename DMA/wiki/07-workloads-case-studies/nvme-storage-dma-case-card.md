# NVMe / 存储路径中的 DMA

上级：[07 工作负载与案例](./README.md)

相关：[PCIe NIC DMA 案例卡](./pcie-nic-dma-case-card.md)、[软件栈与编程模型](../04-programming-model/software-stack.md)

## 这页在回答什么问题

为什么存储系统里的 DMA 和网络 DMA 有相似结构，但性能目标和瓶颈又不完全一样。

## 典型系统位置

- NVMe controller 位于设备侧
- 通过 PCIe 与 host memory 交互
- 与 submission/completion queue 协同

## 它通常在解决什么问题

- 高吞吐块数据传输
- 尽量减少 CPU 参与每次 I/O 数据移动
- 让大量并发 I/O 能稳定推进

## 核心机制

- queue pair
- PRP / SGL 类 buffer 描述
- DMA read/write host memory
- completion queue

## 最常见瓶颈

- 小 I/O 下控制开销占比高
- host buffer 分散导致 SGL 成本升高
- completion 延迟拖累队列深度收益

## 最值得抄走的判断

存储 DMA 强调的是 `深队列并发 + 稳定 completion`，不是单次传输极限速度。

## 一句话理解

NVMe DMA 是“高并发、块导向、completion 驱动”的代表性案例，适合训练你对 queue-depth 与 steady-state 的感觉。
