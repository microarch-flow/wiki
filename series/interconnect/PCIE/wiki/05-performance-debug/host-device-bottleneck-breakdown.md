# Host 到 Device 路径的瓶颈拆解

上级：[05 性能与调试](./README.md)

相关：[设备 DMA 的读写路径](../04-data-path-dma-interrupts/device-dma-read-write-flow.md)、[RAM Wiki](../../../../storage/reading-and-reference/01-reading/README.md)

## 这页在回答什么问题

当你看到“PCIE 不够快”时，应该怎样把瓶颈拆到真正可定位的层级。

## 一条完整路径可以拆成

- device 发包能力
- endpoint 内部队列和 DMA 调度
- switch / root complex 路径
- IOMMU / host memory 子系统
- CPU / driver 提交与回收路径

## 为什么这比只看链路速率有效

因为很多时候链路没满，不代表没有瓶颈。典型情况包括：

- 软件 doorbell 太稀疏
- queue 深度不够
- read completion latency 太大
- 中断过于频繁
- host memory 本身不稳定

## 一个实用拆解顺序

1. 先确认拓扑和链路状态
2. 再看 read/write 比例
3. 再看 queue、outstanding 和 batching
4. 再看 IOMMU / memory / interrupt 路径

同一时间窗记录任务提交率、队列占用、读 Tag 占用、完整 Completion RTT、方向吞吐和各段拥塞计数。若设备待发队列经常为空且链路空闲，先检查 CPU 提交、doorbell 和描述符供给；反例是队列空但上一个任务仍在长时间计算，此时不能只归因软件。若读任务排队、Tag 长期满且最终 CplD RTT 上升，先检查返回路径、翻译和内存服务；反例是 Tag 满而 RTT 稳定时，可能只是槽数不足，仍需与吞吐和路径计数一起判断。

## 一句话理解

PCIE 性能问题通常是整条 host-device 链路的协同问题，不是单独某一级“带宽不够”。
