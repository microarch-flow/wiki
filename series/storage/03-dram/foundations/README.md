# DRAM 单元与阵列

上级：<span id="dram-基础"></span>[存储系统](../../README.md)

相关：[SRAM 器件与应用](../../02-sram/foundations/README.md) · [DRAM 命令与接口](../protocols/README.md) · [原有 RAM 阅读入口](../../reading-and-reference/01-reading/README.md)

## DRAM 基础：从单元到阵列 {#这页在回答什么问题}

“DRAM 基础”从单元出发，解释一笔访问为什么要经过感测、行选择和列选择，以及多个请求为什么会争用阵列和接口。这里以常见的 1T1C DRAM 为主；具体接口和产品可以采用不同组织。

## DRAM 单元、行缓冲与刷新

1T1C 单元用电容保存电荷。读取会扰动电容状态，因此感测后需要恢复；电荷随时间泄漏，还需要按照器件要求刷新。行缓冲和 bank 将这些操作组织起来，channel、rank 和 chip 则描述从系统接口到器件的连接。

本组解释器件和阵列。命令与参数见[DRAM 命令与接口](../protocols/README.md)；调度、地址映射和请求队列见 [DRAM 控制器](../../04-dram-controller/README.md)。系统访问时间还包括队列、总线和其他竞争，不能只由单元操作推断。

## 阅读顺序

1. [1T1C 单元与读出恢复](./1t1c-cell-destructive-read.md)
2. [行列解码与读出放大](./row-column-decode-sense-amplify.md)
3. [Row buffer 与行状态](./row-buffer-as-cache.md)
4. [Bank 与并行性](./bank-organization-parallelism.md)
5. [Channel、rank 与 chip](./channel-rank-chip-hierarchy.md)
6. [Bank group、prefetch 与 burst](./bank-group-prefetch-burst.md)
7. [刷新机制与代价](./refresh-the-fundamental-cost.md)
8. [DRAM 可靠性与错误保护](./dram-reliability-retention-rowhammer-ecc.md)
9. [DRAM 工艺与堆叠](./dram-process-stacking-trends.md)

若已了解阵列，只想查可靠性，可以从第 7、8 篇开始。想理解命令和接口，可从第 6 篇转到[命令与接口导读](../protocols/README.md)。

## 一句话理解

从电荷保存到共享接口，每一层都有不同的状态、并行范围和约束。

## 建模启示

按问题选择抽象：研究行命中时保留 bank 的打开行和可用时间；研究刷新时增加覆盖范围、期限与占用；研究可靠性时再加入错误粒度和处理机制。具体容量、组织与参数应来自目标器件。
