# Row buffer 与 DRAM 行状态

上级：<span id="row-bufferdram-内部的小-cache"></span>[DRAM 单元与阵列](./README.md)

相关：[行列解码](./row-column-decode-sense-amplify.md) · [DRAM 控制器](../../04-dram-controller/README.md)

## 这页在回答什么问题

Row buffer 是打开行对应的感测与数据状态。“DRAM 内部的小 cache”可以帮助理解重用，但它不是具有通用 tag 查找和替换策略的普通 CPU cache。

## 打开行的工作副本

对同一 bank，一次请求可能遇到：

| 先前状态 | 新请求 | 常见命令路径 |
| --- | --- | --- |
| 目标行已打开 | 行命中 | 列命令 |
| bank 已预充 | 关闭行 | ACT，再发列命令 |
| 另一行打开 | 行冲突 | 满足约束后 PRE、ACT，再发列命令 |

命令路径以常见显式控制为例；auto-precharge 等模式的内部动作和外部命令不同。打开的行是否继续保留，取决于器件接口、控制器的 page policy 和后续调度，而不是自动按照 cache 替换算法处理。

相同其他条件下，行命中不需要为本次访问再发 PRE 和 ACT。但实际请求还可能等待队列、共享 DQ、方向切换或刷新，单笔行命中不保证一定比另一笔行冲突更快。[访问模式](../../01-memory-hierarchy/02-access-paths/sram-vs-dram-access-pattern.md)讨论系统观察边界。

## 一句话理解

打开行提供可重用的数据状态；其收益取决于访问顺序和共享资源。

## 建模启示

每个受建模的 bank 至少记录打开行、命令可用时间和关闭过程；行命中率应与排队时间和数据总线占用一起解释。
