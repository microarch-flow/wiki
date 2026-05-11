# IOMMU Fault 案例卡

上级：[06 典型系统与案例](./README.md)

相关：[IOMMU、SMMU 与 DMA 寻址](../04-microarchitecture-integration/iommu-smmu-dma-addressing.md)、[AXI Response 与错误路径](../03-on-chip-protocol-families/axi-response-error-path.md)

## 现象

设备 DMA 发起后出现 translation fault / permission fault，任务失败或反复重试。

## 典型根因方向

- IOVA 到物理地址映射缺失
- 权限位不对
- scatter-gather 某一段没有正确映射
- queue / descriptor 用的地址空间和 data buffer 用的地址空间不一致

## 排查顺序

1. 分清 fault 发生在 descriptor fetch 还是 data move
2. 确认 fault 的地址到底是谁发出的
3. 对照 IOMMU 页表和 buffer 生命周期
4. 看 fault 后 response / retry / interrupt 路径是否完整

## 这类问题为什么难

因为表面现象像“DMA 坏了”或“memory 坏了”，但真正失败点在中间的翻译和权限层。

## 一句话理解

IOMMU fault 的关键不是只看 fault 本身，而是先弄清“是哪一类 DMA 子事务、在什么地址语义下失败了”。
