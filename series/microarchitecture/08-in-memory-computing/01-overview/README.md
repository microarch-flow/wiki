# 问题、术语与分类

<span class="micro-legacy-anchor" id="01-overview"></span>


上级：[CIM Wiki](../README.md)
相关：[知识地图](../SUMMARY.md)

## 这页在回答什么问题

读 CIM 最容易先被论文名词带偏：有人把 HBM-PIM 叫 CIM，有人把 SRAM 阵列旁边加逻辑也叫 CIM，有人只谈 analog MVM 却忽略软件和系统。01 章的任务是先建立一套不会混乱的坐标系，再进入后面的器件、电路、架构、软件、workload 和产业章节。

## 本章先钉住两件事

第一件事是物理机制与术语口径。[跟着同一个点积走三条路](./cim-pim-nmc-taxonomy.md)，可以逐项核对乘法在哪里发生、谁保存部分和，最后对照文献使用的术语。分类依据是可核实的位置和路径，不是名称是否符合本文用词。

第二件事是两条正交主线。[两条正交主线](./two-axes-memory-and-paradigm.md) 把横轴定义为 memory technology，把纵轴定义为 compute paradigm。横轴回答“权重和计算依附在哪类 memory 物理对象上”，纵轴回答“乘加到底以 analog、digital 还是 mixed-signal 方式发生”。这两个问题不能互相替代。


<span class="micro-legacy-anchor" id="推荐阅读顺序"></span>

## 阅读顺序

1. [Memory Wall 与 Von Neumann Bottleneck](./problem-statement.md)
2. [同一个点积，挪到存储旁边或阵列里面怎么算？](./cim-pim-nmc-taxonomy.md)
3. [两条正交主线](./two-axes-memory-and-paradigm.md)
4. [早期 PIM 原型未规模采用与 AI 时代的新机会](./why-cim-now-and-why-not-before.md)
5. [CIM 整体分类体系](./taxonomy.md)
6. [学习路径与章节依赖关系](./learning-roadmap.md)

## 本章对后续章节的约束

后续每篇提到 CIM、PIM、NMC 时，都必须先问计算位置和物理参与度，而不是沿用论文或公司宣传的命名。阵列参与计算的 CIM 再用 memory technology 和 analog/digital/mixed-signal CIM 范式描述；独立 PIM/NMC 单元记录执行方式、局部存储与接口。

## 一句话理解

01 章不是背景介绍，而是整份 wiki 的坐标系：先把术语和两条主线固定住，后面才有资格比较路线、论文、产品和公司。
