# 07 术语与检查清单

前面六章是"学交通系统"，这一章是**工具箱**——不再讲原理，而是把学到的东西压成随时可用的速查卡、检查清单和复盘模板。就像驾校毕业后你需要的不是教材，而是仪表盘速查、保养清单和事故处理指南。

## 本章包含什么

- [BUS 一页版总览](./bus-one-page.md)
- [术语表](./glossary.md)
- [BUS 设计检查清单](./bus-design-checklist.md)
- [Master/Slave/Bridge 设计清单](./master-slave-bridge-checklists.md)
- [DDR/IOMMU/Debug 集成清单](./ddr-iommu-debug-checklists.md)
- [BUS 高频问题](./high-frequency-questions.md)
- [BUS 故障复盘模板](./bus-debug-postmortem-template.md)
- [互连方案评估模板](./interconnect-evaluation-template.md)
- [BUS 协议阅读模板](./protocol-reading-template.md)

## 本章主线

当你已经知道 BUS 的基本概念后，第 07 章帮助你把术语、设计检查、调试复盘和协议阅读统一到同一套语言里：Resource、Topology、Interaction、Capability，以及 request、response、completion、error、timeout、observability 这些可建模事件。

## 建模启示

参考章的价值不只是快速查阅，而是把 wiki 的分析框架固化成可复用工具。设计评审用 checklist，协议学习用 reading template，故障复盘用 postmortem template，系统对比用 evaluation template。它们都应落回同一组事件：`request_accept`、`decode_done`、`arbiter_grant`、`bridge_convert`、`response_return`、`completion_visible`、`fault_recorded`、`timeout_fire`、`resource_release`。

如果新的 BUS 问题无法被这些模板描述，应该优先检查模板缺口；如果能描述但无法观测，应该补 counter/trace；如果能观测但无法闭环，应该回到设计清单修正错误、timeout 或 resource release。
