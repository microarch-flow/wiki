# 01 概览与问题定义

本章先解决三个问题：

1. NoC 到底在解决什么问题
2. 学 NoC 时哪些概念最容易混淆
3. 面向 AI tile dataflow 的主学习路径是什么

## 本章入口

- [NoC 在解决什么问题](./problem-statement.md)
- [NoC 分类框架](./taxonomy.md)
- [学习路线图](./learning-roadmap.md)

## 一句话总纲

NoC 的本质不是“把模块连起来”，而是在有限面积、功耗、带宽、时序和软件可控性约束下，让 `tile / SRAM / DMA / HBM / control` 之间的数据交换可扩展、可预测、可建模。
