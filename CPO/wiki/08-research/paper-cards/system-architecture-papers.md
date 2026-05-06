# 系统架构类论文卡片

上级：[论文卡片库](./README.md)

相关：[案例：系统动机型论文怎么读](../case-studies/system-motivation-paper.md)

## 这一类论文主要看什么

这一类论文通常回答：

- 为什么要从 pluggable 走向 NPO 或 CPO
- 在交换容量继续上升时，系统瓶颈究竟卡在哪里
- CPO 带来的收益是否真的足以覆盖复杂度代价

## 推荐优先收集的论文类型

### 类型 1：交换机带宽扩展与 I/O 瓶颈分析

记录重点：

- 目标系统是传统数据中心还是 AI 集群
- 电链路长度和功耗是如何建模的
- 前面板密度是否构成硬约束

### 类型 2：CPO 与 pluggable 的系统级比较

记录重点：

- 比较维度是带宽、功耗、可维护性还是 TCO
- 假设条件是否偏理想化

### 类型 3：网络拓扑与机柜级布线视角

记录重点：

- CPO 是否改变了整机或整柜互连组织方式
- 收益是局部链路收益，还是系统级收益

## 论文卡片槽位

### 卡片 A：`Co-packaged optics (CPO): status, challenges, and solutions`

- 标题：Co-packaged optics (CPO): status, challenges, and solutions
- 作者 / 单位：Min Tan、Jiang Xu 等，多家高校与研究机构联合
- 时间：2023
- 类型：综述 / Perspective
- 链接：https://link.springer.com/article/10.1007/s12200-022-00055-y
- 核心问题：为什么数据中心和 HPC 需要从 pluggable 走向 CPO
- 关键贡献：把 CPO 放到统一框架里讨论，覆盖系统架构、硅光、DSP、封装、接收前端、标准化等多个维度，适合作为全局入口
- 关键代价：它是综述，不是单点实验验证；读完后你会知道问题地图，但不会直接得到某一具体实现的最终答案
- 我最该记住的一句话：如果你还分不清 CPO 的问题空间，这篇综述最适合作为第一篇总入口

### 卡片 B：`In-Package Optical I/O: Bridging the Gap Between Moore's Law and Amdahl's Law in Modern Compute Systems`

- 标题：In-Package Optical I/O: Bridging the Gap Between Moore's Law and Amdahl's Law in Modern Compute Systems
- 作者 / 单位：Vladimir Stojanovic / Ayar Labs
- 时间：2024
- 类型：OFC 报告
- 链接：https://opg.optica.org/abstract.cfm?uri=OFC-2024-Tu2F.4
- 核心问题：为什么现代计算系统需要 in-package optical I/O，而不只是更强的电互连
- 关键贡献：明确把问题提升到系统扩展和分布式计算层面，强调低时延、高带宽密度和高 radix 对现代计算系统的意义
- 关键代价：这是面向方向判断的系统论述，不是完整量产闭环证明；更适合作为“为什么要做”的材料，而不是“已经大规模能做”的证据
- 我最该记住的一句话：CPO 或 in-package optical I/O 的驱动力，不只是链路优化，而是整体计算系统扩展性

### 卡片 C：怎么用这两篇做入门组合

- 先读 Tan 等 2023 综述，建立 CPO 问题地图
- 再读 Stojanovic 2024，把 CPO 放回现代分布式计算和 AI 系统扩展的语境
- 如果你读完仍然只在想“光模块怎么变”，说明系统层还没真正吃透
