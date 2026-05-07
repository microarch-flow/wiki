# CPU / GPU / NPU 系统中的 DMA 分工

上级：[07 工作负载与案例](./README.md)

相关：[DMA 分类框架](../01-overview/taxonomy.md)、[DMA IP 与厂商图谱](../08-industry-ip/vendor-landscape.md)

## 这页在回答什么问题

为什么不同计算平台都需要 DMA，但它们关心的重点完全不同。

## CPU/SoC

更强调：

- 外设搬运
- OS / driver 协同
- 一致性与虚拟地址支持

## GPU

更强调：

- host-device 数据通道
- copy engine 并发
- 与 compute queue 并行

## NPU / AI accelerator

更强调：

- local memory staging
- tile 数据供给
- 与 NoC / SRAM 的耦合调度

## 一句话理解

同样叫 DMA，CPU 系统更关注软件和 I/O 语义，GPU 更关注 host-device 数据通路，NPU 更关注片上供数和执行节奏。
