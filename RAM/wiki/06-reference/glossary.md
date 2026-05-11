# 术语表

上级：[06 术语与速查](./README.md)

## SRAM

Static RAM。通常用 6T 单元实现，不需要刷新，常用于 cache 和片上局部存储。

## DRAM

Dynamic RAM。通常用 1T1C 单元实现，需要刷新，常用于大容量主存和高带宽外部内存。

## DDR

有两层常见含义：

- 狭义：`Double Data Rate`，每个时钟周期在上升沿和下降沿各传一次数据
- 广义：`DDR SDRAM` 这条 JEDEC 主存产品家族路线

## MT/s

Mega Transfers per second。表示每秒发生多少百万次传输，常用于表述 DDR 接口速率。

## ACT

Activate。打开某个 DRAM row，并将其内容感测到 row buffer。

## PRE

Precharge。关闭当前行并恢复位线状态，为下一次 activate 做准备。

## Row Buffer

行缓冲。可理解为 bank 当前已打开的一行的工作副本。

## Row Hit

请求命中当前已打开行，因此无需重新 activate，延迟较低。

## Row Miss

目标 bank 当前没有打开任何 row，因此通常需要 `ACT -> READ/WRITE`。

## Row Conflict

目标 bank 当前打开的是别的 row，因此通常需要 `PRE -> ACT -> READ/WRITE`。

## Row Locality

多个请求持续复用同一 bank 中已打开 row 的能力，是 DRAM 实际性能分析里的核心概念。

## Page Policy

内存控制器决定一次访问后是否保留当前打开行的策略。

## Open-page

倾向保留当前打开 row，期待后续继续命中。

## Close-page

倾向尽快关闭当前 row，减少未来不确定访问的冲突成本。

## Channel

内存控制器与 DRAM 间的一条独立通道，是扩展带宽的重要资源。

## Rank

共享通道一部分资源的物理组织单位，常用于容量扩展。

## Bank

DRAM 内部的并行存储子阵列，是控制器调度和并行度管理的关键资源。

## Prefetch

DRAM 内部一次先准备更宽数据块，再由外部 I/O 分多拍送出的桥接机制；这里不是 CPU 那种猜测式预取。

## Burst

一次 `READ/WRITE` 后，外部总线连续传出的多个 data beat。

## Bank Group

把多个 bank 再组织成更高一层的组；同组访问和跨组访问可能受不同的时序约束。

## REF / Refresh

为抵消 DRAM 电容漏电而周期性执行的数据保持操作，会占用阵列资源。

## LPDDR

Low Power DDR。面向低功耗系统的 DRAM 路线。

## GDDR

Graphics DDR。面向图形和独立 GPU 的高带宽板级 DRAM 路线。

## HBM

High Bandwidth Memory。HBM stack 内部通常是 3D 堆叠；系统级上常通过 2.5D 先进封装与计算 die 集成，用来获得超宽近距互连。

## TSV

Through-Silicon Via。穿硅通孔，用于 die 垂直互连，是 HBM 堆叠的重要基础结构。

## 2.5D

通常指多个 die 并排放在中介层上，通过高密度短距互连连接。

## 3D

通常指 die 在垂直方向直接堆叠形成更高集成密度的互连结构。

## Interposer

中介层。常见于 2.5D 集成，用来在多个 die 之间提供高密度短距互连。

## Base Die / Logic Die

HBM stack 底部承接信号、电源分配和部分控制逻辑的 die。

## pJ/bit

每传输 1 bit 数据大约消耗多少能量，常用来比较 I/O 能效。

## Scratchpad

由软件或编译器更显式管理的片上局部存储，不完全等同于自动替换的 cache。

## QoS

Quality of Service。控制器在共享内存系统里为吞吐、延迟和公平性做的服务质量约束。
