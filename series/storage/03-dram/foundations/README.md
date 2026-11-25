# DRAM 单元与阵列

上级：<span id="dram-基础"></span>[存储系统](../../README.md)

相关：[SRAM 器件与应用](../../02-sram/foundations/README.md) · [DRAM 命令与接口](../protocols/README.md) · [原有 RAM 阅读入口](../../reading-and-reference/01-reading/README.md)

## DRAM 基础：从单元到阵列 {#这页在回答什么问题}

“DRAM 基础”从单元出发，解释一笔访问为什么要经过感测、行选择和列选择，以及多个请求为什么会争用阵列和接口。这里以常见的 1T1C DRAM 为主；具体接口和产品可以采用不同组织。

## DRAM 单元、行缓冲与刷新

1T1C 单元用电容保存电荷。读取会扰动电容状态，因此感测后需要恢复；电荷随时间泄漏，还需要按照器件要求刷新。行缓冲和 bank 将这些操作组织起来，channel、rank 和 chip 则描述从系统接口到器件的连接。

本组解释器件和阵列。命令与参数见[DRAM 命令与接口](../protocols/README.md)；调度、地址映射和请求队列见 [DRAM 控制器](../../04-dram-controller/README.md)。系统访问时间还包括队列、总线和其他竞争，不能只由单元操作推断。

## 阅读顺序

1. [只读几个字节，DRAM 为什么先打开一整行？](./1t1c-cell-destructive-read.md)
2. [Bank 与并行性](./bank-organization-parallelism.md)
3. [Channel、rank 与 chip](./channel-rank-chip-hierarchy.md)
4. [Bank group、prefetch 与 burst](./bank-group-prefetch-burst.md)
5. [刷新机制与代价](./refresh-the-fundamental-cost.md)
6. [DRAM 可靠性与错误保护](./dram-reliability-retention-rowhammer-ecc.md)
7. [DRAM 工艺与堆叠](./dram-process-stacking-trends.md)

第一篇跟着同一次读取，从一颗电容走到行缓冲和数据引脚。想查某一步，可以直接看[电荷共享](./1t1c-cell-destructive-read.md#charge-sharing)、[列选择](./1t1c-cell-destructive-read.md#column-select)或[行命中与行冲突](./1t1c-cell-destructive-read.md#row-state)。研究数据保持时，可接着读[刷新机制](./refresh-the-fundamental-cost.md)和[错误保护](./dram-reliability-retention-rowhammer-ecc.md)。要理解接口传输，可从 [prefetch 与 burst](./bank-group-prefetch-burst.md)转到[命令与接口导读](../protocols/README.md)。

## 一句话理解

从电荷保存到共享接口，每一层都有不同的状态、并行范围和约束。

## 建模启示

按问题选择抽象：研究行命中时保留 bank 的打开行和可用时间；研究刷新时增加覆盖范围、期限与占用；研究可靠性时再加入错误粒度和处理机制。具体容量、组织与参数应来自目标器件。
