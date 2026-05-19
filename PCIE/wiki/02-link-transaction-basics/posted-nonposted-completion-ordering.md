# Posted / Non-Posted / Completion 与 Ordering

上级：[02 链路、分层与事务基础](./README.md)

相关：[TLP、DLLP 与 Completion 语义](./tlp-dllp-completion-basics.md)、[PCIe Read Completion 延迟为什么敏感](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)

## 这页在回答什么问题

为什么 posted、non-posted 和 completion 的区别，会直接影响系统可见性、延迟和调试方式。

## 先抓三个词

- `posted request`：请求发出后，不以同类 completion 返回作为完成条件
- `non-posted request`：请求发出后，需要某种响应
- `completion`：对请求的返回

## 一个直观对照

- memory write 常常更像 posted 路径
- memory read 一定要等 completion 数据回来
- config read 也依赖 completion

## Ordering 为什么重要

因为系统里同时存在：

- 控制面 MMIO 写
- 数据面 DMA read/write
- interrupt 或 message

如果不了解 ordering 和可见性边界，就容易出现：

- doorbell 已写，但 descriptor 还没对设备真正可见
- completion queue 已更新，但 CPU 观察点还没同步
- 软件把“请求已发出”和“对端已经处理完”误当成同一件事

## 对工程最重要的判断

PCIE 下很多同步问题都不是“功能错了”，而是：

- 请求类型不同
- 返回路径不同
- 软件观察点不同

## 一句话理解

posted / non-posted / completion 的区别，本质上是在定义“请求何时才算真正完成，以及谁能观察到这个完成”。
