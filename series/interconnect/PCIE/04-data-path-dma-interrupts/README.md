# 04 数据路径、DMA 与中断

上级：[系统 I/O 互连（PCIe）](../README.md)

先建立缓冲区合法可用的前提，再追踪设备读写、队列提交与完成。最后用完整返回时间解释有限请求窗口的性能约束。

## 推荐阅读顺序

1. [缓冲区与可见性](./host-memory-pinned-buffer-visibility.md)
2. [设备 DMA 读写](./device-dma-read-write-flow.md)
3. [队列、CQE 与 MSI-X](./queues-doorbells-completions-msix.md)
4. [读延迟与并发](./pcie-read-completion-latency.md)
