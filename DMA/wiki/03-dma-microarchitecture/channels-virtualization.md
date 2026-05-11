# 多通道、虚拟化与隔离

上级：[03 DMA 引擎微架构](./README.md)

相关：[缓存一致性、IOMMU 与地址空间](../02-fundamentals/consistency-cache-coherency.md)、[DMA IP 评估清单](../08-industry-ip/dma-ip-checklist.md)

## 这页在回答什么问题

为什么现代 DMA 往往不是单通道裸引擎，而是多队列、多租户、可隔离的基础设施。

## 多通道不只是为了“并发更多”

这里几个词最好先分开：

- `channel`：DMA 对外暴露的一个独立调度/隔离单元
- `queue`：提交任务的顺序容器
- `stream`：软件或 workload 视角的一路逻辑流量
- `context`：地址空间、权限或虚拟化隔离语义对应的上下文

它们可以一一对应，也可以多对一或一对多，不一定是同一个东西。

多通道通常同时服务：

- 不同外设或 stream
- 不同优先级业务
- 不同安全域或虚拟机

所以它既是性能设计，也是隔离设计。

## 虚拟化能力通常体现在哪

- 每通道独立队列
- per-context 地址空间
- doorbell / completion 分离
- fault isolation
- 带宽或 outstanding 配额

## 隔离失效会带来什么问题

- 一个 noisy neighbor 抢占大部分带宽
- 某通道卡死拖累全局 completion
- 安全域越界访问

## 一句话理解

当 DMA 从单任务搬运器演化成系统共享资源时，多通道、虚拟化和隔离就从“高级功能”变成了基础能力。
