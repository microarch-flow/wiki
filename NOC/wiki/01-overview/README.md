# 01 Overview

这一章先把 NoC 从“很多 router 连起来”的印象里拉出来，重建成一个系统问题。你在这里需要先回答四件事：

- 为什么 BUS 和小规模 crossbar 会在多 tile 系统里失效
- BUS、crossbar、NoC 三种互连到底在解决什么不同的问题
- topology、routing、flow control、QoS 为什么必须拆开看
- 以 deterministic NPU 为目标时，后续章节应该按什么顺序建立语言体系

## 本章入口

- [Problem Statement](./problem-statement.md)
- [Bus Vs NoC Vs Crossbar](./bus-vs-noc-vs-crossbar.md)
- [Taxonomy](./taxonomy.md)
- [Learning Roadmap](./learning-roadmap.md)

## 一句话总纲

NoC 的本质不是“片上连线变复杂了”，而是当系统进入 `多端点并发 + 长线 + 热点 + 可建模调度` 的阶段后，互连必须从共享事务骨架演化成分布式网络。
