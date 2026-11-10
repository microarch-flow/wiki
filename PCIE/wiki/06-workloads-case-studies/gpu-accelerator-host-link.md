# GPU / 加速器 Host Link 视角

上级：[06 工作负载与案例](./README.md)

相关：[PCIe Read Completion 延迟为什么敏感](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)、[NOC Wiki](../../../NOC/wiki/README.md)

## 这页在回答什么问题

为什么在 GPU / 加速器系统里，PCIE 常常既重要又不是最终瓶颈主体。

## 它通常承担什么角色

- 控制面与任务提交入口
- host 和 device 之间的数据交换通道
- bring-up、加载、回读、日志、管理面链路

## 为什么它常常不是全局性能上限

因为设备内部往往还有：

- HBM / DDR 本地内存系统
- on-chip NoC
- 本地 DMA / copy engine

这意味着很多系统最终表现，是 `PCIE + 设备内互连 + 本地内存` 共同决定的。比较同一计算的两种条件：

- 输入一次从 host→device 传入并驻留 HBM，后续多轮复用，只有最终结果 device→host 回读。主机链路的有效字节按复用次数摊薄，计算或设备内带宽可能成为上限。
- 每批都从 host→device 传输入、从 device→host 回结果，且搬运不能与计算重叠。两方向有效字节及各自服务时间都进入批次关键路径；即使 HBM 很快，主机链路也可能限制性能。

实际是否重叠取决于队列、依赖、copy engine 和资源竞争，需在同一窗口测量，而不能仅凭设备有 HBM 推断。

## 但为什么仍然必须理解它

因为：

- host input feeding 往往经过 PCIE
- 小 batch 或交互式任务更受 host-device 往返影响
- bring-up、容错、虚拟化和资源共享都离不开它

## 一句话理解

在 GPU / 加速器里，PCIE 往往不是唯一的数据通路，但常常是决定 host-device 协同体验的第一层门槛。
