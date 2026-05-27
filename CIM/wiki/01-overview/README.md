# 01 Overview

上级：[CIM Wiki](../README.md)
相关：[知识地图](../SUMMARY.md)

## 这页在回答什么问题

读 CIM 最容易先被论文名词带偏：有人把 HBM-PIM 叫 CIM，有人把 SRAM 阵列旁边加逻辑也叫 CIM，有人只谈 analog MVM 却忽略软件和系统。01 章的任务是先建立一套不会混乱的坐标系，再进入后面的器件、电路、架构、软件、workload 和产业章节。

## 本章先钉住两件事

第一件事是术语边界。[CIM/PIM/NMC 的严格区分](./cim-pim-nmc-taxonomy.md) 是全 wiki 的术语锚点：CIM 只用于计算发生在 memory cell 内或紧邻 cell 的存储阵列路径中；PIM 用于 memory die 或 bank 内加入独立 compute unit；NMC 用于 compute 靠近 memory 但不在 memory die 上，例如 HBM base die、logic die、interposer 或 package-side compute。Samsung HBM-PIM 和 SK hynix AiM/AiMX 在本 wiki 中按公开产品语境归 PIM，不归 CIM；如果某方案的 compute 明确位于 HBM base die 而非 memory die，则按 NMC 边界案例处理。

第二件事是两条正交主线。[两条正交主线](./two-axes-memory-and-paradigm.md) 把横轴定义为 memory technology，把纵轴定义为 compute paradigm。横轴回答“权重和计算依附在哪类 memory 物理对象上”，纵轴回答“乘加到底以 analog、digital 还是 mixed-signal 方式发生”。这两个问题不能互相替代。

## 推荐阅读顺序

1. [Memory Wall 与 Von Neumann Bottleneck](./problem-statement.md)
2. [CIM/PIM/NMC 的严格区分](./cim-pim-nmc-taxonomy.md)
3. [两条正交主线](./two-axes-memory-and-paradigm.md)
4. [为什么 CIM 在 1990s 失败、在 2010s 重生](./why-cim-now-and-why-not-before.md)
5. [CIM 整体分类体系](./taxonomy.md)
6. [学习路径与章节依赖关系](./learning-roadmap.md)

## 本章对后续章节的约束

后续每篇提到 CIM、PIM、NMC 时，都必须先问计算位置和物理参与度，而不是沿用论文或公司宣传的命名。后续每篇提到 SRAM-CIM、ReRAM-CIM、DRAM-PIM、analog CIM、digital CIM、mixed-signal CIM 时，都必须能落回 memory technology 和 compute paradigm 两个坐标。

## 一句话理解

01 章不是背景介绍，而是整份 wiki 的坐标系：先把术语和两条主线固定住，后面才有资格比较路线、论文、产品和公司。
