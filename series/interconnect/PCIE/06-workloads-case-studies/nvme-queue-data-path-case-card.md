---
title: "NVMe over PCIe：从 SQ 提交到 CQ 回收"
---

<div id="nvme-队列与数据路径案例卡" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# NVMe over PCIe：从 SQ 提交到 CQ 回收

上级：[工作负载与案例](README.md)

NVMe 命令名按存储操作命名，PCIe DMA 方向按设备发起的内存访问命名。NVMe Read 通常让控制器向主机写数据；NVMe Write 通常让控制器从主机读数据。不能看到“Read”就认定线上一定是 Memory Read。

<div id="典型系统位置" class="pcie-legacy-anchor"></div>

## 约定一个普通主机内存队列

教学前提：控制器已初始化，I/O SQ/CQ 位于合法映射的主机内存，数据缓冲区已准备好，使用普通 Doorbell 通知。控制器内存缓冲、Doorbell Buffer 等可选能力不属于这个例子的默认条件。

| 对象 | 主机职责 | 控制器职责 |
| --- | --- | --- |
| SQ | 填命令、数据位置与命令标识，发布队尾 | 取命令并消费 |
| 数据缓冲区 | 建立映射、按方向交接所有权 | 按命令访问 |
| CQ | 检查 phase、状态和命令身份，归还空间 | 写完成项并推进生产位置 |

<div id="最关键的机制" class="pcie-legacy-anchor"></div>

## 一次 NVMe Read 的事件链

1. 主机填写 SQE，以命令规定的 PRP/SGL 等形式描述数据位置，并按接口发布。
2. 主机写 SQ Tail Doorbell，告知控制器新的队尾。
3. 控制器用 PCIe Memory Read 取得 SQE，接收对应 CplD。
4. 控制器执行存储读取，并通常用 Memory Write 把载荷送到主机缓冲区。
5. 控制器按 NVMe 规则发布 CQE，可依配置产生中断；主机也可轮询。
6. 主机检查新 CQE，处理状态并推进 CQ head，按要求更新 CQ Head Doorbell。

若主机不归还 CQ 空间，控制器可因完成队列空间受限而停止推进。只提高 SQ 深度不能消除这一限制。

## NVMe Write 改变哪一段

SQ 获取和 CQ 发布仍存在。主要数据阶段改为控制器用 PCIe Memory Read 取得主机载荷，并等待相应 CplD。控制器之后按命令语义执行存储写入。

| 名称 | 表示什么 |
| --- | --- |
| PCIe Completion | 某笔 Non-Posted 请求的返回 |
| NVMe CQE | 一个 NVMe 命令的完成状态 |
| 数据持久化 | 数据满足相应存储持久性条件；取决于命令、缓存设置及 Flush/FUA 等语义 |

不能把“DMA 读已收齐”当成“存储写命令已成功”，也不能不看持久性语义就把所有成功 CQE 解释为断电后必然保留。

<div id="为什么它值得学" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 应该测哪些量

软件队列深度、控制器实际并发、PCIe Tag 占用和介质内部并发是不同量。分别观察提交、取命令、数据搬运、CQE 可见和主机消费；否则“提高 QD 后变快”无法说明是哪一段得到改善。

本文队列事件链核对 [NVMe over PCIe Transport 1.4](https://nvmexpress.org/wp-content/uploads/NVM-Express-NVMe-over-PCIe-Transport-Specification-Revision-1.4-Ratified-2026.07.31.pdf) §3.4 与附录 A。传输规范解释寄存器与队列承载，命令及持久性须结合对应 Base/NVM Command Set 版本。通用通知关系见[队列与 MSI-X](../04-data-path-dma-interrupts/queues-doorbells-completions-msix.md)。
