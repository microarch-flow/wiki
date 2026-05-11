# IOMMU、SMMU 与 DMA 寻址

上级：[04 微架构与系统集成](./README.md)

相关：[DMA Wiki 首页](../../../DMA/wiki/README.md)、[缓存一致性、IOMMU 与地址空间](../../../DMA/wiki/02-fundamentals/consistency-cache-coherency.md)

## 这页在回答什么问题

为什么 DMA 看到的地址不一定是物理地址，以及这件事如何改变 BUS 上的事务理解。

## DMA 为什么需要地址翻译或隔离

如果 device 直接拿系统物理地址做 DMA，会很快遇到问题：

- 虚拟化下地址空间隔离不够
- 多进程或多租户安全性差
- buffer 管理和迁移不灵活

所以系统会在 DMA 发起路径上加入 IOMMU / SMMU 一类机制。

## 对 BUS 来说这意味着什么

DMA 请求不再只是：

`device -> interconnect -> memory`

而更像：

`device -> interconnect -> IOMMU/SMMU -> interconnect -> memory`

这会带来额外影响：

- 地址翻译延迟
- 额外 page walk / TLB 行为
- fault / permission error 返回路径
- backpressure 和 observability 复杂度上升

## 继续阅读

- 如果你在追 `DMA 任务链路是怎么被翻译层插入的`：看 [AXI 与 DMA 的系统接口](./axi-dma-system-interface.md)
- 如果你在追 `descriptor fetch 和 data move 谁先 fault`：看 [DMA Descriptor Fetch、Data Move 与 Writeback](./dma-descriptor-fetch-data-move-writeback.md)
- 如果你在追 `IOMMU fault 现场该怎么拆`：看 [IOMMU Fault 案例卡](../06-scenarios-case-studies/iommu-fault-case-card.md)
- 如果你在追 `fault 与 hang 的定位入口差别`：看 [Timeout、Fault 与 Hang 定位框架](../05-performance-debug/timeout-fault-hang-debug-framework.md)

## 最容易被忽略的点

- IOMMU fault 也是 bus-level debug 的一部分
- 地址翻译失败不等于 memory controller 出错
- DMA 性能问题可能先卡在 translation path

## 一句话理解

IOMMU/SMMU 把 DMA 从“直接访存”变成“受翻译、受保护、可虚拟化的总线主设备”，同时也把调试链条拉长了。
