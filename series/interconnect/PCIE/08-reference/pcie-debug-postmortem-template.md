# PCIE 故障复盘模板

上级：[08 术语与检查清单](./README.md)

相关：[PCIE 调试检查清单](./pcie-debug-checklist.md)

## 故障现象

- 现象是什么：枚举失败、降速、DMA 不通、completion timeout、MSI-X 异常
- 首次出现时间和复现条件是什么
- 是否和特定平台、插槽、拓扑或 workload 强相关

## 影响范围

- 影响单设备、单机型还是整类平台
- 影响功能正确性、性能还是稳定性
- 是否存在数据损坏或隔离风险

## 路径定位

- 问题主要落在配置、链路、DMA、interrupt 还是 host memory 路径
- 是 read path 还是 write path 更异常
- 是否能定位到 root complex、switch、endpoint 或软件栈某一侧

## 关键证据

- link status / width / speed
- AER 和相关错误状态
- BAR、MSI-X、bus mastering、IOMMU 配置快照
- queue / completion / interrupt / timeout 统计

## 根因总结

- 根因属于事务语义、资源配置、链路质量、主机内存路径还是软件同步问题
- 哪个系统契约没有闭环

## 修复与预防

- 本次修复做了什么
- 需要补哪些检查清单、监控或压测场景
- 哪些相邻 wiki 页面应该补链接或补案例
