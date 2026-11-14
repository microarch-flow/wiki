# DRAM 组织：channel、rank、chip 与 bank

上级：<span id="channelrankchip从引脚到-cell-的完整物理层级"></span>[DRAM 单元与阵列](./README.md)

相关：[Bank 与并行性](./bank-organization-parallelism.md) · [Bank group 与 burst](./bank-group-prefetch-burst.md)

## 这页在回答什么问题

地址范围、器件容量与数据位宽如何对应？channel、rank 和 chip 描述不同层次的连接，不应把一个 rank 想成位于单个 chip 之内。

## 接口资源与器件层次

### Channel

Channel 是一组受控制的外部接口资源。具体命令、地址、数据线和可独立调度范围依接口代际与系统实现而定。

### Rank

在常见 DIMM 组织中，一个 rank 是一起响应选择、共同提供数据位宽的一组芯片。不同 rank 可共享 channel 的部分信号；能否交错及切换代价依接口和控制器而定。

### Chip

Chip 是 DRAM 器件；标称容量和外部组织如 x8、x16 分别说明每颗容量和数据位宽。chip 内有 bank、行、列等结构；多颗器件并行组成更宽的数据接口。

### 完整层级

一次映射可描述为：channel 选择接口，rank 选择协同工作的芯片组，chip 内再选择 bank group、bank、row 和 column。具体映射可能交错，且接口不一定都有相同的 rank 或 bank group 概念。

### 典型数量级

假设一颗 **8 Gibit、x8** 器件有 16 bank，每 bank 有 65,536 行，每行 1,024 个 x8 列位置：`16 × 65,536 × 1,024 × 8 bit = 8 Gibit = 1 GiB`。这只是自洽的教学组织，不是某产品布局。

八颗 x8 芯片组成 64-bit 数据 rank，总容量为 8 GiB；同一行在每颗芯片占 1 KiB，八颗合计 8 KiB。一次 BL8 的 rank 数据量是 `64 bit × 8 / 8 = 64 B`。此例不含 ECC 芯片、模块寄存器或额外开销。

### 怎样用这张层级表

先核对器件密度与 x 组织，再核对 rank 使用多少颗芯片、系统有多少 rank/channel。burst 大小按实际数据位宽和传输次数计算，不应再次乘芯片数。

## 一句话理解

Rank 内多颗 chip 并行提供位宽；bank 和行列状态位于各器件内部。

## 建模启示

容量、行大小、事务大小和带宽必须使用同一映射及单位。记录共享命令与 DQ 的范围，避免把 rank 或 bank 数直接当作独立 channel 数。
