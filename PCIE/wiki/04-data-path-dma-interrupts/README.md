# 04 数据路径、DMA 与中断

这一部分把 PCIE 放回真实运行路径里：

- 设备怎样 DMA 读写主机内存
- 软件怎样用 queue 和 doorbell 提交工作
- 完成与中断怎样回到主机

## 推荐阅读顺序

1. [设备 DMA 的读写路径](./device-dma-read-write-flow.md)
2. [队列、Doorbell、Completion 与 MSI-X](./queues-doorbells-completions-msix.md)
3. [PCIe Read Completion 延迟为什么敏感](./pcie-read-completion-latency.md)
4. [主机内存、Pinned Buffer 与设备可见性](./host-memory-pinned-buffer-visibility.md)
