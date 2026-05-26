# 06 AI NOC Specifics

上级：[NOC Wiki](../README.md)

相关：[System Integration](../05-system-integration/README.md)、[Evaluation Methodology](../07-evaluation-methodology/README.md)

## 这页在回答什么问题

这一章回答：在已经掌握 `router`、`topology`、`routing` 和 `system integration` 之后，AI/NPU 场景到底新增了哪些真正值得单独讨论的 NoC 问题。

前五章建立的是通用语言。这一章开始讨论 AI 专属约束：

- tile 不是抽象 endpoint，而是带本地 SRAM、compute pipeline 和阶段化数据流的端点
- 关键流量不一定是 point-to-point，而可能是 broadcast、reduce、all-to-all、memory response
- 编译器、placement、static scheduling 会深度参与路径设计
- 某些 workload 更像 bulk throughput 问题，某些更像 response-latency 问题
- 多 die / chiplet 会把“片上网络”扩展成层次化 fabric

## 这一章的主线

可以把 AI NoC 的特殊性压成五个问题：

- 为什么 AI NoC 不等于 CPU coherent NoC 的缩小版
- tile、local SRAM、DMA、HBM 怎样共同定义网络需求
- 哪些 collective 流量值得硬件化支持
- deterministic/static scheduling 能换来什么，又会失去什么
- GEMM、prefill、decode、MoE 各自在逼问 NoC 什么能力

## 为什么这章必须在 system integration 之后

如果不先建立 `NI`、`DMA`、`address map`、`memory system` 这些边界，这一章会退化成“工作负载故事会”。AI NoC 的价值不在于列举模型名字，而在于把 workload 压力翻译成：

- topology 压力
- response path 压力
- collective 支持需求
- compiler/runtime 协同需求

## 这章的阅读顺序

建议顺序是：

1. `why-ai-noc-is-different`
2. `tile-architecture-and-noc`
3. `deterministic-noc-and-static-scheduling`
4. `memory-centric-noc`
5. collective 相关三篇
6. `chiplet-and-die-to-die-interconnect`
7. 四篇 workload 页面
8. `compiler-noc-co-design`

## 读完这章后应该得到什么

读完后，你应该能回答：

- 为什么 GEMM 常常更看重 broadcast / forwarding / reduce
- 为什么 decode 更看重 response isolation 和 memory placement
- 为什么 MoE 会把 routing 和 fairness 问题逼出来
- 为什么 static scheduling 往往比 fully adaptive 更符合 deterministic NPU
- 为什么 chiplet 会把 NoC 问题变成层次化通信问题

## 一句话理解

AI NoC 的特殊性，不在于“流量更大”这么简单，而在于 workload 结构、local memory、compiler 和系统层次共同改变了网络该优化什么。

## 建模启示

这一章对应的模型，不能再只停留在随机 packet 层面，而要开始显式表示：

- tile / memory endpoint 角色
- collective pattern
- static schedule 与 route plan
- workload phase
- cross-die hierarchy

如果模型还无法区分：

- bulk-throughput phase
- response-sensitive phase
- collective-heavy phase
- dynamic hotspot phase

那么它还不够用来分析 AI NoC。
