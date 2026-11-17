---
title: "从提交队列到完成通知：Doorbell、CQE 与 MSI-X"
---

<div id="队列doorbellcompletion-与-msi-x" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# 从提交队列到完成通知：Doorbell、CQE 与 MSI-X

上级：[数据路径、DMA 与中断](README.md)

队列保存工作与结果，Doorbell 提示设备检查已发布工作，MSI-X 提示 CPU 服务设备。队列格式属于设备接口；PCIe 承载相关读写和中断消息。本文采用主机内存中的 SQ/CQ，不把它推广到所有设备。

## 四个对象分别做什么

| 对象 | 生产者与消费者 | 携带的信息 |
| --- | --- | --- |
| 提交队列 SQ / 描述符环 | 软件生产，设备消费 | 命令、DMA 地址、长度、命令标识 |
| Doorbell | 软件更新，设备观察 | 已发布的队尾或接口规定的通知值 |
| 完成项 CQE | 设备生产，软件消费 | 命令标识、状态及接口规定的有效位或 phase |
| MSI-X | 设备发写消息，平台路由到 CPU | 请求软件服务某个中断向量 |

一个向量可以服务多条队列，一个中断可以对应多个 CQE。队列、向量和 CPU 的映射由设备、驱动及资源配置决定，不能默认一一对应。

<div id="一条典型控制到完成链路" class="pcie-legacy-anchor"></div>

## 从提交到回收的一次执行

1. 软件确认 SQ 有空位，填写命令和已映射的数据地址。
2. 按缓冲区与排序契约发布队列项，再更新 Doorbell。
3. 设备读取新 SQE，执行所需 DMA 与内部工作。PCIe 读返回只完成其中一段取数。
4. 设备按接口先发布完成内容和有效状态，再选择通知软件。
5. 软件按映射规则取得可见性，检查 phase/有效位、命令标识和状态，消费 CQE。
6. 软件按接口更新 CQ 消费指针或 Doorbell，回收允许复用的队列槽和缓冲区。

第 6 步不可省略。若设备不知道 CQ 空间已归还，即使载荷链路空闲，也可能停止生成完成项并反压后续任务。

<div id="为什么这是最重要的软件契约" class="pcie-legacy-anchor"></div>

## 环形队列为什么需要有效状态

教学例：CQ 有 4 个槽，设备从槽 3 绕回槽 0。旧内容仍留在槽 0，软件不能只看“该地址非零”判断新完成。采用 phase 的接口会在回绕时改变预期 phase；软件只有观察到本轮有效状态，才按规定顺序读本轮内容。其他接口可能使用不同的所有权位或计数器。

这一机制解决新旧条目识别，不替代非一致内存的同步。详细交接规则见[缓冲区文章](host-memory-pinned-buffer-visibility.md)和[排序文章](../02-link-transaction-basics/posted-nonposted-completion-ordering.md)。

<div id="一句话理解" class="pcie-legacy-anchor"></div>

## MSI-X、合并与轮询的取舍

| 方式 | 收益 | 代价 |
| --- | --- | --- |
| 每次完成及时通知 | 低负载下不需持续轮询 | 高频完成时中断处理成本较大 |
| 按门限或定时合并 | 摊薄通知成本 | 早到的完成可能增加等待 |
| 轮询 CQ | 可减少唤醒等待，适合持续高负载 | 占用 CPU，仍需正确同步 |

MSI-X 通过表项选择消息地址、数据与屏蔽状态。正确排序的通知写为前序数据写提供顺序关系，但通知到达不能代替 CQE 检查，也不能替代非一致缓存维护。[Linux MSI 指南](https://docs.kernel.org/PCI/msi-howto.html)说明机制和配置接口。

从轮询切换到睡眠时，还要防止“检查为空后、真正睡眠前”丢失唤醒。设备 pending/重触发规则与软件等待原语必须协同；通用事件链见 [BUS 的通知流程](../../BUS/04-microarchitecture-integration/doorbell-completion-interrupt-flow.md)。实际队列例子见 [NVMe 案例](../06-workloads-case-studies/nvme-queue-data-path-case-card.md)。
