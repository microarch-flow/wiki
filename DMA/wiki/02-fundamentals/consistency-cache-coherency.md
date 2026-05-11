# 缓存一致性、IOMMU 与地址空间

上级：[02 基础对象与传输语义](./README.md)

相关：[同步、一致性与常见错误](../04-programming-model/synchronization-errors.md)、[SoC 外设与 I/O DMA](../05-system-integration/soc-peripheral-io.md)

## 这页在回答什么问题

为什么很多 DMA 问题看起来像“搬运错误”，本质却是 cache、一致性、地址翻译或权限配置错误。

## Non-coherent DMA 的核心问题

如果 DMA 不与 CPU cache 自动保持一致，那么软件必须显式处理：

- buffer ownership 切换
- CPU 写入何时对 DMA 可见
- DMA 写回何时对 CPU 可见

否则 CPU 看到的可能不是 DMA 刚写入的数据。

更稳妥的理解不是背固定 recipe，而是先按方向分：

- `DMA_TO_DEVICE`：关键是让 CPU 之前写入的数据先对 DMA 可见
- `DMA_FROM_DEVICE`：关键是避免 CPU 继续读到旧缓存副本

具体要做 `clean / flush / invalidate` 的顺序和 API，通常依赖架构、cache 组织和 driver/runtime 所在软件栈，不适合写成所有平台都一样的死规则。

## Coherent DMA 也不是“什么都不用管”

cache coherent 只意味着一致性维护更自动，不意味着：

- 没有地址翻译成本
- 没有同步时序问题
- 没有带宽竞争

## IOMMU / SMMU 在改变什么

它们通常负责：

- I/O 虚拟地址到物理地址映射
- 隔离不同 device / VM 的可访问范围
- scatter-gather 映射组织
- page fault 或权限异常处理

所以 DMA 不只是“会搬”，还带着一层安全与虚拟化语义。

## 一个关键判断

只要系统里出现下面任一条件，就不能把 DMA 当作“裸物理地址搬运”看：

- 用户态 buffer 直达 device
- 多 VM 共享设备
- 高端 SoC 带完整 IOMMU
- 设备支持虚拟化或 SR-IOV 类能力

## 一句话理解

DMA 看到的不只是地址和数据，它还必须服从 cache、一致性、翻译和隔离这些系统级约束。
