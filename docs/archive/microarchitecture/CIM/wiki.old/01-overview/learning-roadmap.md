# 学习路线图

## 这张路线图解决什么问题

CIM 横跨器件、电路、架构、软件和产业。没有主线时，阅读很容易停留在名词堆积，最后既无法判断论文价值，也无法判断产品路线。

本页给出的路线图，目标是把知识逐步压实成判断能力。

## 建议主线

1. Memory wall 与数据搬运
2. CIM / PIM / Near-Memory 分类
3. 不同存储介质路线
4. 电路与 macro 原理
5. 架构与系统集成
6. 编译器、映射与 runtime
7. Workload 适配
8. 产业链与商业化判断

## 为什么按这个顺序

### 先从问题出发

如果不先理解 `memory wall` 和数据搬运，就很容易把 CIM 当成另一种“更省电的 MAC”，从而误判它真正的价值。

### 再看分类和介质

先分清 `CIM / PIM / Near-Memory`，再进入 `SRAM / DRAM / ReRAM / Flash` 等路线，才能避免把完全不同的技术混在一起比较。

### 然后才进入电路和系统

电路论文很容易一开始就把人带进细节，但如果不知道系统层最终想解决什么，就很难判断某个宏到底重要在哪里。

### 最后落到 workload 和商业化

只有当技术路线、系统映射和目标负载三者闭环后，商业判断才有意义。

## 四阶段推进方式

- `阶段 A`：建立概念地图
- `阶段 B`：理解电路和 macro
- `阶段 C`：上升到 chip 和 system
- `阶段 D`：形成产业判断能力

## 每个阶段的目标

### 阶段 A：建立概念地图

目标：

- 搞清楚 CIM 为什么出现
- 知道几条主路线各自解决什么问题
- 能区分 `macro-level` 和 `system-level` 价值

建议输出物：

- CIM taxonomy map
- CIM / PIM / Near-Memory 对比表
- 典型 workload 适配表

### 阶段 B：理解电路和 macro

目标：

- 能读懂常见 bitcell、bitline、ADC、SA 图
- 能看出宏设计的真实瓶颈在哪里
- 能解释精度、噪声和外围开销的关系

建议输出物：

- SRAM-CIM macro 结构图
- ReRAM crossbar MVM 笔记
- ADC 能耗 / 精度 trade-off 表

### 阶段 C：上升到 chip 和 system

目标：

- 能分析 tile、NoC、buffer、controller 如何组成系统
- 能判断数据流、partial sum 和 host 协同是否成立
- 能做初步性能和能耗拆解

建议输出物：

- chip block diagram
- GEMM / attention 映射例子
- 简化的 roofline 或 energy model

### 阶段 D：形成产业判断能力

目标：

- 能看懂公司、产品和论文的真实边界
- 能区分研究样片、工程样机和量产路线
- 能判断客户价值和供应链可行性

建议输出物：

- 公司路线图谱
- 商业化评估表
- 尽调问题清单

## 对应本 wiki 的推荐阅读顺序

1. [CIM 在解决什么问题](./problem-statement.md)
2. [CIM / PIM / Near-Memory 分类](./taxonomy.md)
3. `02-memory-technologies`
4. `04-circuit-macro`
5. `05-architecture-system`
6. `06-software-stack`
7. `07-workloads`
8. `08-industry`

## 后续可补充内容

- 不同阶段对应论文清单
- 不同阶段对应问题列表
- 不同阶段的输出物模板
