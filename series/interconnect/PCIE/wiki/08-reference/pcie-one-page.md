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

- `PCIe Completion` vs `software completion queue`：前者是 non-posted 请求的返回 TLP；后者是保存完成记录的队列，单个命令的状态在 completion queue entry（CQE）中。写 CQE 可用 posted Memory Write，无相应事务 Completion；软件可轮询有效 CQE，不一定需要 MSI-X。
- `BAR address` vs `DMA address`：BAR 描述设备的目标资源窗口，主机通过 MMIO 访问是常见例子。DMA 地址是平台为发起设备映射目标资源所给的地址；目标可以是主机 buffer，也可以是在平台和拓扑允许时的对端设备 BAR 资源。窗口地址与请求者所用地址及翻译路径不能假定相同，见 [P2P 与拓扑约束](../07-advanced-topics/p2p-switch-topology-constraints.md)。
- `link bandwidth` vs `end-to-end throughput`：前者按指定链路、方向和时间窗计字节，后者按应用或 DMA 在同一窗口实际交付的有效字节计；协议开销、排队和其他路径资源使两者不同。

## 一句话理解

PCIE 的核心不是某个字段定义，而是它如何把 host、device、memory 和 software stack 组织成一个可运行的系统契约。
