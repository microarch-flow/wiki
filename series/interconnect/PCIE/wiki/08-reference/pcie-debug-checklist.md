# PCIE 调试检查清单

上级：[08 术语与检查清单](./README.md)

## 链路与拓扑

- 链路是否成功训练到预期速率和宽度
- 设备是否处在预期的 root complex / switch 拓扑下
- 是否存在降速、掉 lane 或不稳定重训练

## 枚举与配置

- 配置空间是否可访问
- BAR 是否正确分配并使能
- bus mastering、MSI-X、相关 capability 是否已闭环配置

## DMA 与地址

- DMA mapping 是否建立正确
- IOMMU 是否放通且域配置正确
- queue / descriptor / buffer 生命周期是否稳定

## 通知与完成

- doorbell 是否真的送达设备
- completion record 是否对 host 可见
- MSI-X 或 polling 是否和完成状态匹配

## 性能与错误

- read 还是 write 在主导瓶颈
- outstanding、MPS、MRRS 是否合理
- AER、UR、CA、timeout 是否给出更明确方向
