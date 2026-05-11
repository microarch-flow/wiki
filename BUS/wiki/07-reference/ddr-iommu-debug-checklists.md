# DDR/IOMMU/Debug 集成清单

上级：[07 术语与检查清单](./README.md)

相关：[AXI 到 DDR Controller 的路径](../04-microarchitecture-integration/axi-to-ddr-controller-path.md)、[IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)、[Debug Path 与 System Access](../04-microarchitecture-integration/debug-path-system-access.md)

## DDR / Memory Controller

- AXI 请求粒度是否和 controller/DDR 粒度匹配
- read/write combine 是否可能拉高关键读延迟
- return path 是否会被其他 master 共享阻塞
- row locality 差时系统是否仍能接受尾延迟
- timeout 触发点是否能区分 controller 慢还是 fabric 堵

## IOMMU / SMMU

- descriptor 和 data buffer 是否都走了正确的地址空间
- fault 信息是否足以定位到具体子事务
- permission / mapping 生命周期是否和 buffer 生命周期一致
- translation miss / page walk 开销是否在性能预算内
- fault 后 device、driver、interrupt 路径如何收尾

## Debug

- debug master 的地址访问范围是否明确定义
- boot / reset / low-power 状态下 debug path 是否可用
- debug 访问是否可能破坏正常软件时序
- debug 读写失败时有没有独立错误反馈
- 关键故障时能否通过 debug 看到 FIFO、state、fault 寄存器

## 一句话理解

DDR、IOMMU、debug 都不是“挂上去就行”的附件，而是最容易决定系统可用性和可调试性的三组集成点。
