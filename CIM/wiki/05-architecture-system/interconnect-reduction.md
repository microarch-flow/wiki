# 互联、归约与存储层次

## 为什么重要

当多个 macro 组成 tile 或 chip 后，互联与归约往往成为隐藏成本。

## 重点问题

- 宏之间通过 bus、crossbar 还是 NoC 连接
- partial sum 是本地归约还是全局归约
- DRAM / SRAM / scratchpad 的分工是什么
- host 接口是否会抵消阵列收益

## 可补充内容

- NoC 拓扑整理
- reduction 路径示意图
- memory hierarchy 对系统能效的影响
