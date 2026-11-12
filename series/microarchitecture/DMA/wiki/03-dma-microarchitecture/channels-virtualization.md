# 多通道、虚拟化与隔离

上级：[03 DMA 引擎微架构](./README.md)

相关：[缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)、[DMA IP 评估清单](../08-industry-ip/dma-ip-checklist.md)

## 这页在回答什么问题

为什么现代 DMA 往往不是单通道裸引擎，而是多通道、多队列、多 context、可隔离的共享基础设施；以及这些能力到底是在解决性能问题、软件问题还是安全问题。

## 先把 channel、queue、stream、context 分开

这些词在很多文档里会被混着用，但它们不是同一个东西：

- `channel`：对外暴露的独立调度或隔离单元
- `queue`：软件提交任务的顺序容器
- `stream`：工作负载视角的一路逻辑流量
- `context`：地址空间、权限、虚拟化语义对应的执行上下文

它们可能一一对应，也可能一对多或多对一。把这些对象混掉，会直接导致错误建模。例如某个 DMA 看似有 8 个 channel，但真正能并发的只是 2 套 data path；或者多个 queue 共享一个 context，于是 fault 和 completion 的归属语义就不一样。

## 多通道首先是在解决共享资源争用

多通道不是为了参数表更好看，而是因为 DMA 逐渐从“单任务搬运器”演化成“系统共享数据移动基础设施”。只要一个引擎要同时服务 display、camera、storage、network 或多个 AI stream，就必须回答这些问题：

- 不同流量如何互不拖死
- 谁能抢更高优先级
- 一个通道卡住时能否局部隔离
- completion 和 fault 如何准确归属

所以多通道同时是性能设计和隔离设计。没有它，noisy neighbor 很容易把全局带宽和 completion 路径一起拖垮。

## 虚拟化不是锦上添花，而是设备侧地址世界的延伸

只要 DMA 要面向多 VM、多租户或用户态直通设备，context 与 isolation 就从高级功能变成基础能力。你不再只关心“这笔搬运发没发出去”，还要关心：

- 这个 descriptor 属于哪个地址空间
- 这个 queue 的 doorbell 和 completion 应落到哪个软件实体
- fault 能否只杀死本 context，而不拖垮整个引擎
- outstanding 配额是否被某个租户独占

这类能力和 IOMMU/SMMU 直接耦合，但不等价。IOMMU 解决的是地址翻译与保护；DMA 内部的 context 管理解决的是“翻译好之后，这笔任务在引擎内部归谁、和谁隔离、用多少资源”。

## 隔离失效时会发生什么

隔离做不好，问题往往不是“性能略差”，而是系统行为直接失真：

- 一个通道的长尾 completion 拖住全局 slot 回收
- 某个租户把 outstanding 和带宽配额全部吃满
- fault 归属不清，软件无法判断该回收哪批 buffer
- doorbell 或 completion 共享路径被挤爆，导致看似无关的 stream 一起抖动

所以评估 DMA 的多通道与虚拟化能力时，不能只看“支持多少 channel”，还要看资源是否真正分离，还是只是接口上分离。

## 常见误解

常见误解：`channel 数量越多越强`。实际上如果 data path、completion path 或 outstanding table 没同步扩展，更多 channel 只是更多争用入口。

常见误解：`queue 多就等于隔离好`。实际上 queue 只是提交容器，不代表地址空间、fault 和资源配额都独立。

常见误解：`虚拟化只是软件层需求`。实际上只要设备面向多 context 工作，DMA 硬件内部就必须显式保存 context 状态。

## 一句话理解

当 DMA 从单任务执行器演化成共享基础设施时，多通道、context 管理和隔离能力就从“高级功能”变成了基本盘。

## 建模启示

这一页的关键是别把所有流量压成一个全局队列。至少要显式保留 `channel_id`、`context_id`、`quota` 和 `fault_owner` 这几类状态。

一个够用的数据结构是：

```text
DMAChannel {
  channel_id
  context_id
  queue_depth
  outstanding_quota
  priority
}
```

若只关心总吞吐，可以把多个 channel 合并成少量 traffic class；若关心公平性、虚拟化隔离或故障定位，`context_id` 和 `fault_owner` 不能省。
