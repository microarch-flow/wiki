# PCIE 设计检查清单

上级：[08 术语与检查清单](./README.md)

相关：[PCIE 调试检查清单](./pcie-debug-checklist.md)、[IOMMU、地址翻译与设备隔离](../03-configuration-enumeration-addressing/iommu-address-translation-device-isolation.md)

## 这页在回答什么问题

做 endpoint、板卡、平台集成或 host-device 软件接口设计时，哪些问题应该在评审阶段就提前问清楚。

## 角色与拓扑

- 设备处在什么拓扑位置：直连 root complex 还是挂在 switch 下
- 是否需要考虑多功能、虚拟化、P2P 或热插拔
- 是否明确了和主机平台的协同假设

## 配置与资源

- config space 和 capability 是否完整、边界清晰
- BAR 数量、大小、用途是否明确
- BAR 中哪些是控制面，哪些是状态或窗口资源
- 枚举后必须使能的能力是否列清楚

## 数据路径

- 队列、descriptor、doorbell 和 completion 模型是否定义清楚
- DMA read 和 DMA write 的主路径是否分别分析过
- outstanding、包粒度、batched submit 是否有基本策略
- host memory buffer 生命周期和可见性是否闭环

## 中断与完成

- MSI 或 MSI-X 使用模型是否明确
- completion record、status bit、interrupt 三者关系是否说清
- 中断合并、轮询和低延迟路径是否有明确取舍

## 地址翻译与隔离

- 是否依赖 IOMMU，以及依赖方式是否清晰
- DMA 地址空间、host 物理地址和软件地址视角是否区分清楚
- 多租户、虚拟化或不可信设备场景下的隔离边界是否定义清楚

## 可观测性与调试

- 是否预留了链路状态、错误、队列和 completion 的观测点
- 性能分析时能否区分链路瓶颈、host memory 瓶颈和软件提交瓶颈
- 错误发生时，能否快速回看 AER、链路状态和 DMA 活动

## 一句话理解

PCIE 设计评审最怕把“能枚举”“能发包”“能 DMA”“能通知”“能隔离”当成同一件事，它们必须分别闭环。
