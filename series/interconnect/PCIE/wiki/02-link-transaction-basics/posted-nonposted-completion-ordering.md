# Posted / Non-Posted / Completion 与 Ordering

上级：[02 链路、分层与事务基础](./README.md)

相关：[TLP、DLLP 与 Completion 语义](./tlp-dllp-completion-basics.md)、[PCIe Read Completion 延迟为什么敏感](../04-data-path-dma-interrupts/pcie-read-completion-latency.md)

## 这页在回答什么问题

为什么 posted、non-posted 和 completion 的区别，会直接影响系统可见性、延迟和调试方式。

## 先抓三个词

- `posted request`：不产生对应的事务级 Completion，例如普通 Memory Write。
- `non-posted request`：需要事务级 Completion，例如 Memory Read、配置读写。
- `completion`：与 non-posted 请求匹配的返回 TLP；成功 Memory Read 返回数据，成功配置写返回不带数据的 Cpl。错误状态也可能通过 Completion 返回。

## 一个直观对照

- 普通 Memory Write 是 posted 路径
- 普通 Memory Read 成功时由 Completion 返回数据；UR、CA 等错误 Completion 返回状态，不提供有效读取数据
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

以主机发布描述符为例，前提是设备接口规定 doorbell 后可读取描述符：CPU 先填字段，再按 DMA 映射和平台契约完成交接与发布排序，最后用规定的 MMIO 访问器写 doorbell。对于非一致的 streaming 映射，还须在交给设备之前按 DMA API 同步；仅靠 PCIe ordering 不能刷新 CPU 缓存。设备观察到有效的描述符后才可取数。完成队列（CQ）的读取顺序取决于 DMA 映射：

- **一致性 coherent CQ**：设备按接口契约先写内容再发布 phase/ownership；CPU 按该接口检查有效位，观察到交还后执行 `dma_rmb()`，再读取完成项内容。
- **非一致 streaming CQ**：CPU 不能在同步前读取该缓冲区的有效位。先由该缓冲区以外的通知或所有权契约确认设备已交还，再按 DMA API 执行 sync-for-CPU，然后读取有效位和数据。复用前按契约 sync-for-device。通知本身必须具有接口规定的交还语义。

不同接口的屏障、同步和 MMIO 访问器不能互换，见 [Linux DMA 映射指南](https://docs.kernel.org/core-api/dma-api-howto.html) 和 [内存屏障示例](https://docs.kernel.org/core-api/wrappers/memory-barriers.html)。

## 对工程最重要的判断

PCIE 下很多同步问题都不是“功能错了”，而是：

- 请求类型不同
- 返回路径不同
- 软件观察点不同

## 一句话理解

posted / non-posted / completion 的区别，本质上是在定义“请求何时才算真正完成，以及谁能观察到这个完成”。
