---
title: "Posted、Non-Posted 与排序：何时可以继续下一步？"
---

<div id="posted-non-posted-completion-与-ordering" class="pcie-legacy-anchor"></div>
<div id="这页在回答什么问题" class="pcie-legacy-anchor"></div>

# Posted、Non-Posted 与排序：何时可以继续下一步？

上级：[链路、分层与事务基础](README.md)

请求类型决定是否有事务返回；排序规则决定某些事务能否越过其他事务。两者都不直接规定一个设备软件命令何时完成，也不能替代 CPU 的内存屏障与 DMA 同步。

<div id="先抓三个词" class="pcie-legacy-anchor"></div>
<div id="一个直观对照" class="pcie-legacy-anchor"></div>

## 先区分请求与返回

| 对象 | 示例 | Requester 等待什么 |
| --- | --- | --- |
| Posted 请求 | 普通 Memory Write | 无对应常规事务 Completion；仍受信用、排序和目标服务约束 |
| Non-Posted 请求 | Memory Read、配置读写 | 对应 Completion 或规定的错误处理 |
| Completion | 成功读的 CplD、成功配置写的 Cpl | 它是请求的返回，不是另一笔业务命令完成记录 |

Posted 不等于“没有错误”，也不等于“发出即全局可见”。错误要通过适用的状态和报告路径定位。

<div id="ordering-为什么重要" class="pcie-legacy-anchor"></div>

## 排序规则不是全局串行执行

PCIe 对不同类别、Traffic Class（TC）及属性组合规定允许或禁止的超越关系。独立读请求的 Completion 不必按请求发出次序整体返回；接收端须按身份和 Tag 匹配。Relaxed Ordering、ID-Based Ordering 等能力会改变适用条件，不能只凭两笔事务相邻发出就断言全系统观察顺序。

本文的发布示例采用设备规定的同一排序域，不启用会破坏所需先后关系的放宽属性。具体桥或 IP 还可能提供更严格的交付顺序；不能把一种 IP 的接口保证推广到所有 PCIe 路径。[AMD 接收排序说明](https://docs.amd.com/r/en-US/pg156-ultrascale-pcie-gen3/Receive-Transaction-Ordering)给出了请求、Completion 与放宽属性的具体例子。

## 主机发布描述符：内存先于 Doorbell

前提是设备接口规定 Doorbell 更新后允许取描述符。执行顺序是：CPU 填写字段 → 按 DMA 映射契约交接缓冲区并完成发布排序 → 用平台规定的 MMIO 访问器写 Doorbell → 设备取描述符。

缓存维护、内存排序和 MMIO 访问是不同操作。非一致 streaming 映射需要适用的 DMA 同步；coherent 映射省去相应缓存维护，但仍不能任意交换字段和有效位的发布顺序。单靠 PCIe 排序不能刷新 CPU 缓存。

## 设备发布完成：数据、有效位与通知

假设设备接口要求先写结果和 CQE 内容，再发布有效位或 phase，最后通知主机。PCIe 的正常写排序为这类发布关系提供基础；MSI/MSI-X 是向配置地址的写，不是无序的旁路线脉冲。[Linux MSI 指南](https://docs.kernel.org/PCI/msi-howto.html)解释了中断写不能越过其所依赖的前序数据写的常规使用条件。

CPU 仍需按队列及映射契约消费：

- coherent CQ：先检查有效位或 phase，观察到交还后执行所需读取屏障，再读内容；Linux 驱动中的 `dma_rmb()` 是对应例子。
- 非一致 streaming CQ：不能在同步前偷读有效位。先由缓冲区之外的通知或所有权机制确认交还，再 sync-for-CPU，然后读取；复用前按需 sync-for-device。

中断可能对应多个 CQE、错误事件或已经被其他消费者处理的工作。它不能替代具体队列状态检查。

<div id="对工程最重要的判断" class="pcie-legacy-anchor"></div>
<div id="一句话理解" class="pcie-legacy-anchor"></div>

## 观察点必须写进接口契约

“MMIO 写调用返回”“设备收到 Doorbell”“读事务收齐”“CQE 有效”“应用得到结果”是五个不同事件。某些场景用对设备的安全寄存器读回冲刷 posted 写；读回的目标、寄存器副作用和排序条件必须由平台与设备接口允许，不能把任意读当成全局屏障。

缓冲区交接细节集中在[缓冲区与可见性](../04-data-path-dma-interrupts/host-memory-pinned-buffer-visibility.md)。软件依据见 [Linux DMA 指南](https://docs.kernel.org/core-api/dma-api-howto.html)和[内存屏障示例](https://docs.kernel.org/core-api/wrappers/memory-barriers.html)。
