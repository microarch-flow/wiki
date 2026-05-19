# PCIE 一页版总览

上级：[08 术语与检查清单](./README.md)

## 一页抓住 PCIE

- `角色`：Root Complex、Switch、Endpoint
- `分层`：Transaction、Data Link、Physical
- `管理面`：config space、BAR、capability、enumeration
- `数据面`：MMIO control、DMA read/write、completion
- `通知面`：MSI / MSI-X、polling、status memory
- `隔离面`：IOMMU、virtualization、address translation
- `调试面`：AER、link status、counters、timeout / UR / CA

## 最常见主线

1. 主机枚举设备并分配 BAR
2. 驱动通过 MMIO 配置 queue 和 doorbell
3. 设备通过 DMA 访问主机内存
4. 完成信息写回 host memory
5. 通过 MSI-X 或 polling 驱动软件推进

## 最容易混淆的三组词

- `PCIe completion` vs `software completion queue`
- `BAR address` vs `DMA address`
- `link bandwidth` vs `end-to-end throughput`

## 一句话理解

PCIE 的核心不是某个字段定义，而是它如何把 host、device、memory 和 software stack 组织成一个可运行的系统契约。
