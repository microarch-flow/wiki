---
search:
  exclude: true
---

# DRAM 时序参数（原入口）

本页已并入[同一个 DRAM bank 连读三次，为什么等待时间不同？](./commands-act-rd-wr-pre.md)。原文各小节可直接在新文中阅读。

<div markdown="1" data-storage-redirect="true">

- <span id="命令时序对应的物理等待"></span>[哪些动作之间必须等待](./commands-act-rd-wr-pre.md#命令时序对应的物理等待)
- <span id="dram-时序从命令采样到读写恢复"></span>[从命令采样到读写恢复](./commands-act-rd-wr-pre.md#dram-时序从命令采样到读写恢复)
- <span id="关键-timing-参数trcdtrptrastcl-的物理来源"></span>[tRCD、tRP、tRAS 与 CL 约束哪些步骤](./commands-act-rd-wr-pre.md#关键-timing-参数trcdtrptrastcl-的物理来源)
- <span id="这页在回答什么问题"></span>[从同一个 bank 的三笔读取开始](./commands-act-rd-wr-pre.md#这页在回答什么问题)
- <span id="开行列访问与首数据"></span>[从 ACT、RD 到第一拍数据](./commands-act-rd-wr-pre.md#开行列访问与首数据)
- <span id="行保持与预充"></span>[最早何时可以关行、再开下一行](./commands-act-rd-wr-pre.md#行保持与预充)
- <span id="写恢复与参数适用条件"></span>[从写数据的哪个时刻计算写恢复](./commands-act-rd-wr-pre.md#写恢复与参数适用条件)
- <span id="ddr4-同-bank-显式-pre-的完整下界"></span>[DDR4 显式 PRE 的三类下界](./commands-act-rd-wr-pre.md#ddr4-同-bank-显式-pre-的完整下界)
- <span id="一句话理解"></span>[怎样读一条命令时间线](./commands-act-rd-wr-pre.md#一句话理解)
- <span id="建模启示"></span>[怎样把时序约束放进模型](./commands-act-rd-wr-pre.md#建模启示)

</div>
