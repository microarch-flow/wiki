# 行缓冲策略：保留、预充与自适应选择

上级：<span id="opencloseadaptive-page-policy-的权衡"></span>[DRAM 控制器与请求调度](./README.md)

相关：[命令调度与 FR-FCFS](./command-scheduling-fr-fcfs.md) · [Row buffer 与行状态](../03-dram/foundations/1t1c-cell-destructive-read.md#row-state) · [SRAM bank 与 DRAM 行状态](../01-memory-hierarchy/02-access-paths/sram-vs-dram-access-pattern.md)

## 这页在回答什么问题

Open、close、adaptive page policy 讨论的是：一次列访问后，控制器应保留当前行，还是在合法时机关闭它？这里的 page 是 DRAM 的打开行，不是操作系统的虚拟内存页。

## Open、close、adaptive page policy 的权衡 {#打开行的保留与关闭决策}

### 行驻留与后续请求

- **Open-page** 倾向保留行；后续访问同一行时可能省去 ACT。需要访问同一 bank 的另一行时，仍要先满足关行条件。
- **Close-page** 倾向尽早安排预充；若在下一笔异行请求到来前完成部分或全部预充，可以隐藏相应等待。若后续又访问原行，则需要重新激活。
- **Adaptive page policy** 根据队列、近期行为或其他可用信息作选择。具体预测范围与误判代价由实现决定，不保证始终优于固定策略。

保留行只提供复用机会；列命令、共享 DQ 和上游队列仍可能阻塞后续请求。对应机制见 [DRAM 行状态](../03-dram/foundations/1t1c-cell-destructive-read.md#row-state)。

### 观察到达时间

沿用[地址映射 X](./address-mapping-channel-rank-bank-row-col.md)：先前访问 line 0—7 后，bank 0 的 row 0 处于打开状态。下面比较两种可能的下一笔请求：line 1 仍在 row 0，line 32 则在同一 bank 的 row 1。这是不同于调度例子的到达时序。

下面是**教学模型**。当前打开行最早在周期 12 可以 PRE；显式 PRE 到下次 ACT 为 4 CK，ACT 到外部 RD 为 3 CK。假设 AL=0，所有其他时序、命令和 DQ 约束均满足，新请求于周期 20 到达。同一时刻的动作按所述顺序处理；数值不是器件规格。

| 新请求的目标 | 提前关行：PRE 12，bank 于 16 可开新行 | 保留原行至请求到达 |
| --- | --- | --- |
| line 1：原来的行 | ACT 20，RD 最早 23 | RD 最早 20 |
| line 32：同一 bank 的另一行 | ACT 20，RD 最早 23 | PRE 20，ACT 最早 24，RD 最早 27 |

这里比较的是 **RD 命令时刻**，不是首数据或完整响应时刻。若异行请求在周期 12 之前已到，且控制器两种策略都在周期 12 发 PRE，则提前关行没有产生额外时间收益。若请求在 12—16 之间到达，提前 PRE 只可能隐藏部分预充等待。

### 自适应策略要看什么？

一个简单策略可以观察当前队列中是否还有同一行的请求，再结合空闲时长决定是否关闭。它只能看到已到达的信息；未来同一行请求可能恰好在关行后出现。比较策略时应保持地址映射、到达时间和队列容量一致，同时观察行命中、关行次数和请求延迟，而不是只比较命中率。

## 策略与 auto-precharge 的区别

Open/close 描述控制器**何时希望关闭**。Auto-precharge 是某些器件支持的命令机制：控制器在列命令中请求器件按规定安排内部预充；它不是一条已经在该时刻发出的外部 PRE。内部触发及下次 ACT 仍受该模式的时序约束。

[AMD UltraScale Memory IP 文档](https://docs.amd.com/r/en-US/pg150-ultrascale-memory-ip/Autoprecharge?contentId=dxL76eC_fD3vaafa125usw)描述了一个默认 open-page、可逐事务请求 auto-precharge 的实现。其他控制器可能作不同选择。显式 PRE 的共同下界见[时序参数](../03-dram/protocols/timing-parameters-trcd-trp-tras.md#ddr4-同-bank-显式-pre-的完整下界)。

## 一句话理解

保留行可以等待复用；提前预充可能利用空闲时间准备换行。收益由后续请求及合法时刻共同决定。

## 建模启示

让策略影响实际关行决策或自动预充事件，而不是只改一个固定命中率。区分策略要求、PRE 合法时刻、预充完成和新 ACT 可发时刻；比较时记录每种策略的初始状态和请求到达时间。
