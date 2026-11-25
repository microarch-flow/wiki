---
search:
  exclude: true
---

# DRAM 行保留与预充策略（原入口）

本页已并入[DRAM 控制器为什么先服务后来排队的读取？](./command-scheduling-fr-fcfs.md)。原文各小节可以直接在新文中阅读。

<div markdown="1" data-storage-redirect="true">

- <span id="行缓冲策略保留预充与自适应选择"></span>[保留打开的行，还是尽早关行](./command-scheduling-fr-fcfs.md#page-policy)
- <span id="opencloseadaptive-page-policy-的权衡"></span>[open、close 和 adaptive 的取舍](./command-scheduling-fr-fcfs.md#page-policy)
- <span id="这页在回答什么问题"></span>[一次访问以后，行还要开着吗](./command-scheduling-fr-fcfs.md#page-policy)
- <span id="打开行的保留与关闭决策"></span>[何时作出保留或关闭的决定](./command-scheduling-fr-fcfs.md#打开行的保留与关闭决策)
- <span id="行驻留与后续请求"></span>[保留行怎样改变下一笔请求](./command-scheduling-fr-fcfs.md#行驻留与后续请求)
- <span id="观察到达时间"></span>[比较提前预充和继续等待的命令时刻](./command-scheduling-fr-fcfs.md#观察到达时间)
- <span id="自适应策略要看什么"></span>[控制器能看到哪些信息](./command-scheduling-fr-fcfs.md#自适应策略要看什么)
- <span id="策略与-auto-precharge-的区别"></span>[关行策略与器件的自动预充](./command-scheduling-fr-fcfs.md#策略与-auto-precharge-的区别)
- <span id="一句话理解"></span>[保留行和提前预充各在什么情况下有利](./command-scheduling-fr-fcfs.md#page-policy)
- <span id="建模启示"></span>[模型怎样记录实际的关行决策](./command-scheduling-fr-fcfs.md#model)

</div>
