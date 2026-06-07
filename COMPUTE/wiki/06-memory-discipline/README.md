# 06 · 存储 discipline:cache vs scratchpad

算完一拍,下一拍的数据从哪来?本章讲算力单元视角下的存储语义分歧:让硬件偷偷决定(cache,非确定),还是让软件显式决定(scratchpad,确定)。这是 COMPUTE↔RAM 的接口章——只讲"确定性对算力单元意味着什么",器件细节交给 RAM 域。

## 篇目

1. **[Cache vs Scratchpad:确定性延迟的设计分歧](./cache-vs-scratchpad.md)**
   cache 是 CPU 非确定性最大来源;scratchpad 把数据放置决策搬到软件→确定性;⚠️确定性是更简单的起点(CPU 主动加 cache 才弄成非确定);为什么 AI 适合 scratchpad(设计局部性而非赌局部性);Groq 全静态的硬件根因。

## 本章在主线上的位置

cache vs scratchpad 不改变[主线](../01-overview/compute-communication-ratio.md)比值的**大小**,而改变分母的**可预测性**:把"数据从哪来"从运行时硬件随机前移到编译期软件确定。这是主线第三类手段——**把分母变确定**。对把 data movement bytes 当可审计物理量的建模而言,确定的分母才能编译期精确求值。

## 与 RAM 域的接口

本章刻意不重写 RAM 的器件分析。强链接:
- [`RAM/.../scratchpad-vs-cache`](../../../RAM/wiki/03-sram-applications/scratchpad-vs-cache.md) — 同一块 SRAM 的器件/面积/bank 视角
- [`RAM/.../data-movement-first-principle`](../../../RAM/wiki/09-ai-chip-memory-architecture/data-movement-first-principle.md) — NPU 存储层次的 data-movement-first
- [`RAM/.../why-mc-is-the-real-bottleneck`](../../../RAM/wiki/06-memory-controller/why-mc-is-the-real-bottleneck.md) — MC 仲裁与非确定性来源

→ 把门、阵列、流水、存储拼成一个核、一片芯片?进入 [07 · 芯片顶层组织](../07-chip-organization/)。
